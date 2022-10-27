from sqlalchemy import Column, Integer, String, DateTime
from base import Base
from datetime import datetime

class PostTrade(Base):
    """ Trade Posting """

    __tablename__ = "posted_trades"

    trade_id = Column(Integer, primary_key=True)
    pokemon_to_trade = Column(String(250), nullable=False)
    pokemon_happiness = Column(Integer, nullable=False)
    pokemon_level = Column(Integer, nullable=False)
    trade_accepted = Column(String(10), nullable=False)
    pokemon_def = Column(Integer, nullable=False)
    pokemon_speed = Column(Integer, nullable=False)
    date_created = Column(String(200), nullable=False)
    trace_id = Column(Integer, nullable=False)

    def __init__(self, trade_id, pokemon_to_trade, pokemon_happiness, pokemon_level, trade_accepted, pokemon_def, pokemon_speed, trace_id):
        """ Initializes a posted trade """
        self.trade_id = trade_id
        self.pokemon_to_trade = pokemon_to_trade
        self.pokemon_happiness = pokemon_happiness
        self.pokemon_level = pokemon_level
        self.trade_accepted = trade_accepted
        self.pokemon_def = pokemon_def
        self.pokemon_speed = pokemon_speed
        self.date_created = datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id


    def to_dict(self):
        """ Dictionary representation of a posted trade """
        dict = {}
        dict['trade_id'] = self.trade_id
        dict['pokemon_to_trade'] = self.pokemon_to_trade
        dict['pokemon_level'] = self.pokemon_level
        dict['trade_accepted'] = self.trade_accepted
        dict['pokemon_def'] = self.pokemon_def
        dict['pokemon_speed'] = self.pokemon_speed
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
