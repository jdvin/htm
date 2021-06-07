import argparse
import logging
import os
import numpy as np
import matplotlib.pyplot as plt
import itertools
from htm.encoder import ScalerEncoder, DiscreteEncoder
from importlib import import_module
from htm.factory import Factory
from htm.enums import PredictionType
from data.cat_generator import generate_cat_exemplars

'''
Some Direction Lol:
Test for the emergence of abstract similarity
'''

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s\t=> %(message)s')
logger = logging.getLogger()
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

logger.info("Beginning Simulation")

network_factory = Factory(logger=logger)

parser = argparse.ArgumentParser(description='''
Run Semantic Network Simulation
''')

parser.add_argument('config',
                    type=str,
                    help='Main Config')

args = parser.parse_args()
config = args.config

# Load parameters from config file
config_path = 'htm.config.' + config
config = {}
try:
    imported_config = import_module(config_path)
except ImportError as e:
    raise ImportError(f'Could not import specified config: {config}\n{e}')

logger.debug('Importing config module: ' + config_path)
for parameter in [param for param in imported_config.__dict__ if param[0] != '_']:
    config[parameter] = imported_config.__dict__[parameter]
logger.info('Imported config module: ' + config_path)

layer_1 = network_factory.create_htm_instance('sem_test')

logger.info("--Generating Categories")

n_exemplars = 5

categories = []

intracat_raw_sims = []
intracat_rep_sims = []

cat_permutations = list(itertools.permutations([0,1,2], 2))
exem_permutations = list(itertools.permutations([i for i in range(n_exemplars)], 2))


# generate categories with different levels of intra category disortion
for i in range(3):
    categories.append(generate_cat_exemplars(200, 0.1, n_exemplars, 0.04)) 


logger.info("Raw Exemplar Similarity")
logger.info("--Calculating Intra-Category Simularity")

intracat_sims = []
for cat in categories:
    intracat_sim = 0
    
    for perm in exem_permutations:
        intracat_sim += network_factory.sdr_percent_overlap(cat[perm[0]], cat[perm[1]])

    intracat_sims.append(intracat_sim / len(exem_permutations))

logger.info("--Calculating Extra-Category Similarity")

extracat_sim = 0
for cat_perm in cat_permutations:
    for exem_perm in exem_permutations:
        extracat_sim += network_factory.sdr_percent_overlap(categories[cat_perm[0]][exem_perm[0]], 
                                                            categories[cat_perm[1]][exem_perm[1]])

extracat_sim /= (len(exem_permutations) * len(cat_permutations))

for i in range(len(intracat_sims)):
    logger.info(f"> Intra-Category Similarity for Category {i+1}: {intracat_sims[i]}")

logger.info(f"> Extra-Category Similarity: {extracat_sim}")

logger.info("Exemplar Representation Similarity")

logger.info("--Loading Exemplar Representations")
representations = []
for cat in categories:
    category_representations = []
    for exemplar in cat:
        layer_1.time_step()
        layer_1.spatial_pool(exemplar)
        category_representations.append([int(col) for col in layer_1.sdr_snapshot(0)])
        
    representations.append(category_representations)

logger.info("--Calculating Intra-Category Similarity")
intracat_sims = []
for cat in representations:
    intracat_sim = 0

    for perm in exem_permutations:
        intracat_sim += network_factory.sdr_percent_overlap(cat[perm[0]], cat[perm[1]])
    
    intracat_sims.append(intracat_sim / len(exem_permutations))

logger.info("--Calculating Extra-Category Similarity")
extracat_sim = 0
for cat_perm in cat_permutations:
    for exem_perm in exem_permutations:
        extracat_sim += network_factory.sdr_percent_overlap(representations[cat_perm[0]][exem_perm[0]],
                                                            representations[cat_perm[1]][exem_perm[1]])
extracat_sim /= (len(cat_permutations) * len(exem_permutations))

for i in range(len(intracat_sims)):
    logger.info(f"> Intra-Category Similarity for Category {i+1}: {intracat_sims[i]}")

logger.info(f"> Extra-Category Similarity: {extracat_sim}")


# fig, [sparcity_plot_1, overlap_plot_1, 
#       sparcity_plot_2, overlap_plot_2,
#       sparcity_plot_3, overlap_plot_3,
#       sparcity_plot_4, overlap_plot_4,
#       sparcity_plot_5, overlap_plot_5] = plt.subplots(nrows=10, ncols=1)

# presentations_axis = [i for i in range(0, representations)]

# sparcity_plot_1.plot(presentations_axis, echo_sparcity[0])
# overlap_plot_1.plot(presentations_axis, echo_overlap[0])

# sparcity_plot_2.plot(presentations_axis, echo_sparcity[1])
# overlap_plot_2.plot(presentations_axis, echo_overlap[1])

# sparcity_plot_3.plot(presentations_axis, echo_sparcity[2])
# overlap_plot_3.plot(presentations_axis, echo_overlap[2])

# sparcity_plot_4.plot(presentations_axis, echo_sparcity[3])
# overlap_plot_4.plot(presentations_axis, echo_overlap[3])

# sparcity_plot_5.plot(presentations_axis, echo_sparcity[4])
# overlap_plot_5.plot(presentations_axis, echo_overlap[4])

# fig.show()

# logger.info("Test Complete")
