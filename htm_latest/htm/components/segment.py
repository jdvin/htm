import weakref
import random as rand

class Segment:
    '''
    Segments connect cells to each other within the htm module. 
    They are ONLY necessary for the TEMPORAL MEMORY algorithm.
    '''

    def __init__(self, _parent_cell, _synapses):
        '''Intialise the segment with synapses'''

        # initialise active potential synapses
        self.active_potential_synapses = 0
        #pass the parent_cell in
        #not really sure what weakref is but a kind gentleman on stack overflow guarenteed me that it was safe from garbage collectors
        self.parent_cell = weakref.ref(_parent_cell)

        # initialise synapses: array of synapses on segment [0(presynaptic cell), 1(permanance)]
        self.synapses = _synapses

    #grows synapses on a segment to the winner cells of the last time step
    #pass in (candidates = winner_cells[1].copy!!, segment to grow on, number of new synapses to grow)
    def grow_synapses(self, _candidates, _new_synapse_count, _cell_synapse_initial_permanence):
        while len(_candidates) > 0 and _new_synapse_count > 0:
            presynaptic_cell = rand.randint(0, len(_candidates)-1)
            already_connected = False
            for synapse in self.synapses:
                if synapse[0] == _candidates[presynaptic_cell]:
                    already_connected = True
            if not already_connected:
                self.synapses.append([_candidates[presynaptic_cell], _cell_synapse_initial_permanence])
                _new_synapse_count -= 1
            del _candidates[presynaptic_cell]
    
