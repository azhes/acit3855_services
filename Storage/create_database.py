import sqlite3

conn = sqlite3.connect('trade.sqlite')

c = conn.cursor()
c.execute('''
        CREATE TABLE posted_trades
        (trade_id INTEGER PRIMARY KEY ASC, 
        pokemon_to_trade VARCHAR(250) NOT NULL,
        pokemon_happiness INTEGER NOT NULL,
        pokemon_level INTEGER NOT NULL,
        trade_accepted VARCHAR(10) NOT NULL,
        pokemon_def INTEGER NOT NULL,
        pokemon_speed INTEGER NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id INTEGER NOT NULL)
        ''')

c.execute('''
        CREATE TABLE accepted_trades
        (accepted_trade_id INTEGER PRIMARY KEY ASC, 
        pokemon_to_accept VARCHAR(250) NOT NULL,
        username VARCHAR(250) NOT NULL,
        pokemon_atk INTEGER NOT NULL,
        pokemon_happiness VARCHAR(100) NOT NULL,
        pokemon_hp INTEGER NOT NULL,
        pokemon_level INTEGER NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id INTEGER NOT NULL)
        ''')

conn.commit()
conn.close()