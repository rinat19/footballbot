import sqlite3

con = sqlite3.connect('telegrambot.db')
cur = con.cursor()
#cur.execute('CREATE TABLE footballer (id INTEGER PRIMARY KEY, user_id INTEGER, first_name VARCHAR(100), second_name VARCHAR(30), username VARCHAR(30))')
#con.commit()
#cur.execute('INSERT INTO footballer (id, user_id, first_name, second_name, username) VALUES(1, 83109589, "Rinat", NULL, "plohoidurdom")')
#con.commit()
#cur.execute('CREATE TABLE footballer_visit (id INTEGER PRIMARY KEY, user_id INTEGER, visit BOOLEAN, resp_date DATETIME)')
#con.commit()
#cur.execute('INSERT INTO footballer_visit (id, user_id, visit, resp_date) VALUES(1, 83109589, 1, "2016-03-28 15:05:59")')
#con.commit()
print cur.lastrowid

cur.execute('SELECT * FROM footballer')
print cur.fetchall()
con.close()