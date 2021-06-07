import random as rand
import math

class Column:
    '''
    Columns represent the spatial pool.
    An activated column represents a semantic detail of an input.
    '''

    def __init__(self, _index):
        #index of column in columns
        self.index = _index
        # cells within the column
        self.cells = []
        # connections to the input space {index of input cell : permanence}
        self.input_synapses = {}
        # array of overlap score at each time step over the active duty cycle (index [0] is the oldest)
        self.overlap_duty = []
        #average overlap
        self.mean_overlap = 0
        # array of bits representing if the column was active or not at each time step over the active duty cycle (index [0] is the oldest)
        self.active_duty = []
        # stores the sum of active_duty
        self.activity = 0
        # multiplier for overlap score: > if column is less active than average, < if is more acive than average
        self.boost = 1
        # overlap of columns synapses with input space
        self.overlap_score = 0

    # update the overlap duty cycle and active duty cycle and related variables for this column: takes (parameter for the length of the active duty cycle, current activity state of column)
    def update_duty_cycles(self, _active_duty_length, _is_active):
        if len(self.overlap_duty) > _active_duty_length:
            del self.overlap_duty[0]
        self.overlap_duty.append(self.overlap_score)
        self.mean_overlap = sum(self.overlap_duty)/_active_duty_length
        
        # if the columns active duty array is longer than the HTM module active duty cycle length parameter
        if len(self.active_duty) > _active_duty_length:
            # remove the oldest recorded active duty
            del self.active_duty[0]
        # if the column is currently active
        if _is_active:
            # append the active duty array with a 1
            self.active_duty.append(1)
        # if the column is not currently active
        else:
            # append the active duty array with a 0
            self.active_duty.append(0)
        # activity of the column is equal to the sum of the active duty
        self.activity = sum(self.active_duty)

    # calculates the boost at each timestep: takes (mean activity of all columns in the pool, parameter length of active duty cycle for the module)
    # need to constrain and standardise boost(maybe dont let boost fall below 1??)
    # potential boost ; e^-b(self.activity-_mean_active) (this is what the numenta boiz use)
    # where e is eulers cosstant and b is boosting factor (a config parameter)
    def calculate_boost(self, _boost_factor, _mean_pool_activity, _active_duty_length):
        
        # boost is equal to 1 plus the difference between the columns activity and the mean activity of all columns in the pool
        # normalised against the length of the active duty cycle (the maximum possible difference)
        # therefore yields a value between 0 and 2
        #self.boost = 1 + ((self.activity - _mean_pool_activity) / _active_duty_length)
        
        self.boost = math.exp(_boost_factor*((self.activity/(_active_duty_length*100))-(_mean_pool_activity/(_active_duty_length*100))))



    # upate the columns overlap score: takes ()
    def update_overlap(self, _input, _input_synapse_threshold, _active_duty_length):
        self.overlap_score = 0
        for synapse in self.input_synapses:
            #if the input bit that this synapse is connected to is 1 and the synapse is over the threshold to be connected
            if _input[synapse] == 1 and self.input_synapses[synapse] >= _input_synapse_threshold:
                #add the input to the overlap score of the column
                self.overlap_score += 1
        self.overlap_score *= self.boost

    #returns all the segments in the column that are in the array_to_check
    #show this to dean and compare with old function; is there a way to make this new one as efficient
    def segments_in_column(self, _segments_to_check):
        segments = []
        for segment in _segments_to_check:
            for cell in self.cells:
                if segment in cell.segments:
                   segments.append(segment)
        return segments 

    #returns the segment on the column which, in the previous time step was matching and had the largest number of active potential synapses
    def best_matching_segment(self, _matching_segments_1, _no_active_potential_synapses_1):
        best_segment = None
        best_score = -1
        for segment in self.segments_in_column(_matching_segments_1):
            if _no_active_potential_synapses_1[segment] > best_score:
                best_segment = segment
                best_score = _no_active_potential_synapses_1[segment]
        return best_segment

    def least_used_cell(self):
        fewest_segments = 999
        for cell in self.cells:
            if len(cell.segments) < fewest_segments:
                fewest_segments = len(cell.segments)
        least_used_cells = []
        for cell in self.cells:
            if len(cell.segments) == fewest_segments:
                least_used_cells.append(cell)
        random = rand.randint(0,len(least_used_cells)-1)
        return least_used_cells[random]

