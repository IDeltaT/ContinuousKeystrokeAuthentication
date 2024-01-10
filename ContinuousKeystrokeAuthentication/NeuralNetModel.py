from sklearn.model_selection import validation_curve
from sklearn.utils import shuffle

from tensorflow.python.client import device_lib
from tensorflow import keras
import tensorflow as tf

from keras import layers
from keras.callbacks import LearningRateScheduler

import numpy as np
import math

import h5py

# import matplotlib.pyplot as plt

# Проверка графического ускорителя
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))
#sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))
#print(device_lib.list_local_devices())

class NeuralNetModel:
    
    def __init__(self, train_data: np.array, train_labels: np.array, models_path: str, current_user: str):
        
        self.train_data = train_data
        self.train_labels = train_labels
        self.models_path = models_path
        self.current_user = current_user

        self.input_shape = (30, 6)
        self.epochs = 100       # Оптимальное кол-во эпох (До насыщения)
        self.batch_size = 32    # Оптимальный размер пакета
        
        # ----------- МОДЕЛЬ НЕЙРОННОЙ СЕТИ ----------- #
        # Сверточный Слой -> LSTM -> Прореживание (0.5) -> LSTM -> Прореживание (0.5) -> Плотно Связанный Слой
        self.model = keras.models.Sequential()
        self.model.add(layers.Conv1D(32, 2, activation='relu', input_shape=self.input_shape))
        self.model.add(layers.LSTM(32 , return_sequences=True))
        self.model.add(layers.Dropout(0.5))
        self.model.add(layers.LSTM(32, return_sequences=True))
        self.model.add(layers.Dropout(0.5))
        self.model.add(layers.Flatten())
        self.model.add(layers.Dense(2, activation='softmax'))
        
        # Параметры результирующей модели
        #print(self.model.summary())
    
        # Оптимизатор Адама лучше всего подходит для работы по классификации.
        # Скорость обучения равна 0, т.к используется кастомный сценарий обучения.
        self.loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        self.optimizer = keras.optimizers.Adam(learning_rate=0.0)
        self.metrics = ['accuracy']

        self.model.compile(loss=self.loss, optimizer=self.optimizer, metrics=self.metrics)
        
        self.lrate = LearningRateScheduler(NeuralNetModel.step_decay)
        self.callbacks_list = [self.lrate]
        

    def train_model(self):
        with tf.device('/device:GPU:0'):
            self.model.fit(self.train_data, 
                           self.train_labels, 
                           batch_size=self.batch_size, 
                           validation_split=0.1, 
                           callbacks=self.callbacks_list, 
                           epochs=self.epochs, 
                           shuffle=True)
            

    def save_model(self):
        self.model.save(f'{self.models_path}/Trained_Model_{self.current_user}.h5')
        

    @staticmethod
    def step_decay(epoch):
        initial_lrate = 0.0001
        drop = 0.1
        epochs_drop = 100.0
        lrate = initial_lrate*math.pow(drop, math.floor((1 + epoch)/epochs_drop))
        return lrate
