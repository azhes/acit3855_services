import mysql.connector

db_conn = mysql.connector.connect(host="localhost", user="root", password="Dreadnought99", database="events")

db_cursor = db_conn.cursor()

db_cursor.execute('''DROP TABLE posted_trades, accepted_trades''')

db_conn.commit()

db_conn.close()