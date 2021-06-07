from htm.config.layer_base import *

# htm['input_size'] = 16
# htm['no_spatial_columns'] = 100
# htm['active_sparcity'] = 0.1



# htm['segment_active_threshold'] /= htm['learning_speed']
# htm['segment_learning_threshold'] /= htm['learning_speed']
# htm['synapse_sample_size'] /= htm['learning_speed']
# htm['max_new_segment_synapse'] /= htm['learning_speed']

htm['input_size'] = 2048 * 2


htm['learning_speed'] = 2
htm['input_synapse_increment'] = 0.05 * htm['learning_speed']
htm['input_synapse_decrement'] = 0.005 * htm['learning_speed']

