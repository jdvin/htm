import pandas as pd
import numpy as np
from tensorflow.keras.utils import to_categorical

class Encoder:
    def __init__(self, input_size, data_file_path='data/training.csv'):
        self.input_size = input_size
        self.data_file_path = data_file_path
    
    def load_data(self):
        print(self.data_file_path)
        self.df = pd.read_csv(self.data_file_path, header=None)
        return self.df

class SimpleEncoder(Encoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_sample(self, index):
        sample = self.serialize_data(self.df.iloc[index])

        while True:
            for data in sample:
                yield data

    def serialize_data(self, sample):
        sample = np.array(sample.values)
        element_bucket_length = int(self.input_size / max(sample))
        categorical_sample = to_categorical(sample)
        serialized_sample = []

        for element in categorical_sample:
            index = np.argmax(element)
            padding_left = [0] * index * element_bucket_length
            element_padding = [1] * element_bucket_length
            padding_right = [0] * (len(element) - index - 1) * \
                element_bucket_length
            serialized_sample.append(padding_left + element_padding + padding_right)

        return serialized_sample

encoder = SimpleEncoder(20)
encoder.load_data()
gen = encoder.get_sample(0)

print(1, next(gen))
print(2, next(gen))
print(3, next(gen))