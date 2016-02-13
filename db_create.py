import psycopg2


conn = psycopg2.connect(
    database='d5orecc0oeod38',
    user='dwxpxijyrlhnyp',
    password='HeTB8Lyf3BLhYbXjHBCV1Wy9zG',
    host='ec2-54-217-202-109.eu-west-1.compute.amazonaws.com',
    port='5432'
)
cur = conn.cursor()
cur.execute('CREATE TABLE footballer (user_id INTEGER PRIMARY KEY, first_name VARCHAR(30), second_name VARCHAR(30), username VARCHAR(30), visit BOOLEAN, resp_date DATE, resp_time TIME WITHOUT ZONE)')
cur.commit()
cur.execute('INSERT INTO footballer (user_id, first_name, second_name, username) VALUES(83109589, "Rinat", NULL, "plohoidurdom", NULL, NULL, NULL)')
cur.commit()
#cur.execute('CREATE TABLE footballer_visit (id INTEGER PRIMARY KEY, user_id INTEGER, visit BOOLEAN, resp_date DATETIME)')
#con.commit()
#cur.execute('INSERT INTO footballer_visit (id, user_id, visit, resp_date) VALUES(1, 83109589, 1, "2016-03-28 15:05:59")')
#con.commit()
print cur.lastrowid

cur.execute('SELECT * FROM footballer')
print cur.fetchall()
cur.close()