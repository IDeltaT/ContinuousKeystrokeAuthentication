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

# Проверка графического ускорителя
print('Доступных графических процессоров: ', len(tf.config.list_physical_devices('GPU')))
#sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))
#print(device_lib.list_local_devices())

class NeuralNetModel:
    
    def __init__(self, train_data: np.array, train_labels: np.array, models_path: str, current_user: str):
        
        self.train_data = train_data
        self.train_labels = train_labels
        self.models_path = models_path
        self.current_user = current_user

        self.input_shape = (30, 6)
        self.epochs = 40        # Оптимальное кол-во эпох (До насыщения)
        self.batch_size = 32    # Оптимальный размер пакета
        
        self.enemy_dataset = 'TemplateSlidingWindow30'
        
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
        

    def prepear_data(self):
        ''' Подготовить данные для обучения модели '''
        
        # Для обучения из заданного файла с данными
        #self.train_data, self.train_labels = NeuralNetModel.open_hdf5_file('IKSuser')
        
        self.test_data = self.train_data[:100]
        self.test_labels = self.train_labels[:100]
        
        self.train_data = self.train_data[100:]
        self.train_labels = self.train_labels[100:]

        # Отладка
        print(np.shape(self.test_data))      # (x, 30, 6)
        print(np.shape(self.test_labels))    # (x, 1)

        print(np.shape(self.train_data))     # (x, 30, 6)
        print(np.shape(self.train_labels))   # (x, 1)
        
        # Примесь данных других пользователей с нулевой меткой (buffalo)
        self.train_data_enemy, self.train_labels_enemy = NeuralNetModel.open_hdf5_file(self.enemy_dataset)
        self.train_data_enemy = self.train_data_enemy[:np.shape(self.train_data)[0]]
        self.train_labels_enemy = np.zeros(np.shape(self.train_data)[0])
        self.train_labels_enemy.reshape(int(self.train_labels_enemy.shape[0]), 1)
        
        # Отладка
        print(self.train_labels_enemy)          # [0. 0. 0. ... 0. 0. 0.]
        print(self.train_data_enemy)            # 
        print(np.shape(self.train_data_enemy))  # (x, 30, 6)
        
        self.train_data = np.concatenate((self.train_data, self.train_data_enemy))
        print(np.shape(self.train_data))    # (x, 30, 6)
        
        self.train_labels = np.append(self.train_labels, self.train_labels_enemy)
        print(np.shape(self.train_labels))  # (x, 1)
        
        self.train_labels.reshape(len(self.train_labels), 1)
        
        # Отладка
        print(np.shape(self.train_labels)) # (x, 1)      
        print(self.train_labels) # [1. 1. 1. ... 0. 0. 0.]

        # Перемешать массивы
        self.train_data, self.train_labels = shuffle(self.train_data, self.train_labels)
        self.train_labels.reshape(len(self.train_labels), 1)
        
        # Отладка
        print(np.shape(self.train_data))     # (x, 30, 6)
        print(np.shape(self.train_labels))   # (x, 1)      
        print(self.train_data)      #
        print(self.train_labels)    # [1. 0. 1. ... 0. 1. 1.]
        

    def train_model(self):
        ''' Начать обучение модели '''
        
        with tf.device('/device:GPU:0'):
            self.model.fit(self.train_data, 
                           self.train_labels, 
                           batch_size=self.batch_size, 
                           validation_split=0.1, 
                           callbacks=self.callbacks_list, 
                           epochs=self.epochs, 
                           shuffle=True)
            

    def save_model(self):
        ''' Сохранить обученную модель '''
        
        self.model.save(f'{self.models_path}/Trained_Model_{self.current_user}.h5')


    def evaluation(self):
        ''' Протестировать обученную модель '''
        
        # Дополнительная проверка на другом наборе данных
        train_data_other, train_labels_other = NeuralNetModel.open_hdf5_file('2000char')
 
        # Метка: 1
        self.model.evaluate(self.test_data, self.test_labels, batch_size=self.batch_size, verbose=1)
        
        probability_model = keras.models.Sequential([self.model, keras.layers.Softmax()])        
        
        predictions = probability_model(self.test_data)
        prediction = predictions[0]
        result = np.argmax(prediction)
        print(f'{prediction}: {result}')
        
        print('---------------')
        
        # Метка: 0
        self.model.evaluate(self.train_data_enemy[:100], 
                            self.train_labels_enemy[:100], 
                            batch_size=self.batch_size, 
                            verbose=1)

        probability_model = keras.models.Sequential([self.model, keras.layers.Softmax()])        
        
        predictions = probability_model(self.train_data_enemy[:100])

        predictions = probability_model(self.test_data)
        prediction = predictions[0]
        result = np.argmax(prediction)
        print(f'{prediction}: {result}')
        
        print('---------------')
        
        # Метка: 1
        test_vec = self.test_data[1:2]
        print(np.shape(test_vec))   # (1, 30, 6)
        predictions = self.model.predict(x=test_vec,verbose=1)
        print(predictions) # [[0.03280104 0.967199]]

        # Метка: 0
        test_vec = train_data_other[1:2]
        predictions = self.model.predict(x=test_vec,verbose=1)
        print(predictions) # [[1.000000e+00 2.599879e-12]]      
        
        # Метка: 0       
        test_vec = self.train_data_enemy[1:2]
        predictions = self.model.predict(x=test_vec,verbose=1)
        print(predictions) # [[9.9996126e-01 3.8720547e-05]]  
        

    def concatinate_HDF_files(self):
        ''' Вспомогательный метод - объединение нескольких HDF-файлов'''
        
        train_data, train_labels = NeuralNetModel.open_hdf5_file('IKs_001')
        
        train_data3, train_labels3 = NeuralNetModel.open_hdf5_file('IKs_003')

        train_data5, train_labels5 = NeuralNetModel.open_hdf5_file('IKs_003')
        
        train_data = np.concatenate((train_data, train_data3))
        train_data = np.concatenate((train_data, train_data5))
        
        print(np.shape(train_data))
        print(train_data)
        
        train_labels = np.append(train_labels, train_labels3)
        train_labels = np.append(train_labels, train_labels5)
        
        print(np.shape(train_labels))
        print(train_labels)   
        
        # Сохранение данных для обучения моедели в файл формата HDF
        with h5py.File(f'{self.models_path}/IKSuser.h5','w') as hdf: 
            hdf.create_dataset('train_data', data = train_data)
            hdf.create_dataset('train_labels', data = train_labels)
            

    @staticmethod        
    def step_decay(epoch):
        ''' Ступенчатое затухание '''
        
        initial_lrate = 0.0001
        drop = 0.1
        epochs_drop = 100.0
        lrate = initial_lrate*math.pow(drop, math.floor((1 + epoch)/epochs_drop))
        return lrate
    

    @staticmethod
    def open_hdf5_file(file_name):
        ''' Считать данные из HDF5 файла '''
        
        with h5py.File(f'UserData/Models/{file_name}.h5','r') as hdf:
            data = hdf.get('train_data')
            train_data = np.array(data)
            data = hdf.get('train_labels')
            train_labels = np.array(data)
        return (train_data, train_labels)