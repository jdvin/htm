from htm import HTM
import pandas as pd
import time
from importlib import *
from htm.enums import PredictionType

#eventually merge with time method in htm to create a master timer where the unit of time can be selected
def time_method(func):
    def time_method_wrapper(*args, **kwargs):
        present = time.time()
        result = func(*args, **kwargs)
        took = round(time.time() - present)
        args[0].logger.info(f'HTM {func.__name__!r} method took {took} s')
        return result
    return time_method_wrapper

class Factory():
    '''
    Factory for spawning HTM instances.
    Will hold a collection of all spawned instances.
    '''

    def __init__(self, logger):
        self.logger = logger

        self.instances = []

    def create_htm_instance(self, config) -> HTM:
        '''
        Create new instance of HTM with parameter encoder
        and a given self.config.
        Adds the new instance to the factory instances
        and returns it.
        '''
        self.logger.info(f"Creating new HTM instance with parameters: {config}")
        
        config_path = 'htm.config.' + config
        config_dict = {}
        try:
            imported_config = import_module(config_path)
        except ImportError as e:
            raise ImportError(f"Could not import specified config {config}\n{e}")
        
        for parameter in [param for param in imported_config.__dict__ if param[0] != '_']:
            config = imported_config.__dict__[parameter]
        self.logger.info('--Imported config module: ' + config_path)
    
        new_htm = HTM(logger=self.logger,
                      config=config)

        self.instances.append(new_htm)
        return new_htm

    # should this take into account zeros as well as ones
    @staticmethod
    def sdr_percent_overlap(sdr1, sdr2):
        overlap_count = 0
        total_count = 0
        if len(sdr1) == len(sdr2):
            for i in range(len(sdr1)):
                if sdr1[i]:
                    total_count += 1
                    if sdr1[i] == sdr2[i]:
                        overlap_count += 1
        else:
            return("Shape Mismatch")
        if total_count > 0:
            return ((overlap_count / total_count) * 100)
        else:
            return 0
    
    @staticmethod
    def sdr_raw_overlap(sdr1, sdr2):
        count = 0
        for i in range(len(sdr1)):
            if sdr1[i] == sdr2[i]:
                count += 1
        
        return count / len(sdr1)


    def classify_sdr(self, instance, sdr):
        '''
        returns an 2D array for each previously encountered input
        [previously encountered input, percentage overlap with corresponding SDR]
        '''
        prediction_overlaps = []
        for input in instance.encoder_classifier:
            prediction_overlaps.append([input, self.sdr_percent_overlap(sdr, instance.encoder_classifier[input])])
        prediction_overlaps = sorted(prediction_overlaps, key = lambda prediction_overlap: prediction_overlap[1])
        return prediction_overlaps

    @time_method
    def get_prediction(self, prediction_type, steps, pattern_length, instance):
        '''
        
        returns a 3D array for each prediction
        [prediction step, previously encountered input, percentage overlap with corresponding SDR]
        '''
        
        predictions = []

        #get the next prediction
        if prediction_type == PredictionType.NEXT:
            prediction = instance.get_next_prediction()
            predictions.append(self.classify_sdr(instance, prediction))

        #get the accumulative predictions for steps ahead
        elif prediction_type == PredictionType.STEPS:
            sdr_predictions = instance.predict_n_steps(steps)
            for prediction in sdr_predictions:
                predictions.append(self.classify_sdr(instance, prediction))

        return predictions

    def get_instance_accuracy(self, instance, pattern_length, prediction_steps, predictions):
        '''
        I have no idea what this is doing
        '''
        
        #get the actual input values of the pattern components which we are trying to predict
        pattern = [instance.encoder.sample_classifier[i] 
                    for i in range((pattern_length-prediction_steps), pattern_length)]
        
        accuracy = [[],[]]
        for i in range(len(pattern)):
            #if the SDR prediction of the ith step in the future which overlaps highest with an existing SDR 
            #that is the correct pattern component: increase accuracy by 1
            if predictions[i][-1][1] != 0:
                accuracy[0].append(abs(predictions[i][-1][0] - pattern[i]))
                accuracy[1].append((1-accuracy[0][-1])*100)
            else:
                accuracy[0].append(1)
                accuracy[1].append(0) 
        return accuracy

    def performance_log(self, pattern_length, prediction_type, prediction_steps, prediction_threshold, instance):
        '''
        Check the performance of the instance against the next iteration of the pattern
        '''

        #iterate the generator into the pattern until the prediction makes up the rest of it
        [instance.update() for i in range(pattern_length - prediction_steps)]
        
        #get predictions for instance and log them
        predictions = self.get_prediction(prediction_type, prediction_steps, 
                                            pattern_length, instance)
        
        #get the accuracy through the magic function that doesnt make any fucking sense
        accuracy = self.get_instance_accuracy(instance, pattern_length, 
                                               prediction_steps, predictions)
        for i in range(len(predictions)):
            next(instance.element_generator)
            self.logger.info("---------------------------------------------------------------------------------------------------------")
            self.logger.info(f"Predictions for {i+1} time step(s) forward...")
            for prediction in predictions[i]:
                if prediction[1] > prediction_threshold:
                    self.logger.info(f"~{prediction[1]}% overlap with {prediction[0]}")
            self.logger.info(f">>For largest matched: Error = {accuracy[0][i]} | Accuracy = {accuracy[1][i]}")

        #get instance accuracy and log it
        #instance.new_pattern()
        return [accuracy, predictions]


    @time_method
    def train_instance(self, training_data, train_episodes, 
                        pattern_length, prediction_type, prediction_steps, 
                        prediction_threshold, instance):
        '''
        train <instance>, <train_episodes> times, on a pattern with length = <pattern_length>
        target <prediction_type> : PredictionType (NEXT, STEPS); <prediction_steps> : through the pattern;
        <prediction_threshold> : threshold for considered prediction.
        '''
        encoder_module = import_module('htm.encoder')
        encoder = getattr(encoder_module, instance.encoder_type)

        instance.encoder = encoder(input_size=instance.input_size, 
                               data_path='data/' + training_data,
                               logger=self.logger)
                               
        instance.element_generator = instance.encoder.get_sample(0)
        
        self.logger.info(f'Training starting with {train_episodes} episodes')
        current_episode = -1
        pattern_position = -1
        #pattern_length = pattern_length
        sdr_snapshots = []
        check_performance_flag = False
        while True:
            
            #iterate patern position and current episode by 1
            pattern_position += 1
            current_episode += 1
           
            self.logger.debug(f"Beginning Training Episode {current_episode+1}...")

            # Update all HTM instances in the factory
            instance.update()

            #for the first iteration of the pattern, load the instances encoder_classifer with the SDR corresponding to each input
            if current_episode < len(instance.encoder.sample_classifier):
                instance.encoder_classifier[instance.encoder.sample_classifier[current_episode]] = instance.sdr_snapshot()

            #if we are at the end of the pattern clear the buffer for a new pattern sequence
            if pattern_position == pattern_length-1:
                #instance.new_pattern()
                pattern_position = -1
                #if we have progressed another 10% through the training data, test the performance of the model
                if check_performance_flag:
                    self.performance_log(pattern_length, prediction_type, prediction_steps, prediction_threshold, instance)
                    check_performance_flag = False


            # Some debug 
            if (current_episode+1) % int(train_episodes / 10) == 0:
                self.logger.info(f'Training {int(100 * (current_episode+1) / train_episodes)}% complete.')
                check_performance_flag = True

            self.logger.debug(f"Training Episode {current_episode+1} Complete!")

            # Check for manual input to simulation
            if current_episode+1 >= train_episodes:
                self.logger.info('Training finished')
                break

            
            
