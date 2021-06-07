import pygame, sys
from pygame.locals import *
import random as rand

#checks if a particular component is in an activity source
#takes in an array of the integers to compare to the members of the activity source
#component integers to compare must be in an array, activity source must be [0] (t) OR [1] (t-1)
def is_active(to_check, activity_source):
    if len(activity_source) > 0:
        if len(to_check) == 1:
            for col in activity_source:
                if col == to_check[0]:
                    return True

        elif len(to_check) == 2:
            for cell in activity_source:
                if cell == to_check:
                    return True

        elif len(to_check) == 3:
            for seg in activity_source:
                if seg == to_check:
                    return True

#takes in the index of the column to bbe checked and the array of segment indexes to be checked
#returns the index ([index of parent column, index of parent cell, index of active segment]) of segments in the column which are in the given segmenet array
def segments_in_col(_i_col, _segment_array):
    segs = []
    #for all segments in segment array
    for seg in _segment_array:
        #if the column the segment belongs to is the column we are checking
        if seg[0] == _i_col:
            #append the return array with the segment
            segs.append(seg)
    return segs

#returns the the index of the least used cell in the column
#if there are multiple that are equally used, it randomly selects one
def least_used_cell(_i_col, _column):
    #number of segs of least used cell to the first cell
    n_least_used = len(_column.neurons[0].d_segs)
    #for all the cells in the column
    for cell in _column.neurons:
        #if cell has less segments than the current least used
        if len(cell.d_segs) < n_least_used:
            #number of least used equals the number in that cell
            n_least_used = len(cell.d_segs)
    least_used = []
    #for index in cells of column
    for i in range(len(_column.neurons)):
        #if the cell has the same number of segments as the least used cell
        if len(_column.neurons[i].d_segs) == n_least_used:
            #add it to the list of least used cell indexes
            least_used.append(i)
    #return the index of the column and a random cell in the least used list
    return([_i_col, least_used[rand.randint(0, (len(least_used)-1))]])

#pick a matching segment from the last time step on the column with the most active potential syynapses
def best_matching_segment(_i_col, _matching_segments_1, _num_active_potential_synapses):
    #initialise variables
    best_matching_segment = None
    best_score = -1
    #for all segments in the column which were matching last time step
    for seg in segments_in_col(_i_col, _matching_segments_1):
        #n = number of active potential synapses in the segment last time step
        n = _num_active_potential_synapses[1][int(str(seg[0])+str(seg[1])+str(seg[2]))]
        #if n is greater than the last best score
        if n > best_score:
            #set the new best matching segment to seg
            best_matching_segment = seg
            #set the new best score to n
            best_Score = n
    #return the best matching segment
    return best_matching_segment

#generate bit array corresponding to active columns
def get_activity_map(_spatial_pool_size, _active_columns):
    map = [0]*_spatial_pool_size
    for i in _active_columns:
        map[i] = 1
    return map

def pred_next_step(_spatial_pool_size, _active_segments_0):
    pred = [0]*_spatial_pool_size
    for i in range(len(pred)):
        if len(segments_in_col(i, _active_segments_0)):
            pred[i] = 1
    return pred
