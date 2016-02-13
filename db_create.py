import os
import psycopg2
import urlparse

urlparse.uses_netloc.append("d5orecc0oeod38")
url = urlparse.urlparse(os.environ["postgres://dwxpxijyrlhnyp:HeTB8Lyf3BLhYbXjHBCV1Wy9zG@ec2-54-217-202-109.eu-west-1.compute.amazonaws.com:5432/d5orecc0oeod38"])

conn = psycopg2.connect(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
)
conn.execute('CREATE TABLE footballer (user_id INTEGER PRIMARY KEY, first_name VARCHAR(30), second_name VARCHAR(30), username VARCHAR(30, visit BOOLEAN, resp_date DATETIME))')
conn.commit()
conn.execute('INSERT INTO footballer (user_id, first_name, second_name, username) VALUES(83109589, "Rinat", NULL, "plohoidurdom", NULL, NULL)')
conn.commit()
#cur.execute('CREATE TABLE footballer_visit (id INTEGER PRIMARY KEY, user_id INTEGER, visit BOOLEAN, resp_date DATETIME)')
#con.commit()
#cur.execute('INSERT INTO footballer_visit (id, user_id, visit, resp_date) VALUES(1, 83109589, 1, "2016-03-28 15:05:59")')
#con.commit()
print conn.lastrowid

conn.execute('SELECT * FROM footballer')
print conn.fetchall()
conn.close()