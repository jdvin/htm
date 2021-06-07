import argparse
import logging
import os
from htm.encoder import ScalerEncoder, DiscreteEncoder

from importlib import import_module

from htm.factory import Factory

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s\t=> %(message)s')
logger = logging.getLogger()
if logger.hasHandlers(): logger.handlers.clear()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# There are 5 logging levels
# DEBUG
# INFO
# WARNING
# ERROR
# CRITICAL

def main():
    '''
    Main initialisation method.
    Will start simulation etc.
    '''

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
    logger.setLevel(config['run']['logging_level'])

    #Simulation Logic

    # Create factory to spawn HTM instances
    htm_factory = Factory(logger=logger,
                          config=config)
    htm_factory.create_htm_instance(ScalerEncoder)
    htm = htm_factory.instances[0]

    logger.info("Beginning Test...")

    current_sample = 0
    sample_length = 6000
    logger.info("Beginning Spatial Pooling...")
    while True:
        htm.spatial_pool(next(htm.element_generator))
        htm.encoder_classifier[htm.encoder.sample_classifier[current_sample-1]] = htm.sdr_snapshot()

        current_sample += 1
        
        if current_sample % int(6000/10) == 0:
            logger.info(f"Spatial Pooling {int(100 * (current_sample/6000))}% Complete")
        

        if current_sample == 6000:
            logger.info("Spatial Pooling Complete")
            break

    logger.info("Getting Boost Values...")
    boost_values = []
    for column in htm.columns:
        boost_values.append(column.boost)
    logger.info(boost_values)

    logger.debug("Calculating Overlaps with 0.500...")
    overlaps = []
    for ip in htm.encoder_classifier:
        overlaps.append(htm_factory.sdr_percent_overlap(htm.encoder_classifier[0.500], htm.encoder_classifier[ip]))
    logger.info(overlaps)
    
    logger.info("Test Complete!")
   
if __name__ == '__main__':
    main()
