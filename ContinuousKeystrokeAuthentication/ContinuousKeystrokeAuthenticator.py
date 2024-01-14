from tkinter.messagebox import showerror, showwarning, showinfo
from tensorflow import keras
from pynput import keyboard
from time import time
import numpy as np
import logging
import os


class ContinuousKeystrokeAuthenticator:
    ''' Непрерывный аутентификатор по клавиатурному почерку '''

    def __init__(self, app, models_path: str, current_user: str, sliding_window_size: int):

        self.app = app # Доступ к виджетам приложения
        
        self.models_path = models_path     # Путь, содержащий обученные модели
        self.current_user = current_user   # Имя текущего пользователя
        self.sliding_window_size = sliding_window_size  # Размер скользящего окна

        self.sliding_window_array = np.array([]) # Скользящее окно
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
        
        self.models_path = 'UserData/Models'
        self.model_prefix = 'Trained_Model_'
        self.model = keras.models.load_model(f'{self.models_path}/{self.model_prefix}{self.current_user}.h5')        
        
        # Прогрев модели :)
        features = np.zeros(180).reshape(1, 30, 6) # (1, 30, 6)
        prediction = self.model.predict(x=features, verbose=0)
        
        self.predictions_required = 20
        self.predictions = []   # Массив с предсказаниями обученной модели
        self.tolerance = 0.4    # Пороговое значение допуска аутентификации по клавиатурному почерку
        
        # Проверка на наличие папки 'Models'        
        is_exist = os.path.exists(self.models_path)
        if not is_exist:
            os.makedirs(self.models_path)
            showinfo(title='Предупреждение', message='Папка с моделями не обнаружена (Создана новая папка).')

        # Логирование
        self.logs_path = 'Logs'
        self.logs_file_name = 'logs'
        is_exist = os.path.exists(self.logs_path)
        if not is_exist:
            os.makedirs(self.logs_path)            
            showinfo(title='Предупреждение', message='Файлы логов не обнаружены.')
            
        logging.basicConfig(level=logging.INFO, 
                            filename=f'{self.logs_path}/{self.logs_file_name}.log', 
                            filemode='a',
                            format='- %(asctime)s %(message)s;')

    def on_press(self, key):
        ''' Действия, производимые при нажатии клавиши '''
        
        current_time = time() 

        if self.start_typing == 0:
            self.start_typing = current_time

        if self.last_key_enterd_time != 0:
            self.keys_down_down_time.append(current_time - self.last_key_enterd_time)                  
               
        self.last_key_enterd_time = current_time
        
        if hasattr(key, 'vk'):
            if self.start_times[key.vk] == 0:
                self.start_times[key.vk] = current_time
                self.virtual_keys_ID.append(key.vk/self.max_virtual_key)
        else:
            if self.start_times[key.value.vk] == 0:
                self.start_times[key.value.vk] = current_time 
                self.virtual_keys_ID.append(key.value.vk/self.max_virtual_key)
         
                
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
        
        # Если нажатых клавиш, больше скользящего окна
        if self.keys_counter > self.sliding_window_size:
            self.feature_preparation()                      
                          
            if len(self.predictions) > self.predictions_required:
                self.predictions = np.array(self.predictions)
                print(self.predictions)
                print(np.shape(self.predictions))
                mean = np.mean(self.predictions)
                print(f'mean: {mean}')
                self.predictions = []
                
                if mean > self.tolerance:
                    print('Легальный пользователь')
                else:
                    # Заблокировать рабочую станцию, если стоит соответствующий флаг
                    if (self.app.block_CheckBox_BooleanVar.get()):
                        self.app.lock_work_station()
                        
                    # Показать уведомление, если стоит соответствующий флаг
                    if (self.app.alert_CheckBox_BooleanVar.get()):
                        showwarning(title='Предупреждение', message='Обнаружен "Чужой" биометрический образ \
(потенциальный злоумышленик)') 

                    logging.info('Обнаружен "Чужой" биометрический образ (потенциальный злоумышленик)')
                    
                    # Останвить прослушиватель
                    return False  
    

    def feature_preparation(self):
        ''' Подготовка признаков '''
        
        index = self.keys_counter - (self.sliding_window_size + 1)
        print(index)
        
        keys_hold_time = np.array(self.keys_hold_time[index:self.keys_counter])
        keys_down_down_time = np.array(self.keys_down_down_time[index:self.keys_counter - 1])
        
        print(np.shape(keys_hold_time))
        print(np.shape(keys_down_down_time))

        try:
            keys_up_down_time = keys_down_down_time - keys_hold_time[:len(keys_hold_time) - 1]
            print('OK')
        except:
            min_len = min(len(keys_down_down_time), len(keys_hold_time[:len(keys_hold_time) - 1]))
            keys_up_down_time = keys_down_down_time[:min_len] - keys_hold_time[:min_len]
            print('-несоответствие длин массивов')
            
        features = []        
        
        # Подготовка веторов (Key[1]ID, Key[2]ID, Key[1]H, Key[2]H, DD, UD)
        for i in range(len(keys_up_down_time)):
            try:
                complete_vector = (self.virtual_keys_ID[i + index], 
                                   self.virtual_keys_ID[i + index + 1], 
                                   keys_hold_time[i],
                                   keys_hold_time[i + 1], 
                                   keys_down_down_time[i], 
                                   keys_up_down_time[i])
                features.append(complete_vector)
            except:
                print('-вектор не составлен')

        features = np.array(features)
        try:
            features = features.reshape(1, self.sliding_window_size, self.fetures_number) # (1, 30, 6)
            prediction = self.model.predict(x=features, verbose=0)
            print(prediction)
            self.predictions.append(prediction[0][1])
        except:
            pass


if __name__ == '__main__':
    
    CKA = ContinuousKeystrokeAuthenticator()     
    with keyboard.Listener(on_press=CKA.on_press, on_release=CKA.on_release) as listener:
        listener.join()