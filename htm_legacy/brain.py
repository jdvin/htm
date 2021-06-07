import pygame, sys
from pygame.locals import *
import random as rand
import numpy as np
from Modules import master_values as mv
from encoder import SimpleEncoder
from Modules.visualiser import visualiser
from Modules.tissue import neuron, n_column, distal_segment
from Modules.Misc import supporting_functions as s_f
from Modules.dict_classifier import dict_classifier
import datetime
import pdb

#NOTES
#most arrays are indexes
#DISCREPENCIES
#boosting algorithm?
#least used cell is supposed to select a random cell but i cant imagine why
class Brain():

    def __init__(self):
        #modules
        self.encoder = SimpleEncoder(mv.ip_size)
        self.vis = visualiser()
        self.classifier = dict_classifier()

        #tick
        self.t = 0

        #input space initial state
        self.ipt = [0]*mv.ip_size

        #neurons
        #cortex = [n_column([neuron(0)]*mv.col_depth)]*mv.spl_cols
        #array of actual cortical columns
        self.cortex = []

        #>>FOR ALL BELOW : [0](t), [1](t-1)<<
        #array of indexes of active columns
        self.active_columns = [[], []]
        #array of [index of parent column, index of active cell]
        self.active_cells = [[], []]
        #array of [index of parent column, index of winner cell]
        self.winner_cells = [[], []]
        #array of [index of parent column, index of parent cell, index of active segment]
        self.active_segments = [[], []]
        #array of [index of parent column, index of parent cell, index of matching segment]
        self.matching_segments = [[], []]
        #array of [segment ID(i_coli_celli_seg), num of active potential synapses for segment]
        self.n_active_potential_synapses = [{}, {}]
        #temp variable for the mean activity of the columns (storing total activity)
        self.t_mean_active = 0


        #potential pool size
        p_s = int(mv.ip_size * mv.pp_size)

        #for all spatial columns
        for i in range(mv.spl_cols):
            self.cortex.append(n_column())
            for j in range(mv.col_depth):
                self.cortex[i].neurons.append(neuron())

        for i in range(len(self.cortex)):
            p_pool = rand.sample(range(mv.ip_size-1), p_s)
            self.cortex[i].p_synapses = {j : np.random.normal(mv.p_syn_threshold, mv.p_syn_threshold/4) for j in p_pool}

        self.vis.init_prox_synapses(self.cortex)

    #for each index array, shift [0](t) --> [1](t-1)
    def time_step(self):
        self.active_columns[1].clear()
        self.active_columns[1] = self.active_columns[0].copy()
        self.active_columns[0].clear()

        self.active_cells[1].clear()
        self.active_cells[1] = self.active_cells[0].copy()
        self.active_cells[0].clear()

        self.winner_cells[1].clear()
        self.winner_cells[1] = self.winner_cells[0].copy()
        self.winner_cells[0].clear()

        self.active_segments[1].clear()
        self.active_segments[1] = self.active_segments[0].copy()
        self.active_segments[0].clear()

        self.matching_segments[1].clear()
        self.matching_segments[1] = self.matching_segments[0].copy()
        self.matching_segments[0].clear()

        self.n_active_potential_synapses[1].clear()
        self.n_active_potential_synapses[1] = self.n_active_potential_synapses[0].copy()
        self.n_active_potential_synapses[0].clear()

    def spatial_pool(self):
        #new array for sorted cortex
        sort_cortex = []
        #mean activity = the total activity for the columns over the duty cycle recorded last update divided by number of columns
        mean_active = self.t_mean_active / mv.spl_cols
        #reset total activity variable
        self.t_mean_active = 0

        #spatial pooling
        #for columns in cortex
        for i in range(len(self.cortex)):
            #update the column
            self.cortex[i].update(s_f.is_active([i], self.active_columns[1]), mean_active)
            #add activity of column to total activity counter of cortex
            self.t_mean_active += self.cortex[i].activity
            #for all proximal synap`ses in column
            for ps in self.cortex[i].p_synapses:
                #if the proximal synapse permanence is greater than the synaptic threshold AND the input tile the synapse is connected to is active
                if self.cortex[i].p_synapses[ps] > mv.p_syn_threshold and self.ipt[ps] == 1:
                    #add 1 to the column overlap score
                    self.cortex[i].overlap_s += 1
                    #is overlap only for connected synapses?? lamo yes it is; THERES YOUR PROBLEM (solved)
            #multiply the columns overlap score by its boost factor
            self.cortex[i].overlap_s = self.cortex[i].overlap_s * self.cortex[i].boost
            #create a representation of the cortex in sort_cortex with each columns index<0> and overlap score<1>
            sort_cortex.append([i, self.cortex[i].overlap_s])
        #sort sort_cortex from lowest to hgihest based on overlap_s ([1])
        sort_cortex = sorted(sort_cortex, key=lambda column: column[1])
        #set the number of columns to be inhibited to (number of spatial columns - (the number of spatial columns * the proportion of columns which can be active at any time))
        inhibition_thresh = mv.spl_cols - int(mv.spl_cols * mv.active_sparcity)

        #column activation and learning
        #for each indexed spatial column in the non inhibited section of sort cortex (i.e. the highest X amount of activated columns)
        for i in range(mv.spl_cols-1, inhibition_thresh, -1):
            ##add the index of the column to the active list
            #   print(sort_cortex[i][0])
            self.active_columns[0].append(sort_cortex[i][0])
            #for all the synapses in the columns
            for j in self.cortex[sort_cortex[i][0]].p_synapses:
                #if its corresponding input tile is active
                if self.ipt[j] == 1:
                    #and the permanance is less than 1
                    if self.cortex[sort_cortex[i][0]].p_synapses[j] < 1:
                        #increase the synapse permanance by the corresponding increment
                        self.cortex[sort_cortex[i][0]].p_synapses[j] += mv.p_syn_incr
                #otherwise if its input tile is not active
                else:
                    #and the permanance of the synapse is not already 0
                    if self.cortex[sort_cortex[i][0]].p_synapses[j] > 0:
                        #decrease the permanance by the corresponding decrement
                        self.cortex[sort_cortex[i][0]].p_synapses[j] -= mv.p_syn_decr

    def grow_synapses(self, _seg, _new_syn_count):
        candidates = self.winner_cells[1].copy()
        while len(candidates) > 0 and _new_syn_count > 0:
            presynaptic_cell = rand.randint(0, len(candidates)-1)
            already_connected = False
            for syn in self.cortex[_seg[0]].neurons[_seg[1]].d_segs[_seg[2]].synapses:
                if syn[0] == candidates[presynaptic_cell]:
                    already_connected = True
            if not already_connected:
                self.cortex[_seg[0]].neurons[_seg[1]].d_segs[_seg[2]].synapses.append([candidates[presynaptic_cell], mv.d_init_perm])
                _new_syn_count -= 1
            del candidates[presynaptic_cell]

    def activate_predicted_column(self, _i_col):
        #for each segment active last time step in the predicted column
        for seg in s_f.segments_in_col(_i_col, self.active_segments[1]):
            #append the current active cells with the column and cell of the active segment
            self.active_cells[0].append([seg[0], seg[1]])
            #append the current winner cells with the column and cell of the active segment
            self.winner_cells[0].append([seg[0], seg[1]])
            #for all synapses in the segment [IF LEARNING ENABLED]
            for syn in self.cortex[seg[0]].neurons[seg[1]].d_segs[seg[2]].synapses:
                #if the presynaptic cell of the synapse was active last time step
                if s_f.is_active(syn[0], self.active_cells[1]):
                    #increase the permanence of the syanpse
                    syn[1] += mv.d_syn_incr
                #otherwise
            else:
                    #decrease the permanance of the synapse
                    syn[1] -= mv.d_syn_decr
            #calculate number of new synapses to be added to this column
            new_syn_count = (mv.synapse_sample_size - self.n_active_potential_synapses[1][int(str(seg[0])+str(seg[1])+str(seg[2]))])
            #if the number is greater than 0
            if new_syn_count > 0:
                self.grow_synapses(seg, new_syn_count)

    def burst_column(self, _i_col):
        #generate bit array corresponding to active columns
        self.classifier.bucket_pool_pairs[s_f.get_activity_map(mv.spl_cols, self.active_columns[0])] = self.ipt
        #for each cell in the bursting column
        for i_cell in range(len(self.cortex[_i_col].neurons)):
            #add it to the list of active cells
            self.active_cells[0].append([_i_col, i_cell])
        #if the any segments in the column were matching_segments
        if len(s_f.segments_in_col(_i_col, self.matching_segments[1])) > 0:
            #select a learning segment based on the best matching segment algorithm
            learning_segment = s_f.best_matching_segment(_i_col, self.matching_segments[1], self.n_active_potential_synapses)
            #the winner cell of the column is cell which the learning segment is attached to
            winner_cell = [learning_segment[0], learning_segment[1]]
        else:
            #the winner cell is teh least used cell in the column
            winner_cell = s_f.least_used_cell(_i_col, self.cortex[_i_col])
            #grow a new segment on the cell the be the learning segment
            self.cortex[winner_cell[0]].neurons[winner_cell[1]].d_segs.append(distal_segment([]))
            learning_segment = [winner_cell[0], winner_cell[1], len(self.cortex[winner_cell[0]].neurons[winner_cell[1]].d_segs)-1]

        #add the winner cell to the list of current winner_cells
        self.winner_cells[0].append(winner_cell)
        #for each synapse in the learning segment (attacheted to the winner cell)
        for syn in self.cortex[learning_segment[0]].neurons[learning_segment[1]].d_segs[learning_segment[2]].synapses:
            #if the winner cell (presynaptic cell for the synapse) was active last time step
            if s_f.is_active(syn[0], self.active_cells[1]):
                syn[1] += mv.d_syn_incr
            else:
                syn[1] -= mv.d_syn_decr
        #calculate number of new synapses to be added to this learning semgent
        learning_segment_ID = int(str(learning_segment[0])+str(learning_segment[1])+str(learning_segment[2]))
        try:
            n = self.n_active_potential_synapses[1][learning_segment_ID]
        except KeyError:
            n = 0
        new_syn_count = (mv.synapse_sample_size - n)
        #if the number is greater than 0
        if new_syn_count > 0:
            #grow synapses on the learning segment
            self.grow_synapses(learning_segment, new_syn_count)

    def punish_predicted_column(self, _i_col):
        #for each segment that was in matching segments last time step
        for seg in s_f.segments_in_col(_i_col, self.matching_segments[1]):
            #for each synapse in the segment
            for syn in seg.synapses:
                #if the cell was active last time step
                if s_f.is_active(syn[0], self.active_cells[1]):
                    #decrease the strength of the synapse in the cell
                    syn[1] -= mv.false_pred_decr

    def temporal_memory(self):
        #for all columns
        for i_col in range(len(self.cortex)):
            #if column is active
            if s_f.is_active([i_col], self.active_columns[0]):
                #if any of the columns segments were active last timestep
                if len(s_f.segments_in_col(i_col, self.active_segments[1])) > 0:
                    self.activate_predicted_column(i_col)
                else:
                    self.burst_column(i_col)
            else:
                #if any of the columns segments were matching lst timestep
                if len(s_f.segments_in_col(i_col, self.matching_segments[1])) > 0:
                    self.punish_predicted_column(i_col)
        #for all columns
        for i_col in range(len(self.cortex)):
            #for all cells in the columns
            for i_cell in range(len(self.cortex[i_col].neurons)):
                #for segs in the cell
                for i_seg in range(len(self.cortex[i_col].neurons[i_cell].d_segs)):
                    #reset values
                    n_active_connected = 0
                    n_active_potential = 0
                    #for all synapses in the segment
                    for syn in self.cortex[i_col].neurons[i_cell].d_segs[i_seg].synapses:
                        #if the cell is active in current time step
                        if s_f.is_active([syn[0][0], syn[0][1]], self.active_cells[0]):
                            #if syn permanance is greater than the threshold
                            if syn[1] >= mv.d_syn_threshold:
                                #increment number connected synapses on the segment
                                n_active_connected += 1
                            #if syn permanance is greater than 0
                            if syn[1] >= 0:
                                #increment number of potential synapses on the segment
                                n_active_potential += 1
                    #if number of active connected synapses on the segment is greater than the segment activation threshold
                    if n_active_connected >= mv.actv_threshold:
                        #add segment to active segments
                        self.active_segments[0].append([i_col, i_cell, i_seg])
                    #if number of potential connected syanpses on the segment is greater than the segment learning threshold
                    if n_active_potential >= mv.learn_threshold:
                        #add segment to matching segment
                        self.matching_segments[0].append([i_col, i_cell, i_seg])
                    #update the current active potential database
                    self.n_active_potential_synapses[0][int(str(i_col)+str(i_cell)+str(i_seg))] = n_active_potential

    def cycle_htm(self):
        #parse in input from encoder
        
        self.ipt = self.encoder.get_sample(0)
        #if the input is not empty
        if self.ipt is not None:
            #step forward
            self.time_step()
            #run sptial pooling
            self.spatial_pool()
            #run temporal Memory
            self.temporal_memory()
            #predict next step
            prediction = s_f.pred_next_step(mv.spl_cols, self.active_segments[0])
            #print next step
            classifier.classify(prediction)
            #update visualisation
            self.vis.update(self.ipt, self.cortex, self.active_columns, self.active_segments)

    def update(self, fps):
        self.cycle_htm()
        #print("cycle")
        if self.t == (fps/mv.cyc_ps):
            self.cycle_htm()
            self.t = 0
        else:
            self.t += 1

    def draw(self, display, fps):
        self.vis.draw(display)
