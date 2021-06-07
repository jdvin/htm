import random
import time
import numpy as np
from htm.components import Segment, Cell, Column


def time_method(func):
    def time_method_wrapper(*args, **kwargs):
        present = time.time()
        result = func(*args, **kwargs)
        took = round((time.time() - present) * 1000)
        args[0].logger.debug(f'HTM {func.__name__!r} method took {took} ms')
        return result
    return time_method_wrapper


class HTM:
    def __init__(self, logger, config):
        
        self.logger = logger
        self.logger.info("--Initialising HTM instance paramters")

        self._load_config(config)

        #dict of [key]<real input value>: [value] <SDR>
        self.encoder_classifier = {}

        self.columns = []

        self.training_parameters = {}

        # FOR ALL BELOW : [0] = t, [1] = t-1
        # array of indexes of active columns
        self.active_columns = [[], []]
        # pointer array of active cells
        self.active_cells = [[], []]
        # pointer array of winner cells
        self.winner_cells = [[], []]
        # pointer array of active segments
        self.active_segments = [[], []]
        # pointer array of matching segments
        self.matching_segments = [[], []]
        # array of [segment ID(i_coli_celli_seg), num of active potential synapses for segment]
        self.no_active_potential_synapses = [{}, {}]

        self.pointer_arrays = [self.active_columns, self.active_cells, self.winner_cells,
                               self.active_segments, self.matching_segments, self.no_active_potential_synapses]

        ppool_size = int(self.input_size * self.ppool_size)

        # initialise columns and cells
        for i in range(self.no_spatial_columns):
            self.columns.append(Column(i))
            for j in range(self.column_depth):
                self.columns[i].cells.append(Cell())

        # initialise input synapses
        for column in self.columns:
            potential_pool = random.sample(range(self.input_size - 1), ppool_size)
            column.input_synapses = {j : np.random.normal(self.input_synapse_threshold, 
                                                          self.input_synapse_threshold / 4) for j in potential_pool}

        # calculate the column with the lowest overlap score than can be active
        self.inhibition_limit = self.no_spatial_columns - int(self.no_spatial_columns * self.active_sparcity)

        self.logger.info('HTM instance loaded')

    def _load_config(self, config):
        self.config = config
        self.__dict__.update(config)

    #returns an bit array corresponding to the activation of the spatial pool at the current time step
    def sdr_snapshot(self, t):
        return [column in self.active_columns[t] for column in self.columns]
   
    # step forward in time by iterating each pointer array forward, making way for new data in pointer_array[0]
    def time_step(self):
        for pointer_array in self.pointer_arrays:
            pointer_array[1].clear()
            pointer_array[1] = pointer_array[0].copy()
            pointer_array[0].clear()

    def new_pattern(self):
        for pointer_array in self.pointer_arrays:
            pointer_array[0].clear()

    #directly activates columns with pattern specified by sdr
    def direct_activate(self, sdr):
        for i in range(len(sdr)):
            if sdr[i]:
                self.active_columns[0].append(self.columns[i])

    # 
    @time_method
    def spatial_pool(self, input):
        '''
        this algorithm activates a series of columns which represent a given input semantically
        Takes one argument; input array
        '''

        # temp variable to sum total activity of cortex (required to calculate mean activity)
        total_pool_activity = 0

        # calculate how much each columns active synapses overlap with the input space and multiply by boosting factor
        for column in self.columns:
            column.update_overlap(input, self.input_synapse_threshold, self.active_duty_length)
            total_pool_activity += column.activity

        # create a list which stores the columns in order sorted in ascending order by overlap score
        sorted_columns = sorted(self.columns, key=lambda column: column.overlap_score)

        # for the columns with the top <self.active_sparticity>% of overlap score
        for i in range(self.inhibition_limit - 1, self.no_spatial_columns):
            if sorted_columns[i].overlap_score >= self.column_activation_threshold:
                # add them to the active columns list
                self.active_columns[0].append(sorted_columns[i])
                # adjust synaptic permances depending on if the synapse was connected to an active input
                for synapse in sorted_columns[i].input_synapses:
                    if input[synapse] == 1 and sorted_columns[i].input_synapses[synapse] != 1:
                        sorted_columns[i].input_synapses[synapse] += self.input_synapse_increment
                    elif sorted_columns[i].input_synapses[synapse] != 0:
                        sorted_columns[i].input_synapses[synapse] -= self.input_synapse_decrement

        for i in range(self.no_spatial_columns):
            #update active and overlap duty cycles for all columns | parse in activity based on location of index in sorted columns
            sorted_columns[i].update_duty_cycles(self.active_duty_length, not (i < self.inhibition_limit - 1))
            self.mean_pool_activity = total_pool_activity / self.no_spatial_columns
            sorted_columns[i].calculate_boost(self.config['boost_factor'], self.mean_pool_activity, self.active_duty_length)
            #increase the permanance of all columns whos overlap score hasnt risen above threshold over the duty cycle
            if len(self.columns[i].overlap_duty) == self.active_duty_length and self.columns[i].mean_overlap < self.column_activation_threshold:
                for synapse in self.columns[i].input_synapses:
                    self.columns[i].input_synapses[synapse] += (0.1 * self.input_synapse_threshold)

    def get_echo(self):
        '''
        returns an array of input cells
        which the currently activated columns are connected to above threshold
        '''

        _echo = [0 for i in range(self.input_size)]

        for col in self.active_columns[0]:
            for syn in col.input_synapses:
                if col.input_synapses[syn] >= self.input_synapse_threshold:
                    _echo[syn] = 1
        
        return _echo

                
                

    #cell activation logic for a colum that has cells which were correctly predicted to be active
    def activate_predicted_column(self, column):
        # activate cells with segments that were active last time step
        for segment in column.segments_in_column(self.active_segments[1]):
            self.active_cells[0].append(segment.parent_cell)
            self.winner_cells[0].append(segment.parent_cell)
            if self.learning_enabled: 
                # adjust permanences in the synapses according to if the presynaptic cell of the synapse was active last timestep
                for synapse in segment.synapses:
                    if synapse[0] in self.active_cells[1]:
                        synapse[1] += self.cell_synapse_increment
                    else:
                        synapse[1] -= self.cell_synapse_decrement
                #grow synapses on the segment to the winner cells of the previous time step
                new_synapse_count = self.synapse_sample_size - self.no_active_potential_synapses[1][segment]
                segment.grow_synapses(self.winner_cells[1].copy(), new_synapse_count, self.cell_synapse_initial_permanence)

    #cell activation logic for a column which does not have cells which were predicted to be active
    def burst_column(self, _column):
        #unsure of step in line 186 of legacy brain: come back to later
        for cell in _column.cells:
            self.active_cells[0].append(cell)
        if len(_column.segments_in_column(self.matching_segments[1])) > 0:
            learning_segment = _column.best_matching_segment(self.matching_segments[1], self.no_active_potential_synapses[1])
            winner_cell = learning_segment.parent_cell
        else:
            winner_cell = _column.least_used_cell()
            if self.learning_enabled:
                winner_cell.segments.append(Segment(winner_cell, []))
                learning_segment = winner_cell.segments[-1]
        
        self.winner_cells[0].append(winner_cell)

        if self.learning_enabled:
            for synapse in learning_segment.synapses:
                #if synapse presynaptic cell was active last time step
                if synapse[0] in self.active_cells[1]:
                    synapse[1] += self.cell_synapse_increment
                else:
                    synapse[1] -= self.cell_synapse_decrement
            try:
                n = self.no_active_potential_synapses[1][learning_segment]
            except KeyError:
                n = 0
            new_synapse_count = self.synapse_sample_size - n
            learning_segment.grow_synapses(self.winner_cells[1].copy(), new_synapse_count, self.cell_synapse_initial_permanence)

    def punish_predicted_column(self, column):
        if self.learning_enabled:
            for segment in column.segments_in_column(self.matching_segments[1]):
                for synapse in segment.synapses:
                    if synapse[0] in self.active_cells[1]:
                        synapse[1] -= self.false_prediction_decrement

    @time_method
    def temporal_memory(self):
        # for all columns
        for column in self.columns:
            # if column is active this timestep
            if column in self.active_columns[0]:
                # if column had active segments last time step
                if len(column.segments_in_column(self.active_segments[1])) > 0:
                    # then this column was predicted; activate it
                    self.activate_predicted_column(column)
                else:
                    self.burst_column(column)
            else:
                if len(column.segments_in_column(self.matching_segments[1])) > 0:
                    self.punish_predicted_column(column)

        # for all columns
        for column in self.columns:
            # for all cells in column
            for cell in column.cells:
                # for all segments in cell
                for segment in cell.segments:
                    # intialise connected synapses
                    no_active_connected = 0
                    no_active_potential = 0
                    # for synapses in segment
                    for synapse in segment.synapses:
                        # if the presynaptic cell is active
                        if synapse[0] in self.active_cells[0]:
                            # if the permanance of the synapse is greater than threshold
                            if synapse[1] >= self.cell_synapse_threshold:
                                # increment the number of active connected synapses for this segment
                                no_active_connected += 1
                            # if the permanance of the synapse is greater than 0
                            if synapse[1] >= 0:
                                # increment the number of active potential synapses for this segment
                                no_active_potential += 1 
                    # if the number of active connected synapses for the segment is greater than segment active threshold
                    if no_active_connected >= self.segment_active_threshold:
                        # add segment to active connected segments for this time step
                        self.active_segments[0].append(segment)
                    # if the number of active potential synapses for this segment is greater than segment learning threshold
                    if no_active_potential >= self.segment_learning_threshold:
                        # add segment to matching segments for this timestep
                        self.matching_segments[0].append(segment)
                    # log number of active pontential synapses for this segment for this timestep
                    self.no_active_potential_synapses[0][segment] = no_active_potential

    def get_next_prediction(self):
        prediction_SDR = []
        for column in self.columns:
            if len(column.segments_in_column(self.active_segments[0])) > 0:
                prediction_SDR.append(True)
            else:
                prediction_SDR.append(False)
        return prediction_SDR

    #get a accumulative predictions for n steps in the future
    @time_method
    def predict_n_steps(self, n):
        predictions = []
        self.learning_enabled = False
        for i in range(n):
            predictions.append(self.get_next_prediction())
            self.time_step()
            self.direct_activate(predictions[-1])
            self.temporal_memory()
        self.learning_enabled = True
        return predictions

    #iterate the algorithm
    @time_method
    def update(self):
        self.time_step()
        input = next(self.element_generator)
        self.spatial_pool(input)
        self.temporal_memory()
