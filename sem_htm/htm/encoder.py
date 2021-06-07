import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical

class Encoder:
    '''
    Base class for encoders.
    Inherit from this when creating an encoder type.
    '''

    def __init__(self, input_size, data_path, logger):
        self.input_size = input_size
        self.data_path = data_path
        self.logger = logger
        self.sample_classifier = [] 
    
    def load_data(self):
        '''Read CSV file into pandas dataframe'''
        self.logger.debug('Reading data from CSV file: ' + self.data_path)
        self.df = pd.read_csv(self.data_path).drop('index', axis=1)
        return self.df

class ScalerEncoder(Encoder):
    def __init__(self, overlap=50, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_data()
        self.overlap = overlap

    def get_sample(self, index):
        self.sample_classifier = self.df.data.values
        sample = self.serialize_data(self.df.data.values)
        self.logger.debug(f'Serialized sample {index} ({len(sample)} elements)')

        # Feed the data continuosly until training stops
        # FOOD FOR THOUGHT: This will return the data in a loop
        # and will NEVER stop
        while True:
            for data in sample:
                yield data

    def serialize_data(self, sample):

        # Round the data to 3 decimal places then times it up to become an index
        sample = sample.round(3) * 1000
        # Number of buckets is the input size divided by the largest input in the sequence
        element_bucket_length = int(self.input_size) + 1
        # Converts the sample into categorical data

        serialized_sample = []

        for element in sample:
            element = int(element)
            # Get the index of the data in the categorical sample
            # minus_gap = 1 if index == 0 or index == len(element) - self.overlap else 0
            # Pad the left and right of the data with 0s and the data in the middle with 1s
            # padding_left = [0] * (index * element_bucket_length - self.overlap)
            # element_padding = [1] * (element_bucket_length + self.overlap * 2 - minus_gap)
            # padding_right = [0] * ((len(element) - index - 1) * element_bucket_length - self.overlap)
            # Add them all together and slap that shit into a new sample
            # serialized_sample.append(padding_left + element_padding + padding_right)
            new_sample = list(np.zeros(element_bucket_length, dtype=int))
            for i in range(element - self.overlap, element + self.overlap + 1):
                if i < 0 or i > len(new_sample) - 1:
                    continue

                try:
                    new_sample[i] = 1
                except:
                    continue
            serialized_sample.append(new_sample)
        self.sample = sample
        return serialized_sample

class DiscreteEncoder(Encoder):
    ''' 
    Converts input data to list of categorical data with padding
    that extends the index to the size of the bucket divided by
    the number of unique inputs
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_data()

    def get_sample(self, index):
        self.sample_classifier = self.df.data.values
        sample = self.serialize_data(self.df.data)
        self.logger.debug(f'Serialized sample {index} ({len(sample)} elements)')

      

        # Feed the data continuosly until training stops
        # FOOD FOR THOUGHT: This will return the data in a loop
        # and will NEVER stop
        while True:
            for data in sample:
                yield data

    def serialize_data(self, sample):
        sample = np.array(sample.values)
        # Number of buckets is the input size divided by the largest input in the sequence
        element_bucket_length = int(self.input_size / max(sample))
        # Converts the sample into categorical data
        categorical_sample = to_categorical(sample)[:, 1:]
        serialized_sample = []

        for element in categorical_sample:
            # Get the index of the data in the categorical sample
            index = np.argmax(element)
            # Pad the left and right of the data with 0s and the data in the middle with 1s
            padding_left = [0] * index * element_bucket_length
            element_padding = [1] * element_bucket_length
            padding_right = [0] * (len(element) - index - 1) * element_bucket_length
            # Add them all together and slap that shit into a new sample
            serialized_sample.append(padding_left + element_padding + padding_right)

        return serialized_sample