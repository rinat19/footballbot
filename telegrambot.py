# -*- coding: utf-8 -*-
import requests
import time
import subprocess
import os
#import mailchecker

requests.packages.urllib3.disable_warnings() # Подавление InsecureRequestWarning, с которым я пока ещё не разобрался

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
INTERVAL = 3 # Интервал проверки наличия новых сообщений (обновлений) на сервере в секундах
ADMIN_ID = 83109589 # ID пользователя. Комманды от других пользователей выполняться не будут
ADMIN_GROUP = -103322856 # ID группы. Комманды от других пользователей выполняться не будут
URL = 'https://api.telegram.org/bot' # Адрес HTTP Bot API
TOKEN = '169184937:AAF7IQ3eWsMaTuMTQyA3fQMZ_m53g5qKQP0' # Ключ авторизации для Вашего бота
offset = 0 # ID последнего полученного обновления

def check_updates():
    """Проверка обновлений на сервере и инициация действий, в зависимости от команды"""
    global offset
    data = {'offset': offset + 1, 'limit': 5, 'timeout': 0} # Формируем параметры запроса

    try:
        request = requests.post(URL + TOKEN + '/getUpdates', data=data) # Отправка запроса обновлений
    except:
        log_event('Error getting updates') # Логгируем ошибку
        return False # Завершаем проверку

    if not request.status_code == 200: return False # Проверка ответа сервера
    if not request.json()['ok']: return False # Проверка успешности обращения к API
    for update in request.json()['result']: # Проверка каждого элемента списка
        offset = update['update_id'] # Извлечение ID сообщения

        # Ниже, если в обновлении отсутствует блок 'message'
        # или же в блоке 'message' отсутствует блок 'text', тогда
        if not 'message' in update or not 'text' in update['message']:
            log_event('Unknown update: %s' % update) # сохраняем в лог пришедшее обновление
            continue # и переходим к следующему обновлению

        from_id = update['message']['chat']['id'] # Извлечение ID чата (отправителя)
        name = update['message']['from']['first_name'] # Извлечение username отправителя
        if from_id != ADMIN_ID: # Если отправитель не является администратором, то
            if from_id != ADMIN_GROUP:
                send_text(from_id, "You're not autorized to use me!") # ему отправляется соответствующее уведомление
                log_event('Unautorized: %s' % update) # обновление записывается в лог
                continue # и цикл переходит к следующему обновлению
        message = update['message']['text'] # Извлечение текста сообщения
        parameters = (offset, name, from_id, message)
        log_event('Message (id%s) from %s (id%s): "%s"' % parameters) # Вывод в лог ID и текста сообщения

        # В зависимости от сообщения, выполняем необходимое действие
        run_command(*parameters)

def run_command(offset, name, from_id, cmd):
    if cmd == '/yes': # Ответ на yes
        send_sticker(from_id, 'BQADAgAD_gQAAkKvaQABbdMfUUWsaZEC') # Отправка ответа

    elif cmd == '/no': # Ответ на no
        send_sticker(from_id, 'BQADAgADGgUAAkKvaQABSfrnIsfrgPYC') # Отправка ответа

def log_event(text):
    """
    Процедура логгирования
    ToDo: 1) Запись лога в файл
    """
    event = '%s >> %s' % (time.ctime(), text)
    print event

def send_text(chat_id, text):
    """Отправка текстового сообщения по chat_id
    ToDo: повторная отправка при неудаче"""
    log_event('Sending to %s: %s' % (chat_id, text)) # Запись события в лог
    data = {'chat_id': chat_id, 'text': text} # Формирование запроса
    request = requests.post(URL + TOKEN + '/sendMessage', data=data) # HTTP запрос
    if not request.status_code == 200: # Проверка ответа сервера
        return False # Возврат с неудачей
    return request.json()['ok'] # Проверка успешности обращения к API

def send_sticker(chat_id, sticker_id):
    """Отправка стикера по chat_id
    ToDo: повторная отправка при неудаче"""
    log_event('Sending to %s: %s' % (chat_id, sticker_id)) # Запись события в лог
    data = {'chat_id': chat_id, 'sticker': sticker_id} # Формирование запроса
    request = requests.post(URL + TOKEN + '/sendSticker', data=data) # HTTP запрос
    if not request.status_code == 200: # Проверка ответа сервера
        return False # Возврат с неудачей
    return request.json()['ok'] # Проверка успешности обращения к API

def make_photo(photo_id):
    """Обращение к приложению fswebcam для получения снимка с Web-камеры"""
    photo_name = 'photo/%s.jpg' % photo_id # Формирование имени файла фотографии
    subprocess.call('fswebcam -q -r 1280x720 %s' % photo_name, shell=True) # Вызов shell-команды
    #subprocess.call('fswebcam -c /home/pi/.fswebcam.conf') # Вызов shell-команды
    return os.path.exists(photo_name) # Проверка, появился ли файл с таким названием

def send_photo(chat_id, photo_id):
    """Отправка фото по его идентификатору выбранному контакту"""
    data = {'chat_id': chat_id} # Формирование параметров запроса
    photo_name = 'photo/%s.jpg' % photo_id # Формирования имени файла фотографии
    if not os.path.exists(photo_name): return False # Проверка существования фотографии
    files = {'photo': open(photo_name, 'rb')} # Открытие фото и присвоение
    request = requests.post(URL + TOKEN + '/sendPhoto', data=data, files=files) # Отправка фото
    return request.json()['ok'] # Возврат True или False, полученного из ответа сервера, в зависимости от результата

def check_mail():
    """Проверка почтовых ящиков с помощью самодельного модуля"""
    print "Подключите и настройте модуль проверки почты"
    return False
    try:
        log_event('Checking mail...') # Запись в лог
        respond = mailchecker.check_all() # Получаем ответ от модуля проверки
    except:
        log_event('Mail check failed.') # Запись в лог
        return False # И возврат с неудачей
    if not respond: respond = 'No new mail.' # Если ответ пустой, тогда заменяем его на соответствующее сообщение
    send_text(ADMIN_ID, respond) # Отправляем это сообщение администратору
    return True

if __name__ == "__main__":
    while True:
        try:
            check_updates()
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print 'Прервано пользователем..'
            break