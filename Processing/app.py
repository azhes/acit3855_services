from datetime import datetime
import json
from tokenize import Single
import swagger_ui_bundle
import connexion
from connexion import NoContent
import mysql.connector
import pymysql
import yaml
import logging
import logging.config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from post_trade import PostTrade
from accept_trade import AcceptTrade
from stats import Stats
from flask_cors import CORS, cross_origin

import requests
from apscheduler.schedulers.background import BackgroundScheduler

with open('app_conf.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())

filename = app_config['datastore']['filename']
period_sec = app_config['scheduler']['period sec']
url = app_config['eventstore']['url']

DB_ENGINE = create_engine('sqlite:///%s' %app_config["datastore"]["filename"])
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

def get_stats():
    """ GET endpoint for /events/stats resource """

    # Log an INFO message indicating request has started
    logger.info("Request has started")

    # Read in the current statistics from the SQLite database
    session = DB_SESSION()
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    query_results = session.execute(results).fetchall()

    current_statistics = query_results[0][0]

    # Convert the statistics as necessary into a new Python dictionary such that
    # the structure matches that of your response defined in the openapi.yaml file
    stats_dict = {'num_posted_trades': current_statistics.num_posted_trades,
                'num_accepted_trades': current_statistics.num_accepted_trades,
                'max_posted_trades_level': current_statistics.max_posted_trades_level,
                'max_accepted_trades_happiness': current_statistics.max_accepted_trades_happiness,
                'last_updated': current_statistics.last_updated}

    logger.info(f'Request has completed')

    return stats_dict, 200

def populate_stats():
    """ Periodically update stats """
    session = DB_SESSION()
    # Log an INFO message indicating periodic processing has started
    logger.info("Start Periodic Processing")

    # Read in the current statistics from the SQLite database
    results = session.query(Stats).order_by(Stats.last_updated.desc())
    query_results = session.execute(results).fetchall()

    timestamp = query_results[0][0].last_updated

    session.close()

    # Query the two GET endpoints from your data store service to get all new events
    # from the last datetime you requested them to the current datetime
    # timestamp_datetime = timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    # debug_timestamp = "2022-09-10T11:16:44Z"

    posted_trades_url = 'http://localhost:8090/posttrade?timestamp=' + timestamp

    posted_trades = requests.get(posted_trades_url)
    posted_trades_json = posted_trades.json()
    logger.info(f'{len(posted_trades_json)} trade post events received.')
    if posted_trades.status_code != 200:
        logger.error("Did not receive a 200 response code")

    accepted_trades_url = 'http://localhost:8090/accepttrade?timestamp=' + timestamp
    
    accepted_trades = requests.get(accepted_trades_url)
    accepted_trades_json = accepted_trades.json()
    logger.info(f'{len(accepted_trades_json)} trade accept events received.')
    if accepted_trades.status_code != 200:
        logger.error("Did not receive a 200 response code")

    #calculate updated statistics
    num_posted_trades = len(posted_trades_json) #num_posted_trades
    num_accepted_trades = len(accepted_trades_json) #num_accepted_trades

    #max_posted_trades_level
    try:
        posted_levels = []
        for trade in posted_trades_json:
            posted_levels.append(trade['pokemon_level'])
        max_posted_trades_level = max(posted_levels)
    except:
        max_posted_trades_level = 0

    #max_accepted_trades_happiness
    try:
        accepted_happinesses = []
        for trade in accepted_trades_json:
            accepted_happinesses.append(int(trade['pokemon_happiness']))
        max_accepted_trades_happiness = max(accepted_happinesses)
    except:
        max_accepted_trades_happiness = 0

    #new_stats_dictionary
    new_stats = {'num_posted_trades': num_posted_trades, 'num_accepted_trades': num_accepted_trades, 'max_posted_trades_level': max_posted_trades_level, 'max_accepted_trades_happiness': max_accepted_trades_happiness, 'last_updated': datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}

    #write a Stats object to the database
    session = DB_SESSION()
    stats = Stats(new_stats['num_posted_trades'], new_stats['num_accepted_trades'], new_stats['max_posted_trades_level'], new_stats['max_accepted_trades_happiness'], new_stats['last_updated'])
    logger.debug(f'Updated statistics values: {new_stats}')

    session.add(stats)

    session.commit()
    session.close()

    #log an info message indicating period processing has ended
    logger.info(f'Period processing has ended.')


def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=period_sec)

    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('pokeTrader.yaml', strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8100)