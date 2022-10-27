from sqlalchemy import Column, Integer, String, DateTime
from base import Base
class Stats(Base):
    """ Processing Statistics """
    __tablename__ = "stats"
    id = Column(Integer, primary_key=True)
    num_posted_trades = Column(Integer, nullable=False)
    num_accepted_trades = Column(Integer, nullable=True)
    max_posted_trades_level = Column(Integer, nullable=True)
    max_accepted_trades_happiness = Column(Integer, nullable=True)
    last_updated = Column(String(250), nullable=False)

    def __init__(self, num_posted_trades, num_accepted_trades, max_posted_trades_level, max_accepted_trades_happiness, last_updated):
        """ Initializes a processing statistics object """
        self.num_posted_trades = num_posted_trades
        self.num_accepted_trades = num_accepted_trades
        self.max_posted_trades_level = max_posted_trades_level
        self.max_accepted_trades_happiness = max_accepted_trades_happiness
        self.last_updated = last_updated
        
    def to_dict(self):
        """ Dictionary Representation of a statistics """
        dict = {}
        dict['num_posted_trades'] = self.num_posted_trades
        dict['num_accepted_trades'] = self.num_accepted_trades
        dict['max_posted_trades_level'] = self.max_posted_trades_level
        dict['max_accepted_trades_happiness'] = self.max_accepted_trades_happiness
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S")
        return dict