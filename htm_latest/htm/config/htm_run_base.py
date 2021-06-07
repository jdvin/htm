from htm.enums import PredictionType

run = dict(
    pattern_length = 8, #32
    pattern_iterations = 200,
    data_path='basic_training.csv',
    prediction_type = PredictionType.STEPS,
    prediction_steps = 8,
    prediction_threshold = 0
)

run['train_episodes'] = run['pattern_length'] * run['pattern_iterations']
