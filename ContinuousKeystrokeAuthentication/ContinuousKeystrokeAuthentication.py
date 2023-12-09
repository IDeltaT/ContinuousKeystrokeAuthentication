from transitions import Machine


class ProgramCore:
    

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


