import sqlite3

conn = sqlite3.connect('trade.sqlite')

c = conn.cursor()
c.execute('''
          DROP TABLE posted_trades;
          ''')
c.execute('''
          DROP TABLE accepted_trades;
          ''')


conn.commit()
conn.close()
