# coding=utf-8
from datetime import datetime
from time import sleep
from telegrambot import send_text, db_visit_update

date_start = 3
time_start1 = ('11:00')
time_start2 = ('23:30')
while True:
    d = datetime.today()
    print d.strftime('%H:%M')
    print 'weekday = ', d.weekday()
    date_x = d.weekday()
    time_x = d.strftime('%H:%M')
    if date_x == date_start:
        if time_x in time_start1:
            text = 'Идешь на футбол?'
            send_text('83109589', text)
            sleep(59)
        if time_x in time_start2:
            db_visit_update()
            sleep(59)
