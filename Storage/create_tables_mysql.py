import mysql.connector

db_conn = mysql.connector.connect(host="acit3855kafka.westus3.cloudapp.azure.com", user="root", password="Dreadnought99", database="events")

c = db_conn.cursor()
c.execute('''
        CREATE TABLE posted_trades
        (trade_id INT NOT NULL AUTO_INCREMENT, 
        pokemon_to_trade VARCHAR(250) NOT NULL,
        pokemon_happiness INT NOT NULL,
        pokemon_level INT NOT NULL,
        trade_accepted VARCHAR(10) NOT NULL,
        pokemon_def INT NOT NULL,
        pokemon_speed INT NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id INT NOT NULL,
        CONSTRAINT trade_id_pk PRIMARY KEY (trade_id))
        ''')

c.execute('''
        CREATE TABLE accepted_trades
        (accepted_trade_id INT NOT NULL AUTO_INCREMENT, 
        pokemon_to_accept VARCHAR(250) NOT NULL,
        username VARCHAR(250) NOT NULL,
        pokemon_atk INT NOT NULL,
        pokemon_happiness VARCHAR(100) NOT NULL,
        pokemon_hp INT NOT NULL,
        pokemon_level INT NOT NULL,
        date_created VARCHAR(100) NOT NULL,
        trace_id INT NOT NULL,
        CONSTRAINT accepted_trade_id_pk PRIMARY KEY (accepted_trade_id))
        ''')

db_conn.commit()
db_conn.close()