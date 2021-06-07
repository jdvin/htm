'''
This file is the base config. Any other config files shall import this
file and override the variables.
'''
# from enum import Enum
# import logging

htm = dict(
    # ENCODER
    encoder_type = 'ScalerEncoder',

    # POOL SIZES
    input_size=200, # No. of cells in input space
    no_spatial_columns=2048, # No. of columns in the spatial pool 
    column_depth= 1, # No. of cells in each column

    # SPATIAL POOL VALUES
    ppool_size=0.85, # potential pool size of each column (as percentage of <ip_size>) 
    column_activation_threshold=0, #the minimum overlap score a column can have and still be active
    input_synapse_threshold=0.1, # threshold over which a potential connection is synapsed
    active_sparcity= 0.02, # percentage of active columns in each step 
    input_synapse_increment=0.05,  # increment for active synapse permanence
    input_synapse_decrement=0.005,  # decrement for inactive synapses
    max_boost=2,  # maximum boost value CHANGE THE BOOST ALGORITHM
    boost_factor = 100,
    active_duty_length=1000,  # number of most recent cycles counted in cells activity

    # TEMPORAL MEMORY VALUES
    segment_active_threshold=16, # threshold of connected synapses required in a segment to activate it
    segment_learning_threshold=12,  # minimum number of active synapses for a segment to be considered as best matching
    cell_synapse_initial_permanence=0.21,  # initial permanence of segment synapses
    cell_synapse_threshold=0.5, # connected threshold for segment synapses
    max_new_segment_synapse=20,  # maximum number of synapses added to a segment during learning
    cell_synapse_increment=0.1,  # increment for distal synapses
    cell_synapse_decrement=0.05, # decrement for distal synapses
    false_prediction_decrement=0.0,  # decrement for synapses of falsely predicted cells
    max_cell_segments=128,  # maximum segments per cell
    max_segment_synapses=32, # maximum synapses per segment
    learning_enabled=True,  # will distal synapses be adjusted
    synapse_sample_size=16, # target number of active synapses on a segment
)