import math as m

#OPERATION CONTRAINTS
cyc_ps = 1 #maximum cycles per second
system_scale = 1 #scale of the htm system from the default parameters

#POOL SIZES
ip_size = 256 # No. of cells in input space
spl_cols = int(2048*system_scale) # No. of columns in the spatial pool
col_depth = int(32*system_scale) # No. of neurons in each column
active_sparcity = 0.02 #percentage of active columns in each step

#SPATIAL POOL VALUES
pp_size = 0.85 #potential pool size of each column (as percentage of <ip_size>)
p_syn_threshold = 0.1 #threshold over which a potential connection is synapsed
p_syn_incr = 0.05 #increment for active synapse permanence
p_syn_decr = 0.005 #decrement for inactive synapses
max_boost = 2 #maximum boost value CHANGE THE BOOST ALGORITHM
act_duty_cycle = 1000 #number of most recent cycles counted in cells activity

#TEMPORAL MEMORY VALUES
actv_threshold = int(16*system_scale) #threshold of connected synapses required in a segment to activate it
learn_threshold = int(12*system_scale) #minimum number of active synapses for a segment to be considered as best matching
d_init_perm = 0.21 #initial permanence of distal synapses
d_syn_threshold = 0.5 #connected threshold for distal synapses
max_new_d_syn = 20 #maximum number of synapses added to a segment during learning
d_syn_incr = 0.1 #increment for distal synapses
d_syn_decr = 0.1 #decrement for distal synapses
false_pred_decr = 0.0 #decrement for falsely predicted cells synapses
max_cell_segs = int(128*system_scale) #maximum segments per cell
max_seg_syns = int(32*system_scale) #maximum synapses per segment
learning_enabled = True #will distal synapses be adjusted
synapse_sample_size = int(16*system_scale) #target number of active synapses on a segment

#CLASSIFIER
hidden_layers = 1
nodes_per_hidden_layer = 2048

#VISUALISATION
n_cols = 4 #No. of colours in patterns

input_space_size = 400 #dimensions of input space in pixels
input_space_location = [25, 550] #location of top left corner of input space

sp_layer_size = 200 #dimensions of each spatial pool layer in pixels
sp_layer_location = [[600,730],[600,510],[600,290],[600,70]] #top left corner of each layer

ADC_vis_size = 300 #dimensions of the ADC visualiser
ADC_vis_location = [1000, 650]
#sp_layer_location = [i for]
