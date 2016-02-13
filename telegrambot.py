# -*- coding: utf-8 -*-
import requests
import time
import subprocess
import os
import psycopg2
from datetime import datetime
#import mailchecker

requests.packages.urllib3.disable_warnings()  # Подавление InsecureRequestWarning, с которым я пока ещё не разобрался

# Ключ авторизации Вашего бота Вы можете получить в любом клиенте Telegram у бота @BotFather
# ADMIN_ID - идентификатор пользователя (то есть Вас), которому подчиняется бот
# Чтобы определить Ваш ID, я предлагаю отправить боту сообщение от своего имени (аккаунта) через любой клиент
# А затем получить это сообщения с помощью обычного GET запроса
# Для этого вставьте в адресную строку Вашего браузера следующий адрес, заменив <token> на свой ключ:
# https://api.telegram.org/bot169184937:AAF7IQ3eWsMaTuMTQyA3fQMZ_m53g5qKQP0/getUpdates
# Затем, в ответе найдите объект "from":{"id":01234567,"first_name":"Name","username":"username"}
# Внимательно проверьте имя, логин и текст сообщения
# Если всё совпадает, то цифровое значение ключа "id" - это и есть ваш идентификатор

# Переменным ADMIN_ID и TOKEN необходимо присвоить Вашим собственные значения
INTERVAL = 3  # Интервал проверки наличия новых сообщений (обновлений) на сервере в секундах
ADMIN_ID = 83109589  # ID пользователя. Комманды от других пользователей выполняться не будут
ADMIN_GROUP = -103322856  # ID группы. Комманды от других пользователей выполняться не будут
URL = 'https://api.telegram.org/bot'  # Адрес HTTP Bot API
TOKEN = '169184937:AAF7IQ3eWsMaTuMTQyA3fQMZ_m53g5qKQP0'  # Ключ авторизации для Вашего бота
offset = 0  # ID последнего полученного обновления
questionnaire = 0
date_start = 2 # день недели запуска опроса и обнуления поля visit

# noinspection PyBroadException
def check_updates():
    """Проверка обновлений на сервере и инициация действий, в зависимости от команды"""
    global offset
    data = {'offset': offset + 1, 'limit': 5, 'timeout': 0}  # Формируем параметры запроса

    try:
        request = requests.post(URL + TOKEN + '/getUpdates', data=data)  # Отправка запроса обновлений
    except:
        log_event('Error getting updates')  # Логгируем ошибку
        return False  # Завершаем проверку

    if not request.status_code == 200: return False  # Проверка ответа сервера
    if not request.json()['ok']: return False  # Проверка успешности обращения к API
    for update in request.json()['result']:  # Проверка каждого элемента списка
        offset = update['update_id']  # Извлечение ID сообщения

        # Ниже, если в обновлении отсутствует блок 'message'
        # или же в блоке 'message' отсутствует блок 'text', тогда
        if not 'message' in update or not 'text' in update['message']:
            log_event('Unknown update: %s' % update)  # сохраняем в лог пришедшее обновление
            continue  # и переходим к следующему обновлению

        from_id = update['message']['chat']['id']  # Извлечение ID чата (отправителя)
        name = update['message']['from']['first_name']  # Извлечение first_name отправителя
        if not 'last_name' in update['message']['from']:
            second_name = None
        else:
            second_name = update['message']['from']['last_name']  # Извлечение last_name отправителя
        if not 'username' in update['message']['from']:
            username = None
        else:
            username = update['message']['from']['username']  # Извлечение username отправителя
        #        if from_id != ADMIN_ID: # Если отправитель не является администратором, то
        #            if from_id != ADMIN_GROUP:
        #                send_text(from_id, "You're not autorized to use me!") # ему отправляется соответствующее уведомление
        #                log_event('Unautorized: %s' % update) # обновление записывается в лог
        #                continue # и цикл переходит к следующему обновлению
        message = update['message']['text']  # Извлечение текста сообщения
        parameters = (offset, name, from_id, message, second_name, username)
        log_event('Message (id %s) from %s (id %s): "%s"' % (offset, name, from_id, message))  # Вывод в лог ID и текста сообщения

        # В зависимости от сообщения, выполняем необходимое действие
        run_command(*parameters)


def run_command(offset, name, from_id, cmd, second_name, username):
    if cmd == '/start':  # Ответ на yes
        send_text(from_id, 'Привет! Идешь на футбол? \nОтвечай: /yes или /no')  # Отправка ответа
        db_insert(from_id, name, second_name, username)

    elif cmd == '/help':  # Ответ на yes
        send_text(from_id,
                  'Бот предназначен для переклички сотрудников, идущих на футбол. \n\nПо средам в 11 часов бот будет опрашивать все подписчиков (подписка началась после команды /start) идешь ли ты на футбол \n\nЕсли отметиться второй раз, то бот перезапишет первый ответ. \n\nУзнать списки идущих и неидущих можно через команду /list  \n\nВ ночь после футбола результаты опроса будут обнуляться \n\nДля остановки подписки используйте команду /stop')  # Отправка ответа

    elif cmd == '/yes':  # Ответ на yes
        #send_text(from_id, 'Молодцом!') # Отправка ответа
        send_sticker(from_id, 'BQADAgAD_gQAAkKvaQABbdMfUUWsaZEC')  # Отправка ответа
        db_update(from_id, True)

    elif cmd == '/no':  # Ответ на no
        send_sticker(from_id, 'BQADAgADGgUAAkKvaQABSfrnIsfrgPYC')  # Отправка ответа
        db_update(from_id, False)

    elif cmd == '/list':  # Ответ на no
        #send_text(from_id, 'в работе...') # Отправка ответа
        db_select(from_id)

    elif cmd == '/stop':  # Ответ на no
        send_sticker(from_id, 'BQADAgADDgUAAkKvaQABF5KWQUCJNzkC')  # Отправка ответа
        db_delete(from_id)

    elif cmd == '/reset_visit' and from_id == ADMIN_ID:  # Ответ на no
        db_visit_update()
        send_text(from_id, 'ok')  # Отправка ответа

    elif cmd == '/send_opros' and from_id == ADMIN_ID:  # Ответ на no
        send_questionnaire()
        send_text(from_id, 'ok')  # Отправка ответа

def log_event(text):
    """
    Процедура логгирования
    ToDo: 1) Запись лога в файл
    """
    event = '%s >> %s' % (time.ctime(), text)
    print event
    #logfile = open('log.txt', 'a')
    #logfile.write(event)
    #logfile.write('\n')
    #logfile.close()

def send_text(chat_id, text):
    """Отправка текстового сообщения по chat_id
    ToDo: повторная отправка при неудаче"""
    log_event('Sending to %s: %s' % (chat_id, text))  # Запись события в лог
    data = {'chat_id': chat_id, 'text': text}  # Формирование запроса
    request = requests.post(URL + TOKEN + '/sendMessage', data=data)  # HTTP запрос
    if not request.status_code == 200:  # Проверка ответа сервера
        return False  # Возврат с неудачей
    return request.json()['ok']  # Проверка успешности обращения к API


def send_sticker(chat_id, sticker_id):
    """Отправка стикера по chat_id
    ToDo: повторная отправка при неудаче"""
    log_event('Sending to %s: %s' % (chat_id, sticker_id))  # Запись события в лог
    data = {'chat_id': chat_id, 'sticker': sticker_id}  # Формирование запроса
    request = requests.post(URL + TOKEN + '/sendSticker', data=data)  # HTTP запрос
    if not request.status_code == 200:  # Проверка ответа сервера
        return False  # Возврат с неудачей
    return request.json()['ok']  # Проверка успешности обращения к API


def make_photo(photo_id):
    """Обращение к приложению fswebcam для получения снимка с Web-камеры"""
    photo_name = 'photo/%s.jpg' % photo_id  # Формирование имени файла фотографии
    subprocess.call('fswebcam -q -r 1280x720 %s' % photo_name, shell=True)  # Вызов shell-команды
    #subprocess.call('fswebcam -c /home/pi/.fswebcam.conf') # Вызов shell-команды
    return os.path.exists(photo_name)  # Проверка, появился ли файл с таким названием


def send_photo(chat_id, photo_id):
    """Отправка фото по его идентификатору выбранному контакту"""
    data = {'chat_id': chat_id}  # Формирование параметров запроса
    photo_name = 'photo/%s.jpg' % photo_id  # Формирования имени файла фотографии
    if not os.path.exists(photo_name): return False  # Проверка существования фотографии
    files = {'photo': open(photo_name, 'rb')}  # Открытие фото и присвоение
    request = requests.post(URL + TOKEN + '/sendPhoto', data=data, files=files)  # Отправка фото
    return request.json()['ok']  # Возврат True или False, полученного из ответа сервера, в зависимости от результата


def check_mail():
    """Проверка почтовых ящиков с помощью самодельного модуля"""
    print "Подключите и настройте модуль проверки почты"
    return False
    try:
        log_event('Checking mail...')  # Запись в лог
        respond = mailchecker.check_all()  # Получаем ответ от модуля проверки
    except:
        log_event('Mail check failed.')  # Запись в лог
        return False  # И возврат с неудачей
    if not respond: respond = 'No new mail.'  # Если ответ пустой, тогда заменяем его на соответствующее сообщение
    send_text(ADMIN_ID, respond)  # Отправляем это сообщение администратору
    return True


def db_insert(chat_id, name, second_name, username):
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM footballer WHERE user_id = %s", [chat_id])
    u = cursor.fetchone()
    if not u:
        cursor.execute(
            "INSERT INTO footballer (user_id, first_name, second_name, username, visit, resp_date, resp_time) VALUES (%s, %s, %s, %s, %s, %s, %s)", (chat_id, name, second_name, username, None, None, None))
        conn.commit()
        log_event('Records created successfully')
        conn.close()
        return True
    else:
        cursor.execute(
            "UPDATE footballer SET first_name = %s, second_name = %s, username = %s WHERE user_id = %s", [name, second_name, username, chat_id])
        conn.commit()
        log_event('Record updated successfully')
        conn.close()
        return True


def db_update(chat_id, visit_id):
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully')
    cursor = conn.cursor()
    cursor.execute("UPDATE footballer SET visit = %s WHERE user_id = %s", (visit_id, chat_id))
    conn.commit()
    log_event('Records updated successfully.')
    conn.close()
    return True


def db_select(chat_id, yes_list='***Идут: ', no_list='***Не идут: '):
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM footballer WHERE visit = True")
    for row in cursor.fetchall():
        yes_list = yes_list + str(row[0]) + '\n'
        yes_list = yes_list.decode('utf-8')
    cursor.execute("SELECT first_name, second_name, username FROM footballer WHERE visit = True")
    for row in cursor.fetchall():
        yes_list = yes_list + row[0] + '\n'

    #    for row in cursor:
    #        print "first_name = ", row[0]
    #        print "second_name = ", row[1]
    #        print "username = ", row[2], "\n"
    #for f, s, u in cursor.fetchall():
    cursor.execute("SELECT COUNT(user_id) FROM footballer WHERE visit = FALSE")
    for row in cursor.fetchall():
        no_list = no_list + str(row[0]) + '\n'
        no_list = no_list.decode('utf-8')
    cursor.execute("SELECT first_name, second_name, username FROM footballer WHERE visit = FALSE")
    for row in cursor.fetchall():
        no_list = no_list + row[0] + '\n'
    log_event('Operation done successfully.')
    conn.close()
    #if not yes_list: yes_list = '*Список пуст*'  # Если ответ пустой, тогда заменяем его на соответствующее сообщение
    #if not yes_list: yes_list = '*Список пуст*'  # Если ответ пустой, тогда заменяем его на соответствующее сообщение
    text = yes_list + no_list
    data = {'chat_id': chat_id, 'text': text}  # Формирование запроса
    #log_event('Sending to %s: %s' % (chat_id, text))  # Запись события в лог
    log_event('Lists sent, fully done.')
    request = requests.post(URL + TOKEN + '/sendMessage', data=data)  # HTTP запрос
    if not request.status_code == 200:  # Проверка ответа сервера
        return False  # Возврат с неудачей
    return request.json()['ok']  # Проверка успешности обращения к API


def db_delete(chat_id):
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM footballer WHERE user_id = %s", [chat_id])
    conn.commit()
    log_event('Operation done successfully.')
    conn.close()
    return True

def db_visit_update():
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully')
    cursor = conn.cursor()
    cursor.execute("UPDATE footballer SET visit = %s", [None])
    conn.commit()
    log_event('Operation db_visit_update done successfully.')
    conn.close()
    return True

def send_questionnaire():
    conn = psycopg2.connect(database='d5orecc0oeod38', user='dwxpxijyrlhnyp', password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG', host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com', port='5432')
    log_event('Opened database successfully.')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM footballer")
    for row in cursor.fetchall():
        user_id = row[0]
        log_event('Sending to %s: %s' % (user_id, 'Привет! Идешь на футбол? Отвечай: /yes или /no'))  # Запись события в лог
        data = {'chat_id': user_id, 'text': 'Привет! Идешь на футбол? \nОтвечай: /yes или /no'}  # Формирование запроса
        requests.post(URL + TOKEN + '/sendMessage', data=data)  # HTTP запрос
    log_event('Operation send_questionnaire done successfully.')
    conn.close()
    return True

def questionnaire_n_visit_reset():
    global questionnaire
    global d
    time_start1 = ('11:00')
    time_start2 = ('23:59')
    time_x = d.strftime('%H:%M')
    if time_x in time_start1 and questionnaire == 0:
        send_questionnaire()
        questionnaire = 1
        log_event('Questionnaire done successfully.')
    if time_x in time_start2:
        db_visit_update()
        questionnaire = 0
        log_event('Questionnaire has reset successfully.')
        time.sleep(60)
    return True

if __name__ == "__main__":
    while True:
        try:
            check_updates()
            d = datetime.today()
            if d.weekday() == date_start:
                questionnaire_n_visit_reset()
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print 'Прервано пользователем..'
            break