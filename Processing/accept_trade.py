from inspect import trace
from sqlalchemy import Column, Integer, String, DateTime
from base import Base
from datetime import datetime

class AcceptTrade(Base):
    """ Trade Accepting """

    __tablename__ = "accepted_trades"

    accepted_trade_id = Column(Integer, primary_key=True)
    pokemon_to_accept = Column(String(250), nullable=False)
    username = Column(String(250), nullable=False)
    pokemon_atk = Column(Integer, nullable=False)
    pokemon_happiness = Column(Integer, nullable=False)
    pokemon_hp = Column(Integer, nullable=False)
    pokemon_level = Column(Integer, nullable=False)
    date_created = Column(String(200), nullable=False)
    trace_id = Column(Integer, nullable=False)


    def __init__(self, accepted_trade_id, pokemon_to_accept, username, pokemon_atk, pokemon_happiness, pokemon_hp, pokemon_level, trace_id):
        """ Initializes an accepted trade """
        self.accepted_trade_id = accepted_trade_id
        self.pokemon_to_accept = pokemon_to_accept
        self.username = username
        self.pokemon_atk = pokemon_atk
        self.pokemon_happiness = pokemon_happiness
        self.pokemon_hp = pokemon_hp
        self.pokemon_level = pokemon_level
        self.date_created = datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id


    def to_dict(self):
        """ Dictionary representation of an accepted trade """
        dict = {}
        dict['accepted_trade_id'] = self.accepted_trade_id
        dict['pokemon_to_accept'] = self.pokemon_to_accept
        dict['username'] = self.username
        dict['pokemon_atk'] = self.pokemon_atk
        dict['pokemon_happiness'] = self.pokemon_happiness
        dict['pokemon_hp'] = self.pokemon_hp
        dict['pokemon_level'] = self.pokemon_level
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict