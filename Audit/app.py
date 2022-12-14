import json
import swagger_ui_bundle
import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
from pykafka import KafkaClient
from pykafka.common import OffsetType
from flask_cors import CORS, cross_origin
import math
import os
from itertools import islice

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

kafka_hostname = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']

with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
   
logger = logging.getLogger('basicLogger')

logger.info(f'App Conf File: {app_conf_file}')
logger.info(f'Log Conf FIle: {log_conf_file}')

def get_posted_trade(index):
    """ Get posted trade in history """
    hostname = f'{kafka_hostname}:{kafka_port}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(kafka_topic)]

    """ Here we reset the offset on start so that we retrieve
    messages at the beginning of the message queue. To prevent
    the for loop from blocking, we set the timeout to 1000ms.
    There is a risk that this loop never stops if the index
    is large and messages are constantly being received. """

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info(f'Retrieving posted trade at {index}')
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg_json = json.loads(msg_str)

            if msg.offset == index:
                return msg_json, 200

    except:
        logger.error("No more messages found")

    logger.error(f"could not find a posted trade at index {index}")
    return {"message": "Not Found"}, 404

def get_accepted_trade(index):
    """ Get accepted trade in history """
    hostname = f'{kafka_hostname}:{kafka_port}'
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(kafka_topic)]

    """ Here we reset the offset on start so that we retrieve
    messages at the beginning of the message queue. To prevent
    the for loop from blocking, we set the timeout to 1000ms.
    There is a risk that this loop never stops if the index
    is large and messages are constantly being received. """

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info(f'Retrieving accepted trade at {index}')
    try:
        for msg in consumer:
            logger.debug(msg.offset)
            msg_str = msg.value.decode('utf-8')
            msg_json = json.loads(msg_str)

            if msg.offset == index:
                return msg_json, 200

    except:
        logger.error("No more messages found")

    logger.error(f"could not find an accepted trade at index {index}")
    return {"message": "Not Found"}, 404

def health_check():
    """ Health Check """

    logger.info(f'Health check initiated.')

    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
#if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('pokeTrader.yaml', base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    app.run(port=8110)
