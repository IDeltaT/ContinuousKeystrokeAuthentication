from sklearn.utils import shuffle
from pynput import keyboard
from time import time
import numpy as np
import pickle
import h5py

# Hold time – время между нажатием и отпусканием клавиши (H).
# Keydown-Keydown time – время между нажатиями последовательных клавиш (DD).
# Keyup-Keydown time – время между отпусканием одной клавиши и нажатием следующей клавиши (UD).
# Полный вектор: (Key[1]ID, Key[2]ID, Key[1]H, Key[2]H, DD, UD)

class FeatureExtractor:
    ''' Экстрактор признаков '''
    
    
    def __init__(self, keys_required: int, models_path: str, current_user: str, sliding_window_size: int):
                   
        self.keys_required = keys_required # Количество клавиш, необходимых для остановки слушателя
        self.models_path = models_path     # Путь сохранения моделей
        self.current_user = current_user   # Имя текущего пользователя
        self.sliding_window_size = sliding_window_size  # Размер скользящего окна

        self.sliding_window_array = np.array([]) # Скользящее окно
        self.train_labels = np.array([])         # Массив с метками для обучения
        self.fetures_number = 6                  # Кол-во признаков в завершенном векторе
        
        self.start_times = np.zeros(254)
        self.start_typing = 0            # Время начала
        self.keys_hold_time = []  
        self.keys_down_down_time = []
        self.keys_up_down_time = [] 
        self.last_key_enterd_time = 0    # Расчет продолжительности между нажатиями клавиш
        self.virtual_keys_ID = []               
        self.keys_counter = 0        
        self.max_virtual_key = 254       # 0xFE - 'OEMCLEAR'       
        
     
    def on_press(self, key):
        ''' Действия, производимые при нажатии клавиши '''
        
        current_time = time() 

        if self.start_typing == 0:
            self.start_typing = current_time

        if self.last_key_enterd_time != 0:
            if hasattr(key, 'vk'): # Проверка виртуального атрибута
                if self.start_times[key.vk] == 0: # Рассчитывание Keydown-Keydown time
                    self.keys_down_down_time.append(current_time - self.last_key_enterd_time)
            elif self.start_times[key.value.vk] == 0:
                self.keys_down_down_time.append(current_time - self.last_key_enterd_time)
                
        self.last_key_enterd_time = current_time
        
        if hasattr(key, 'vk'):
            if self.start_times[key.vk] == 0:
                self.start_times[key.vk] = current_time
                self.virtual_keys_ID.append(key.vk)
        else:
            if self.start_times[key.value.vk] == 0:
                self.start_times[key.value.vk] = current_time 
                self.virtual_keys_ID.append(key.value.vk)
         
                
    def on_release(self, key):
        ''' Действия, производимые при отпускании клавиши '''
        
        current_time = time()
        
        self.keys_counter += 1
               
        if hasattr(key, 'vk'):
            start = self.start_times[key.vk]
            self.start_times[key.vk] = 0
            
        else: 
            start = self.start_times[key.value.vk]
            self.start_times[key.value.vk] = 0
        self.keys_hold_time.append(current_time - start)
        
        if self.keys_counter > self.keys_required:
            self.feature_preparation()          
            # Останвить прослушиватель
            return False
        

    def feature_preparation(self):
        ''' Подготовка признаков, с последующей сериализацией и сохранением в файл HDF '''
        
        keys_hold_time = np.array(self.keys_hold_time)
        keys_down_down_time = np.array(self.keys_down_down_time)
        
        try:
            keys_up_down_time = keys_down_down_time - keys_hold_time[:len(keys_hold_time) - 1]
        except:
            min_len = min(len(keys_down_down_time), len(keys_hold_time[:len(keys_hold_time) - 1]))
            keys_up_down_time = keys_down_down_time[:min_len] - keys_hold_time[:min_len]
            print('---- !!! Несоответствие длин массивов !!! ----')

        features = []
        
        # Подготовка веторов (Key[1]ID, Key[2]ID, Key[1]H, Key[2]H, DD, UD)
        for i in range(len(keys_hold_time) - 1):
            complete_vector = (self.virtual_keys_ID[i], self.virtual_keys_ID[i + 1], keys_hold_time[i],
                               keys_hold_time[i + 1], keys_down_down_time[i], keys_up_down_time[i])
            features.append(complete_vector)
        
        #print(features) # Отладка
        
        # Сериализация списка в файл
        self.save_list_to_file(features)
        #self.read_list_from_file()

        # Сохранение списка в HDF файл, использующийся для обучения модели
        self.save_list_to_hdf5(features)
        

    def save_list_to_file(self, list_to_save: list):
        ''' Сериализация списка в файл '''
        
        with open(f'{self.models_path}/{self.current_user}.lst', 'wb') as file:
            pickle.dump(list_to_save, file)
            print('Признаки успешно сохранены')       


    def read_list_from_file(self):
        ''' Десериализация списка из файла '''
        
        with open(f'{self.models_path}/{self.current_user}.lst', 'rb') as file:
            list_from_file = pickle.load(file)
            return list_from_file
    

    def save_list_to_hdf5(self, list_to_save: list):
        ''' Сохранение списка в файл формата HDF '''
        
        features_matrix = np.array(list_to_save)
        
        #print(features_matrix) # Отладка
        
        # Нормализация клавишных индексов (деление на общее кол-во)
        for i in range(0,len(features_matrix)):
            features_matrix[i][0] /= self.max_virtual_key
            features_matrix[i][1] /= self.max_virtual_key
            
        #print(features_matrix) # Отладка
        
        # Сбор данных скользящим окном 
        for i in range(features_matrix.shape[0] - self.sliding_window_size):
            
            # На каждой итерации массив пополняется на размер скользящего окна (30*6 = 180)
            # Кол во итераций: дляина массива признаков - длина скользящего окна: 40 - 30 = 10
            # Конечный массив одномерный: 180*10 = 1800
            self.sliding_window_array = np.append(self.sliding_window_array, 
                                                  features_matrix[i:i+self.sliding_window_size])

        print(np.shape(self.sliding_window_array)) # (1800,)        

        # Заполнение массива меток (1 - легальный пользователь системы)
        labels = np.empty(features_matrix.shape[0] - self.sliding_window_size)
        labels.fill(1)
        self.train_labels = np.append(self.train_labels, labels)
        
        print(np.shape(self.train_labels)) # (10,)
        
        # Конвертация массивов в размерности, необходимые для последующей передачи нейронной сети
        self.train_labels = self.train_labels.reshape(int(self.train_labels.shape[0]), 1)
        self.sliding_window_array = self.sliding_window_array.reshape(int(self.train_labels.shape[0]), 
                                                                      self.sliding_window_size,
                                                                      self.fetures_number)
        # Отладка      
        #print(self.train_labels)
        print(np.shape(self.train_labels)) # (10, 1)       
        #print(self.sliding_window_array)
        print(np.shape(self.sliding_window_array)) # (10, 30, 6)

        # Перемешать массивы
        self.sliding_window_array, self.train_labels = shuffle(self.sliding_window_array, self.train_labels)
        
        # Отладка
        #print(self.train_labels)
        print(np.shape(self.train_labels)) # (10, 1)        
        #print(self.sliding_window_array)
        print(np.shape(self.sliding_window_array)) # (10, 30, 6)

        # Сохранение данных для обучения моедели в файл формата HDF
        with h5py.File(f'{self.models_path}/{self.current_user}.h5','w') as hdf: 
            hdf.create_dataset('train_data',data = self.sliding_window_array)
            hdf.create_dataset('train_labels',data = self.train_labels)


if __name__ == '__main__':
    
    FE = FeatureExtractor() 
    
    with keyboard.Listener(on_press=FE.on_press, on_release=FE.on_release) as listener:
        listener.join()