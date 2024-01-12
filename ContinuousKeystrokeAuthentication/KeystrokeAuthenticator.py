from tkinter.messagebox import showerror, showwarning, showinfo
from tensorflow import keras
from pynput import keyboard
from time import time
import numpy as np
import os


# Hold time – время между нажатием и отпусканием клавиши (H).
# Keydown-Keydown time – время между нажатиями последовательных клавиш (DD).
# Keyup-Keydown time – время между отпусканием одной клавиши и нажатием следующей клавиши (UD).
# Полный вектор: (Key[1]ID, Key[2]ID, Key[1]H, Key[2]H, DD, UD)


class KeystrokeAuthenticator:
    ''' Аутентификатор по клавиатурному почерку '''
    
    def __init__(self, app, keys_required: int, models_path: str, current_user: str, sliding_window_size: int):

        self.app = app # Доступ к виджетам приложения
        
        self.keys_required = keys_required # Количество клавиш, необходимых для остановки слушателя
        self.models_path = models_path     # Путь, содержащий обученные модели
        self.current_user = current_user   # Имя текущего пользователя
        self.sliding_window_size = sliding_window_size  # Размер скользящего окна

        self.sliding_window_array = np.array([]) # Скользящее окно
        
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
        
        # Проверка на наличие папки 'Models'        
        is_exist = os.path.exists(self.models_path)
        if not is_exist:
            os.makedirs(self.models_path)
            showinfo(title='Предупреждение', message='Папка с моделями не обнаружена (Создана новая папка).')
            

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
            #self.feature_preparation()          
            # Останвить прослушиватель
            return False