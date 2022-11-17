import sqlite3

def create_tables():

    conn = sqlite3.connect('data.sqlite')

    c = conn.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS stats
                (id INTEGER PRIMARY KEY ASC,
                num_posted_trades INTEGER NOT NULL,
                num_accepted_trades INTEGER NOT NULL,
                max_posted_trades_level INTEGER,
                max_accepted_trades_happiness INTEGER,
                last_updated VARCHAR(100) NOT NULL) 
                ''')

    conn.commit()
    conn.close()