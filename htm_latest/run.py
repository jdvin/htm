import argparse
import logging
import os
from htm.encoder import ScalerEncoder, DiscreteEncoder
from importlib import import_module
from htm.factory import Factory
from htm.enums import PredictionType

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s\t=> %(message)s')
logger = logging.getLogger()
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# There are 5 logging levels
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL

logger.info("== Vinkan HTM Platform Version: 0.5 ==")

htm_factory = Factory(logger=logger)
logger.info("Successfully generated HTM factory instance")


# Parse arguments
parser = argparse.ArgumentParser(description='''
Main HTM initalisation file. 
Run this to kick off the whole process.
''')
parser.add_argument('config', 
                    type=str,
                    help='Config of choice')

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

# Create factory to spawn HTM instances
htm_factory.create_htm_instance("htm_test")
htm = htm_factory.instances[0]

#train instance
htm_factory.train_instance(config['run']['data_path'],
                            config['run']['train_episodes'], 
                            config['run']['pattern_length'], 
                            config['run']['prediction_type'],
                            config['run']['prediction_steps'],
                            config['run']['prediction_threshold'],
                            htm)

