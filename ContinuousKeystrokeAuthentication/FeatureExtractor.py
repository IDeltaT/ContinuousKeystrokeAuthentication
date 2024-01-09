from pynput import keyboard
from time import time
import numpy as np
import pickle

# Hold time – время между нажатием и отпусканием клавиши (H).
# Keydown-Keydown time – время между нажатиями последовательных клавиш (DD).
# Keyup-Keydown time – время между отпусканием одной клавиши и нажатием следующей клавиши (UD).
# Полный вектор: (Key[1]ID, Key[2]ID, Key[1]H, Key[2]H, DD, UD)

class FeatureExtractor:
    ''' Экстрактор признаков '''
    
    
    def __init__(self, keys_required: int, models_path: str, current_user: str):
                         
        self.keys_required = keys_required # Количество клавиш, необходимых для остановки слушателя
        self.start_times = np.zeros(254)
        self.start_typing = 0            # Время начала
        self.keys_hold_time = []  
        self.keys_down_down_time = []
        self.keys_up_down_time = [] 
        self.last_key_enterd_time = 0    # Расчет продолжительности между нажатиями клавиш
        self.virtual_keys_ID = []               
        self.keys_counter = 0
        self.models_path = models_path   # Путь сохранения моделей
        self.current_user = current_user # Имя текущего пользователя
        

    def on_press(self,key):

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
        
        if key == keyboard.Key.esc: # -------------------- !Убрать! --------------------
            # Останвить прослушиватель при нажатии клавиши 'esc'
            return False
        

    def feature_preparation(self):
        keys_hold_time = np.array(self.keys_hold_time)
        keys_down_down_time = np.array(self.keys_down_down_time)
        
        try:
            keys_up_down_time = keys_down_down_time - keys_hold_time[:len(keys_hold_time) - 1]
        except:
            min_len = min(len(keys_down_down_time), len(keys_hold_time[:len(keys_hold_time) - 1]))
            keys_up_down_time = keys_down_down_time[:min_len] - keys_hold_time[:min_len]
            print('---- !!! Diff shape !!! ----')

        features = []
            
        for i in range(len(keys_hold_time) - 1):
            complete_vector = (self.virtual_keys_ID[i], self.virtual_keys_ID[i + 1], keys_hold_time[i],
                               keys_hold_time[i + 1], keys_down_down_time[i], keys_up_down_time[i])
            features.append(complete_vector)
        
        print(features)
        
        self.save_list_to_file(features)
        self.read_list_from_file()
        

    def save_list_to_file(self, list_to_save):
        ''' Сериализация списка в файл '''
        
        with open(f'{self.models_path}/{self.current_user}.lst', 'wb') as file:
            pickle.dump(list_to_save, file)
            print('Признаки успешно сохранены')       


    def read_list_from_file(self):
        ''' Десериализация списка из файла '''
        
        with open(f'{self.models_path}/{self.current_user}.lst', 'rb') as file:
            n_list = pickle.load(file)
            print(n_list)
            return n_list
    

if __name__ == '__main__':
    
    FE = FeatureExtractor() 
    
    with keyboard.Listener(on_press=FE.on_press, on_release=FE.on_release) as listener:
        listener.join()