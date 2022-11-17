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
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from post_trade import PostTrade
from accept_trade import AcceptTrade

from pykafka.exceptions import SocketDisconnectedError, LeaderNotAvailable

import requests
import time
import os

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

user = app_config['datastore']['user']
password = app_config['datastore']['password']
hostname = app_config['datastore']['hostname']
port = app_config['datastore']['port']
db = app_config['datastore']['db']
kafka_hostname = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']
retries = app_config['datastore']['retries']
sleep_sec = app_config['datastore']['sleep']

DB_ENGINE = create_engine(f'mysql+pymysql://{user}:{password}@{hostname}:{port}/{db}')
DB_SESSION = sessionmaker(bind=DB_ENGINE)

with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

logger.info(f'App Conf File: {app_conf_file}')
logger.info(f'Log Conf FIle: {log_conf_file}')

def post_trade(body):

    session = DB_SESSION()

    logger.info(f'Connecting to DB. Hostname:{hostname}, Port:{port}')

    trade_post = PostTrade(
        body['trade_id'],
        body['pokemon_to_trade'],
        body['pokemon_happiness'],
        body['pokemon_level'],
        body['trade_accepted'],
        body['pokemon_def'],
        body['pokemon_speed'],
        body['trace_id']
    )

    session.add(trade_post)

    session.commit()
    session.close()

    trace_id = body['trace_id']

    logger.info(f'Stored event post_trade request with a trace id of {trace_id}')

def get_posted_trades(timestamp):
    # Gets new posted trades after the timestamp
    session = DB_SESSION()

    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    trades = session.query(PostTrade).filter(PostTrade.date_created >= timestamp_datetime)

    results_list = []

    for trade in trades:
        results_list.append(trade.to_dict())

    session.close()

    logger.info("Query for Posted Trades after %s returns %d results" %(timestamp, len(results_list)))

    return results_list, 200

def accept_trade(body):

    # create an instance of the event using SQLAlchemy declarative
    # object should be added and committed to db session
    # create and close the session

    session = DB_SESSION()

    trade_accept = AcceptTrade(
        body['accepted_trade_id'],
        body['pokemon_to_accept'],
        body['username'],
        body['pokemon_atk'],
        body['pokemon_happiness'],
        body['pokemon_hp'],
        body['pokemon_level'],
        body['trace_id']
    )

    session.add(trade_accept)

    session.commit()
    session.close()

    trace_id = body['trace_id']

    logger.info(f'Stored event accept_trade request with a trace id of {trace_id}')

def get_accepted_trades(timestamp):
    # Gets new posted trades after the timestamp
    session = DB_SESSION()

    timestamp_datetime = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")

    trades = session.query(AcceptTrade).filter(AcceptTrade.date_created >= timestamp_datetime)

    results_list = []

    for trade in trades:
        results_list.append(trade.to_dict())

    session.close()

    logger.info("Query for Accepted Trades after %s returns %d results" %(timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    """ Process event messages """

    hostname = f'{kafka_hostname}:{kafka_port}'

    retry_count = 0
    while retry_count < retries:
        logger.info(f'Trying to connect to Kafka. Retries: {retry_count}')
        try:
            client = KafkaClient(hosts=hostname)
            topic = client.topics[str.encode(kafka_topic)]
            consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=False,
                                        auto_offset_reset=OffsetType.LATEST)

            # This is blocking - it will wait for a new message
            for msg in consumer:
                msg_str = msg.value.decode('utf-8')
                msg = json.loads(msg_str)
                logger.info(f'Message: {msg}')

                payload = msg['payload']
                logger.info(f'Payload: {payload}')

                if msg['type'] == "posted_trade":
                    post_trade(payload)
                elif msg['type'] == "accepted_trade":
                    accept_trade(payload)

                consumer.commit_offsets()
        except:
            logger.error(f'Connection failed.')
            time.sleep(sleep_sec)
            retry_count += 1


    # Create a consume on a consumer group, that only reads new messages
    # (uncommitted mesages) when the service re-starts (i.e., it doesn't
    #  read all the old messages from the history in the message queue).

    

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('pokeTrader.yaml', strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    t1 = Thread(target=process_messages)
    t1.setDaemon(True)
    t1.start()
    app.run(port=8090)
