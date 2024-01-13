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


