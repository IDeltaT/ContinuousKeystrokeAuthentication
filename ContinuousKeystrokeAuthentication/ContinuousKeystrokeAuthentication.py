﻿import tkinter as TK
from PIL import Image
import customtkinter as CTk
from transitions import Machine

    

class StateMachine:
    

    # Возможные состояния программы:
    # 1. password_authorization - Базовая авторизация (Ввод: имя пользователя/пароль);
    # 2. registration - Регистрация нового пользователя (Ввод: имя пользователя/пароль);
    # 3. keystroke_authorization - Аутентификация по клавиатурному почерку 
    #    (Ввод: произвольный текст/ответы на вопросы/заданный текст);
    # 4. keystroke_extract - Извлечение пользовательского ритма нажатия клавиш, 
    #    для последующего обучения икуственной нейронной сети 
    #    (Ввод: произвольный текст/ответы на вопросы/заданный текст);
    # 5. user_profile - Профиль польователя. Возможности: поменять пароль, выйти из системы,
    #    сбросить обученную модель, удалить профиль, выбрать действия при обнаружении нарушителя,
    #    изменить допустимое отклонение, включить/выключить непрерывную аутентификацию.

    states = ['password_authorization', 'registration', 'keystroke_authorization', 
              'keystroke_extract','user_profile']


    transitions = [{ 'trigger': 'switch_to_password_authorization', 
                     'source': '*', 
                     'dest': 'password_authorization', 
                     'after': 'display_password_authorization'},

                   { 'trigger': 'switch_to_registration', 
                     'source': ['password_authorization', 'registration'], # !!!!
                     'dest': 'registration',
                     'after': 'display_registration'},

                   { 'trigger': 'switch_to_keystroke_authorization', 
                     'source': ['password_authorization', 'keystroke_authorization'], # !!!!
                     'dest': 'keystroke_authorization',
                     'after': 'display_keystroke_authorization'},
                     
                   { 'trigger': 'switch_to_keystroke_extract', 
                     'source': 'registration', 
                     'dest': 'keystroke_extract',
                     'after': 'display_keystroke_extract'},

                   { 'trigger': 'switch_to_user_profile', 
                     'source': ['keystroke_authorization', 'keystroke_extract'], 
                     'dest': 'user_profile',
                     'after':'display_user_profile'}]  

    def __init__(self):
        self.frames = {'password_authorization_frame': 0,
                       'registration_frame': 0}
                

    def frames_setter(self, frame_name: str, frame):
        if frame_name in self.frames.keys():
            self.frames[frame_name] = frame
        else:
            print('Попытка добавить несуществующий фрейм!')


    def forget_all_frames(self):
        for frame in self.frames.values():
            frame.grid_forget()
    

    def display_password_authorization(self):
        print("display_password_authorization")
        self.forget_all_frames()
        
        self.frames['password_authorization_frame'].grid(row=0, column=0, sticky='ns')


    def display_registration(self):
        print("display_registration")
        
        self.forget_all_frames()
        
        self.frames['registration_frame'].grid(row=0, column=0, sticky='ns')
            

    def display_keystroke_authorization(self):
        print("display_keystroke_authorization")      
    
        
    def display_keystroke_extract(self):
        print("display_keystroke_extract")
            

    def display_user_profile(self):
        print("display_user_profile")      



class App(CTk.CTk):
    
    # Размеры окна (В пикселях)
    WIDTH = 900
    HEIGHT = 600

    
    CTk.set_appearance_mode("dark")         # Тема приложения по умолчанию: Темная
    CTk.set_default_color_theme("green")    # Цветовая тема приложения по умолчанию: Зеленая
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        # Инициализация машины состояний
        self.state_machine = StateMachine()
        self.machine = Machine(model = self.state_machine, 
                               states = StateMachine.states, 
                               transitions = StateMachine.transitions, 
                               initial = 'password_authorization')
        
        #print(self.state_machine.state)
        #state_machine.switch_to_registration()
        #print(state_machine.state)

        
        self.title('Программное средство аутентификации пользователя на основе клавиатурного почерка')
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}') # Ширина и Высота окна
        self.resizable(False, False) # Запрет на изменение размеров окна
        self.iconbitmap('images/Icon_Key_Lock.ico') # Иконка программы
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --------------------------------- password authorization frame ---------------------------------- #
        # Загрузка и установка заднего фона
        self.bg_image = CTk.CTkImage(Image.open('images/bg_gradient.jpg'), size=(self.WIDTH, self.HEIGHT))
        self.bg_image_label = CTk.CTkLabel(self, text='', image=self.bg_image)
        self.bg_image_label.grid(row=0, column=0)
        
        # Название программного средства
        program_name = 'ПРОГРАММНОЕ\nСРЕДСТВО\nБИОМЕТРИЧЕСКОЙ\nАУТЕНТИФИКАЦИИ\nНА ОСНОВЕ\nКЛАВИАТУРНОГО\nПОЧЕРКА'
        
        # Создание фрейма окна авторизации
        self.password_authorization_frame = CTk.CTkFrame(self, corner_radius=0)
        self.password_authorization_frame.grid(row=0, column=0, sticky='ns')

        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('password_authorization_frame', self.password_authorization_frame)

        # Отображение названия программы (Label)
        self.program_name_label = CTk.CTkLabel(self.password_authorization_frame, text=program_name, 
                                               font=CTk.CTkFont(size=20, weight='bold'))
        self.program_name_label.grid(row=0, column=0, padx=30, pady=(60, 15))
        
        # Лейбл: "Авторизация"
        self.authorization_label = CTk.CTkLabel(self.password_authorization_frame, text='АВТОРИЗАЦИЯ', 
                                                font=CTk.CTkFont(size=20, weight='bold'))
        self.authorization_label.grid(row=1, column=0, padx=30, pady=(40, 15))
  
        # Поле для ввода логина
        self.username_entry = CTk.CTkEntry(self.password_authorization_frame, width=200, 
                                           placeholder_text='Имя пользователя')
        self.username_entry.grid(row=2, column=0, padx=30, pady=(15, 15))
        
        # Поле для ввода пароля
        self.password_entry = CTk.CTkEntry(self.password_authorization_frame, width=200, show='*', 
                                           placeholder_text='Пароль')
        self.password_entry.grid(row=3, column=0, padx=30, pady=(0, 15))
        
        # Кнопка: "Войти"
        self.login_button = CTk.CTkButton(self.password_authorization_frame, text='Войти', 
                                          command=self.login_event, width=200)
        self.login_button.grid(row=4, column=0, padx=30, pady=(10, 10))
        
        # Кнопка: "Регистрация"
        self.to_registration_frame_button = CTk.CTkButton(self.password_authorization_frame, 
                                                          text='Регистрация', 
                                                          command=self.state_machine.switch_to_registration,
                                                          width=200)
        self.to_registration_frame_button.grid(row=5, column=0, padx=30, pady=(10, 10))

        #self.password_authorization_frame.grid_forget() # Забыть фрейм
        #self.password_authorization_frame.grid(row=0, column=0, sticky='ns') # Разместить фрейм


        # -------------------------------------- registration frame --------------------------------------- #

        # Создание фрейма окна регистрации
        self.registration_frame = CTk.CTkFrame(self, corner_radius=0)
        #self.registration_frame.grid(row=0, column=0, sticky='ns')

        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('registration_frame', self.registration_frame)
       
        # Лейбл: "Регистрация"
        self.program_name_label = CTk.CTkLabel(self.registration_frame, text='РЕГИСТРАЦИЯ', 
                                               font=CTk.CTkFont(size=20, weight='bold'))
        self.program_name_label.grid(row=0, column=0, padx=30, pady=(200, 15))
   
        # Поле для ввода логина
        self.registration_username_entry = CTk.CTkEntry(self.registration_frame, width=200, 
                                                        placeholder_text='Имя пользователя')
        self.registration_username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        
        # Поле для ввода пароля
        self.registration_password_entry = CTk.CTkEntry(self.registration_frame, width=200, 
                                                        placeholder_text='Пароль')
        self.registration_password_entry.grid(row=2, column=0, padx=30, pady=(0, 15))

        # Кнопка: "Зарегистрироваться"
        self.registration_button = CTk.CTkButton(self.registration_frame, text='Зарегистрироваться', 
                                                 command=self.login_event, width=200)
        self.registration_button.grid(row=3, column=0, padx=30, pady=(10, 10))
        
        
        # Кнопка: "Авторизация"
        self.to_authorization_frame_button = CTk.CTkButton(self.registration_frame, 
                                                           text='Авторизация', 
                                                           command=self.state_machine.switch_to_password_authorization, 
                                                           width=200)
        
        self.to_authorization_frame_button.grid(row=4, column=0, padx=30, pady=(30, 10))


    def login_event(self):
        "Заглушка"
        pass


def main():
    app = App()
    app.mainloop()


    

if __name__ == '__main__':
    main()