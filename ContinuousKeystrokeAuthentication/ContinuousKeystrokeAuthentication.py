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
                       'registration_frame': 0,
                       'keystroke_authorization_frame': 0,
                       'keystroke_extract_frame': 0,
                       'user_profile_frame': 0}
                

    def frames_setter(self, frame_name: str, frame):
        if frame_name in self.frames.keys():
            self.frames[frame_name] = frame
        else:
            print('Попытка добавить несуществующий фрейм!')


    def forget_all_frames(self):
        for frame in self.frames.values():
            frame.grid_forget()
    

    def display_password_authorization(self):
        print('display_password_authorization')
        self.forget_all_frames()
        
        self.frames['password_authorization_frame'].grid(row=0, column=0, sticky='ns')


    def display_registration(self):
        print('display_registration')
        
        self.forget_all_frames()
        
        self.frames['registration_frame'].grid(row=0, column=0, sticky='ns')
            

    def display_keystroke_authorization(self):
        print('display_keystroke_authorization')      
        self.characters_counter = 0 # Сбросить кол-во введенных символов
        
        self.forget_all_frames()        

        self.frames['keystroke_authorization_frame'].grid(row=0, column=0, sticky='ns')

        
    def display_keystroke_extract(self):
        print('display_keystroke_extract')
        self.characters_counter = 0 # Сбросить кол-во введенных символов
        
        self.forget_all_frames()
        
        self.frames['keystroke_extract_frame'].grid(row=0, column=0, sticky='ns')


    def display_user_profile(self):
        print('display_user_profile')  
        
        self.forget_all_frames()

        self.frames['user_profile_frame'].grid(row=0, column=0, sticky='ns')



class App(CTk.CTk):
    
    # Размеры окна (В пикселях)
    WIDTH = 900
    HEIGHT = 600
    
    CTk.set_appearance_mode('dark')         # Тема приложения по умолчанию: Темная
    CTk.set_default_color_theme('green')    # Цветовая тема приложения по умолчанию: Зеленая
    


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

        # Инициализация машины состояний
        self.state_machine = StateMachine()
        self.machine = Machine(model = self.state_machine, 
                               states = StateMachine.states, 
                               transitions = StateMachine.transitions, 
                               initial = 'password_authorization')

        # Вопросы, для прохождения биометрической аутентификации по клавиатурному почерку
        self.questions = {1: 'Чем вы любите заниматься в свободное время?',
                          2: 'Что вам больше нравится: искусство, музыка, спорт или театр? И почему?',
                          3: 'Опишите вид активного отдыха, которым вы любите заниматься.',
                          4: 'Чувствуете ли вы себя комфортно и почему?',
                          5: 'Кем Вы видите себя через пять лет?',
                          6: 'Опишите ваше домашнее животное.',
                          7: 'Опишите помещение, в котором Вы сейчас находитесь',}
        
        self.current_question = 0
        self.questions_number = len(self.questions)

        self.characters_counter = 0      
        self.authentication_required_characters = 20
        self.registration_required_characters = 200

        self.title('Программное средство аутентификации пользователя на основе клавиатурного почерка')
        self.geometry(f'{self.WIDTH}x{self.HEIGHT}') # Ширина и Высота окна
        self.resizable(False, False) # Запрет на изменение размеров окна
        self.iconbitmap('images/Icon_Key_Lock.ico') # Иконка программы
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        self.current_user = 'IKSuser'

        self.alert_CheckBox_BooleanVar = CTk.BooleanVar()
        self.alert_CheckBox_BooleanVar.set(True)
        
        self.block_CheckBox_BooleanVar = CTk.BooleanVar()
        self.block_CheckBox_BooleanVar.set(True)
        
        self.ContAuth_Switch_BooleanVar = CTk.BooleanVar()
        self.ContAuth_Switch_BooleanVar.set(True)
        
        
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

        # Label: Отображение названия программы
        self.program_name_label = CTk.CTkLabel(self.password_authorization_frame, 
                                               text=program_name, 
                                               font=CTk.CTkFont(size=20, weight='bold'))
        self.program_name_label.grid(row=0, column=0, padx=30, pady=(40, 15))
        
        # Label: "Авторизация"
        self.authorization_label = CTk.CTkLabel(self.password_authorization_frame, 
                                                text='АВТОРИЗАЦИЯ', 
                                                font=CTk.CTkFont(size=20, weight='bold'))
        self.authorization_label.grid(row=1, column=0, padx=30, pady=(40, 10))
  
        # Entry: Поле для ввода логина
        self.username_entry = CTk.CTkEntry(self.password_authorization_frame, 
                                           width=200, 
                                           placeholder_text='Имя пользователя')
        self.username_entry.grid(row=2, column=0, padx=30, pady=(10, 15))
        
        # Entry: Поле для ввода пароля
        self.password_entry = CTk.CTkEntry(self.password_authorization_frame, 
                                           width=200, 
                                           show='*', 
                                           placeholder_text='Пароль')
        self.password_entry.grid(row=3, column=0, padx=30, pady=(0, 15))
        
        # Button: "Войти"
        self.login_button = CTk.CTkButton(self.password_authorization_frame, 
                                          text='войти', 
                                          command=self.state_machine.switch_to_keystroke_authorization, 
                                          width=200,
                                          font=CTk.CTkFont(size=14, weight='bold'))
        self.login_button.grid(row=4, column=0, padx=30, pady=(10, 10))
        
        # Button: "Регистрация"
        self.PassAuth_to_Reg_frame_button = CTk.CTkButton(self.password_authorization_frame, 
                                                          text='регистрация', 
                                                          command=self.state_machine.switch_to_registration,
                                                          width=200,
                                                          font=CTk.CTkFont(size=14, weight='bold'))
        self.PassAuth_to_Reg_frame_button.grid(row=5, column=0, padx=30, pady=(10, 10))


        # -------------------------------------- registration frame --------------------------------------- #

        # Создание фрейма окна регистрации
        self.registration_frame = CTk.CTkFrame(self, corner_radius=0)
        #self.registration_frame.grid(row=0, column=0, sticky='ns')

        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('registration_frame', self.registration_frame)
       
        # Label: "Регистрация"
        self.registration_frame_name_label = CTk.CTkLabel(self.registration_frame, 
                                                          text='РЕГИСТРАЦИЯ\nНОВОГО\nПОЛЬЗОВАТЕЛЯ', 
                                                          font=CTk.CTkFont(size=20, weight='bold'))
        self.registration_frame_name_label.grid(row=0, column=0, padx=30, pady=(170, 15))
   
        # Entry: Поле для ввода логина
        self.registration_username_entry = CTk.CTkEntry(self.registration_frame, 
                                                        width=200, 
                                                        placeholder_text='Имя пользователя')
        self.registration_username_entry.grid(row=1, column=0, padx=30, pady=(15, 15))
        
        # Entry: Поле для ввода пароля
        self.registration_password_entry = CTk.CTkEntry(self.registration_frame, 
                                                        width=200, 
                                                        placeholder_text='Пароль')
        self.registration_password_entry.grid(row=2, column=0, padx=30, pady=(0, 10))

        # Button: "Зарегистрироваться"
        self.registration_button = CTk.CTkButton(self.registration_frame, 
                                                 text='зарегистрироваться', 
                                                 command=self.state_machine.switch_to_keystroke_extract, 
                                                 width=200,
                                                 font=CTk.CTkFont(size=14, weight='bold'))
        self.registration_button.grid(row=3, column=0, padx=30, pady=(5, 10))
        
        
        # Button: "Авторизация"
        self.Reg_to_PassAuth_frame_button = CTk.CTkButton(self.registration_frame, 
                                                          text='авторизация', 
                                                          command=self.state_machine.switch_to_password_authorization, 
                                                          width=200,
                                                          font=CTk.CTkFont(size=14, weight='bold'))      
        self.Reg_to_PassAuth_frame_button.grid(row=4, column=0, padx=30, pady=(30, 10))


        # --------------------------------- keystroke authorization frame --------------------------------- #

        # Создание фрейма окна авторизации по клавиатурному почерку
        self.keystroke_authorization_frame = CTk.CTkFrame(self, corner_radius=0)
        #self.keystroke_authorization_frame.grid(row=0, column=0, sticky='ns')

        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('keystroke_authorization_frame', self.keystroke_authorization_frame)
        
        KeyAuth_frame_name_text = 'АУТЕНТИФИКАЦИЯ ПО КЛАВИАТУРНОМУ ПОЧЕРКУ'
        # Label: "Аутентификация по клавиатурному почерку"
        self.keystroke_authorization_frame_name_label = CTk.CTkLabel(self.keystroke_authorization_frame, 
                                                                     text=KeyAuth_frame_name_text, 
                                                                     font=CTk.CTkFont(size=20, weight='bold'))
        self.keystroke_authorization_frame_name_label.grid(row=0, column=0, padx=30, pady=(20, 10))

        KeyAuth_frame_instruction_text = 'для успешного прохождения данного этапа аутентификации,\n\
посторайтесь дать развернутые ответы на поставленные вопросы\n(при необходимости, можно заменить вопрос)\n\n\
ВОПРОСЫ:'
        # Label: Инструкция прохождения биометрической аутентификации по клавиатурному почерку
        self.KeyAuth_instruction_label = CTk.CTkLabel(self.keystroke_authorization_frame, 
                                                      text=KeyAuth_frame_instruction_text, 
                                                      font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyAuth_instruction_label.grid(row=1, column=0, padx=30, pady=(10, 5))

        # TextBox: Содержит вопросы
        self.KeyAuth_questions_textbox = CTk.CTkTextbox(self.keystroke_authorization_frame, 
                                                        width=500, 
                                                        height=100,
                                                        wrap=CTk.WORD,
                                                        font=CTk.CTkFont(size=16, weight='bold'))
        self.KeyAuth_questions_textbox.grid(row=2, column=0, padx=(20, 20), pady=(5, 0))
        # Отчистка TextBox'а
        self.KeyAuth_questions_textbox.delete('1.0', CTk.END)
        # Вставка вопроса в TextBox
        self.KeyAuth_questions_textbox.insert('0.0', f'{self.questions[self.current_question + 1]}')
        self.KeyAuth_questions_textbox.configure(state='disabled') # Деактивировать TextBox


        # Создание фрейма, содержащего элементы управления перелистывания вопросов
        self.KeyAuth_question_control_frame = CTk.CTkFrame(self.keystroke_authorization_frame, 
                                                           corner_radius=0,
                                                           fg_color='transparent')
        self.KeyAuth_question_control_frame.grid(row=3, column=0, padx=0, pady=(3, 10))
        
        # Button: "<" Предыдущий вопрос
        args = lambda: self.display_previous_question(self.KeyAuth_question_counter_label, self.KeyAuth_questions_textbox)
        self.previous_question_button = CTk.CTkButton(self.KeyAuth_question_control_frame, 
                                                      text='<', 
                                                      command=args,
                                                      width=30,
                                                      font=CTk.CTkFont(size=20, weight='bold'))
        self.previous_question_button.grid(row=0, column=0, padx=5, pady=(3, 5))
        
        # Label: Текущий вопрос / Всего вопросов
        self.KeyAuth_question_counter_label = CTk.CTkLabel(self.KeyAuth_question_control_frame, 
                                                           text=f'{self.current_question + 1}/{self.questions_number}', 
                                                           font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyAuth_question_counter_label.grid(row=0, column=1, padx=5, pady=(3, 5))        
        
        # Button: ">" Следующий вопрос
        self.next_question_button = CTk.CTkButton(self.KeyAuth_question_control_frame, 
                                                  text='>', 
                                                  command=lambda: self.display_next_question(self.KeyAuth_question_counter_label,
                                                                                             self.KeyAuth_questions_textbox),
                                                  width=30,
                                                  font=CTk.CTkFont(size=20, weight='bold'))
        self.next_question_button.grid(row=0, column=2, padx=5, pady=(3, 5))

        # Label: Ответы
        self.KeyAuth_answers_label = CTk.CTkLabel(self.keystroke_authorization_frame, 
                                                  text='ПОЛЕ, ДЛЯ ВВОДА ОТВЕТОВ:', 
                                                  font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyAuth_answers_label.grid(row=4, column=0, padx=30, pady=(5, 5))

        # TextBox: Предназначен для ввода ответов
        self.KeyAuth_answers_textbox = CTk.CTkTextbox(self.keystroke_authorization_frame, 
                                                      width=500, 
                                                      height=100,
                                                      wrap=CTk.WORD,
                                                      font=CTk.CTkFont(size=16, weight='bold'))
        self.KeyAuth_answers_textbox.grid(row=5, column=0, padx=(20, 20), pady=(5, 0))      
        self.KeyAuth_answers_textbox.delete('1.0', CTk.END) # Отчистка TextBox'а
        
        self.KeyAuth_answers_textbox.bind('<KeyPress>', self.press_key_event_KeyAuthFrame)

        # CTk 5.2.1 - Фокус на TextBox'е все еще не работает
        self.KeyAuth_answers_textbox.focus() # Фокус на TextBox'е
        #self.KeyAuth_answers_textbox.focus_set() # Альтернативный Фокус на TextBox'е
        #self.KeyAuth_answers_textbox.focus_force() # Альтернативный Фокус на TextBox'е
       
        self.KeyAuth_progressbar = CTk.CTkProgressBar(self.keystroke_authorization_frame)
        self.KeyAuth_progressbar.grid(row=6, column=0, padx=30, pady=(5, 5))
        #self.KeyAuth_progressbar.configure(mode='indeterminnate')
        self.KeyAuth_progressbar.configure(mode='determinate')
        self.KeyAuth_progressbar.set(0)
        #self.KeyAuth_progressbar.start()
        
        # Button: "Вернутся"
        self.KeyAuth_to_PassAuth_frame_button = CTk.CTkButton(self.keystroke_authorization_frame, 
                                                              text='вернуться', 
                                                              command=self.state_machine.switch_to_password_authorization, 
                                                              width=200,
                                                              font=CTk.CTkFont(size=14, weight='bold'))
        self.KeyAuth_to_PassAuth_frame_button.grid(row=7, column=0, padx=30, pady=(20, 10))
        

        # ------------------------------------ keystroke extract frame ------------------------------------ #

        # Создание фрейма окна извлечения ритма нажатия клавиш польователя, для последующего обечения модели
        self.keystroke_extract_frame = CTk.CTkFrame(self, corner_radius=0)
        #self.keystroke_extract_frame.grid(row=0, column=0, sticky='ns')

        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('keystroke_extract_frame', self.keystroke_extract_frame)
        
        KeyExtr_frame_name_text = 'ЭКСТРАКТОР ПРИЗНАКОВ'
        # Label: "Экстрактор признаков"
        self.KeyExtr_frame_name_label = CTk.CTkLabel(self.keystroke_extract_frame, 
                                                     text=KeyExtr_frame_name_text, 
                                                     font=CTk.CTkFont(size=20, weight='bold'))
        self.KeyExtr_frame_name_label.grid(row=0, column=0, padx=30, pady=(20, 10))

        KeyExtr_frame_instruction_text = 'для успешного обучения искусственной нейронной сети\n\
определять вас как "Своего" и блокировать доступ\n"Чужому", вам следует отвечать на заданные вопросы,\n\
пока не заполнится шкала (вопросы можно менять)\n\nВОПРОСЫ:'
        # Label: Инструкция прохождения биометрической аутентификации по клавиатурному почерку
        self.KeyExtr_frame_instruction_label = CTk.CTkLabel(self.keystroke_extract_frame, 
                                                            text=KeyExtr_frame_instruction_text, 
                                                            font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyExtr_frame_instruction_label.grid(row=1, column=0, padx=30, pady=(10, 5))
        
        # TextBox: Содержит вопросы
        self.KeyExtr_questions_textbox = CTk.CTkTextbox(self.keystroke_extract_frame, 
                                                        width=500, 
                                                        height=100,
                                                        wrap=CTk.WORD,
                                                        font=CTk.CTkFont(size=16, weight='bold'))
        self.KeyExtr_questions_textbox.grid(row=2, column=0, padx=(20, 20), pady=(5, 0))
        # Отчистка TextBox'а
        self.KeyExtr_questions_textbox.delete('1.0', CTk.END)
        # Вставка вопроса в TextBox
        self.KeyExtr_questions_textbox.insert('0.0', f'{self.questions[self.current_question + 1]}')
        self.KeyExtr_questions_textbox.configure(state='disabled') # Деактивировать TextBox       
        

        # Создание фрейма, содержащего элементы управления перелистывания вопросов
        self.KeyExtr_question_control_frame = CTk.CTkFrame(self.keystroke_extract_frame, 
                                                           corner_radius=0,
                                                           fg_color='transparent')
        self.KeyExtr_question_control_frame.grid(row=3, column=0, padx=0, pady=(3, 10))
        
        # Button: "<" Предыдущий вопрос
        args = lambda: self.display_previous_question(self.KeyExtr_question_counter_label, self.KeyExtr_questions_textbox)
        self.previous_question_button = CTk.CTkButton(self.KeyExtr_question_control_frame, 
                                                      text='<', 
                                                      command=args,
                                                      width=30,
                                                      font=CTk.CTkFont(size=20, weight='bold'))
        self.previous_question_button.grid(row=0, column=0, padx=5, pady=(3, 5))
        
        # Label: Текущий вопрос / Всего вопросов
        self.KeyExtr_question_counter_label = CTk.CTkLabel(self.KeyExtr_question_control_frame, 
                                                           text=f'{self.current_question + 1}/{self.questions_number}', 
                                                           font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyExtr_question_counter_label.grid(row=0, column=1, padx=5, pady=(3, 5))        
        
        # Button: ">" Следующий вопрос
        self.next_question_button = CTk.CTkButton(self.KeyExtr_question_control_frame, 
                                                  text='>', 
                                                  command=lambda: self.display_next_question(self.KeyExtr_question_counter_label, 
                                                                                             self.KeyExtr_questions_textbox), 
                                                  width=30,
                                                  font=CTk.CTkFont(size=20, weight='bold'))
        self.next_question_button.grid(row=0, column=2, padx=5, pady=(3, 5))

        # Label: Ответы
        self.KeyExtr_answers_label = CTk.CTkLabel(self.keystroke_extract_frame, 
                                                  text='ПОЛЕ, ДЛЯ ВВОДА ОТВЕТОВ:', 
                                                  font=CTk.CTkFont(size=18, weight='bold'))
        self.KeyExtr_answers_label.grid(row=4, column=0, padx=30, pady=(5, 5))

        # TextBox: Предназначен для ввода ответов
        self.KeyExtr_answers_textbox = CTk.CTkTextbox(self.keystroke_extract_frame, 
                                                      width=500, 
                                                      height=100,
                                                      wrap=CTk.WORD,
                                                      font=CTk.CTkFont(size=16, weight='bold'))
        self.KeyExtr_answers_textbox.grid(row=5, column=0, padx=(20, 20), pady=(5, 0))      
        self.KeyExtr_answers_textbox.delete('1.0', CTk.END) # Отчистка TextBox'а
        
        self.KeyExtr_answers_textbox.bind('<KeyPress>', self.press_key_event_KeyExtrFrame)

        # CTk 5.2.1 - Фокус на TextBox'е все еще не работает
        self.KeyExtr_answers_textbox.focus() # Фокус на TextBox'е
        #self.KeyExtr_answers_textbox.focus_set() # Альтернативный Фокус на TextBox'е
        #self.KeyExtr_answers_textbox.focus_force() # Альтернативный Фокус на TextBox'е

        self.KeyExtr_progressbar = CTk.CTkProgressBar(self.keystroke_extract_frame)
        self.KeyExtr_progressbar.grid(row=6, column=0, padx=30, pady=(5, 5))
        #self.KeyAuth_progressbar.configure(mode='indeterminnate')
        self.KeyExtr_progressbar.configure(mode='determinate')
        self.KeyExtr_progressbar.set(0)
        
        # Button: "Вернутся"
        self.KeyExtr_to_PassAuth_frame_button = CTk.CTkButton(self.keystroke_extract_frame, 
                                                              text='вернуться', 
                                                              command=self.state_machine.switch_to_password_authorization, 
                                                              width=200,
                                                              font=CTk.CTkFont(size=14, weight='bold'))
        self.KeyExtr_to_PassAuth_frame_button.grid(row=7, column=0, padx=30, pady=(20, 10))
        

        # -------------------------------------- user profile frame --------------------------------------- #

        # Создание фрейма профиля пользователя
        self.user_profile_frame = CTk.CTkFrame(self, corner_radius=0)
        self.user_profile_frame.grid_rowconfigure(0, weight=1)
        #self.user_profile_frame.grid(row=0, column=0, sticky='ns')
            
        # Обеспечиваем доступ к фрейму из машины состояний
        self.state_machine.frames_setter('user_profile_frame', self.user_profile_frame)
        
        # Создание подфрейма, содержащего настройки
        self.settings_frame = CTk.CTkFrame(self.user_profile_frame, corner_radius=0)
        self.settings_frame.grid(row=0, column=0, sticky='ns')
 

        # Label: ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ
        self.settings_frame_profile_label = CTk.CTkLabel(self.settings_frame, 
                                                         text='ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ', 
                                                         font=CTk.CTkFont(size=20, weight='bold'))
        self.settings_frame_profile_label.grid(row=0, column=0, padx=30, pady=(15, 15))

        # Создание подфрейма, содержащего имя текущего пользовтеля
        self.settings_current_user_frame = CTk.CTkFrame(self.settings_frame, 
                                                        corner_radius=0)
        self.settings_current_user_frame.grid(row=1, column=0, sticky='nswe')
        
        # Картинка (абстрактное обозначение пользователя)
        self.user_image = CTk.CTkImage(Image.open('images/UserImage.png'), size=(48, 48))
        
        # Label: Отображение картинки
        self.settings_frame_current_user_image = CTk.CTkLabel(self.settings_current_user_frame, 
                                                              text='', 
                                                              image=self.user_image,
                                                              font=CTk.CTkFont(size=18, weight='bold'))
        self.settings_frame_current_user_image.grid(row=0, column=0, padx=(30,5), pady=(5, 5), sticky='nsw')
        
        # Label: Отображение имени текущего пользователя
        self.settings_frame_current_user_label = CTk.CTkLabel(self.settings_current_user_frame, 
                                                              text=f'{self.current_user}', 
                                                              font=CTk.CTkFont(size=18, weight='bold'))
        self.settings_frame_current_user_label.grid(row=0, column=1, padx=5, pady=(5, 5), sticky='nsw')


        # Label: настройки
        self.settings_frame_settings_label = CTk.CTkLabel(self.settings_frame, 
                                                          text='НАСТРОЙКИ:', 
                                                          font=CTk.CTkFont(size=18, weight='bold'))
        self.settings_frame_settings_label.grid(row=2, column=0, padx=0, pady=(25, 5))


        # Button: "сбросить модель"
        self.settings_frame_reset_model_button = CTk.CTkButton(self.settings_frame, 
                                                               text='сбросить модель', 
                                                               command=self.login_event, 
                                                               width=200,
                                                               font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_reset_model_button.grid(row=3, column=0, padx=0, pady=(10, 10))
        

        # Button: "Изменить пароль"
        self.settings_frame_change_password_button = CTk.CTkButton(self.settings_frame, 
                                                                   text='изменить пароль', 
                                                                   command=self.login_event, 
                                                                   width=200,
                                                                   font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_change_password_button.grid(row=4, column=0, padx=0, pady=(10, 10))
        

        # Label: "допустимое отклонение"
        self.settings_frame_tolerance_label = CTk.CTkLabel(self.settings_frame, 
                                                          text='допустимое отклонение:', 
                                                          font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_tolerance_label.grid(row=5, column=0, padx=0, pady=(5, 0))
        
        
        # OptionMenu: Допустимое отклонение (стандартное/увеличенное)
        self.settings_frame_tolerance_mode = CTk.CTkOptionMenu(self.settings_frame, 
                                                               dynamic_resizing=False,
                                                               values=['стандартное', 'увеличенное'],
                                                               width=200,
                                                               font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_tolerance_mode.grid(row=6, column=0, padx=0, pady=(5, 10))
        

        # Создание подфрейма (Выбор действий, при обнаружении "Чужого" - предупреждений и/или блокирование)
        self.actions_frame = CTk.CTkFrame(self.settings_frame, corner_radius=10)
        self.actions_frame.grid(row=7, column=0, pady=(8, 0))

        # Label: действия при обнаружении "Чужого"
        self.settings_frame_tolerance_label = CTk.CTkLabel(self.actions_frame, 
                                                          text='действия при\nобнаружении "Чужого":', 
                                                          font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_tolerance_label.grid(row=0, column=0, padx=12, pady=(8, 3))
        
        # CheckBox: включает/отключает отображение предупреждения при обнаружении "Чужого"
        self.action_alert_CheckBox = CTk.CTkCheckBox(master=self.actions_frame, 
                                                     text='предупреждение',
                                                     variable=self.alert_CheckBox_BooleanVar,
                                                     font=CTk.CTkFont(size=14, weight='bold'))
        self.action_alert_CheckBox.grid(row=1, column=0, pady=(10, 0), padx=20, sticky='nsw')

        # CheckBox: включает/отключает блокирование машины при обнаружении "Чужого"
        self.action_block_CheckBox = CTk.CTkCheckBox(master=self.actions_frame, 
                                                     text='блокирование',
                                                     variable=self.block_CheckBox_BooleanVar,
                                                     font=CTk.CTkFont(size=14, weight='bold'))
        self.action_block_CheckBox.grid(row=2, column=0, pady=(10, 10), padx=20, sticky='nsw')
        
        # Switch: включает/отключает непрерывную аутентификацию по клавиатурному почерку
        self.settings_frame_ContAuth_Switch = CTk.CTkSwitch(master=self.settings_frame, 
                                                            text='     непрерывная\n  аутентификация',
                                                            variable=self.ContAuth_Switch_BooleanVar,
                                                            font=CTk.CTkFont(size=13, weight='bold'))
        self.settings_frame_ContAuth_Switch.grid(row=8, column=0, pady=(15, 10))


        # Button: "выйти"
        self.settings_frame_logout_button = CTk.CTkButton(self.settings_frame, 
                                                                   text='выйти', 
                                                                   command=self.login_event, 
                                                                   width=200,
                                                                   font=CTk.CTkFont(size=14, weight='bold'))
        self.settings_frame_logout_button.grid(row=9, column=0, padx=0, pady=(10, 10))


        # Создание подфрейма, содержащего логи
        self.logs_frame = CTk.CTkFrame(self.user_profile_frame, corner_radius=0, fg_color='transparent')
        self.logs_frame.grid(row=0, column=1, sticky='ns')
        
        
        #####################################################################################################


    def press_key_event_KeyAuthFrame(self, event):
        print(event) # <KeyPress event send_event=True state=Mod1 keysym=w keycode=87 char='w' x=275 y=46>
        self.characters_counter += 1
            
        progressbar_new_value = self.characters_counter / self.authentication_required_characters

        self.KeyAuth_progressbar.set(progressbar_new_value)
        
        print(f'{self.characters_counter} / {self.authentication_required_characters}') # Debug

        if self.characters_counter >= self.authentication_required_characters:
            self.focus() # Убрать фокус с текстбокса
            self.state_machine.switch_to_user_profile()
  
        
    def press_key_event_KeyExtrFrame(self, event):
        print(event) # <KeyPress event send_event=True state=Mod1 keysym=w keycode=87 char='w' x=275 y=46>
        self.characters_counter += 1
            
        progressbar_new_value = self.characters_counter / self.registration_required_characters

        self.KeyExtr_progressbar.set(progressbar_new_value)
        

    def display_next_question(self, label, textbox):
        self.current_question = ((self.current_question + 1) % self.questions_number)
        label.configure(text=f'{self.current_question + 1}/{self.questions_number}')
        
        # Активировать ТекстБокс
        textbox.configure(state='normal') 
        # Отчистка ТекстБокса
        textbox.delete('1.0', CTk.END) 
        # Вставка вопроса в ТекстБокс
        textbox.insert('0.0', f'{self.questions[self.current_question + 1]}')
        # Деактивировать ТекстБокс
        textbox.configure(state='disabled') 


    def display_previous_question(self, label, textbox):
        self.current_question = ((self.current_question - 1) % self.questions_number)
        label.configure(text=f'{self.current_question + 1}/{self.questions_number}')
        
        # Активировать ТекстБокс
        textbox.configure(state='normal')         
        # Отчистка ТекстБокса
        textbox.delete('1.0', CTk.END) 
        # Вставка вопроса в ТекстБокс
        textbox.insert('0.0', f'{self.questions[self.current_question + 1]}')
        # Деактивировать ТекстБокс
        textbox.configure(state='disabled')        


    def login_event(self):
        # "Заглушка"
        pass


def main():
    app = App()
    app.mainloop()


    

if __name__ == '__main__':
    main()