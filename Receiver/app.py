from datetime import datetime
import json
import swagger_ui_bundle
import connexion
import requests
from connexion import NoContent
import yaml
import logging
import logging.config
import random
from pykafka import KafkaClient
import time
import os

def create_kafka_connection():
    app_config, logger, kafka_server, kafka_port, kafka_topic, retries, sleep_sec = load_config()

    retry_count = 0
    while retry_count < retries:
        logger.info(f'Trying to connect to Kafka. Retries: {retry_count}')
        try:
            client = KafkaClient(hosts=f'{kafka_server}:{kafka_port}')
            topic = client.topics[str.encode(kafka_topic)]
            return client, topic
        except:
            logger.error(f'Connection failed.')
            time.sleep(sleep_sec)
            retry_count += 1

def load_config():

    if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
        print("In Test Environment")
        app_conf_file = "/config/app_conf.yml"
        log_conf_file = "/config/log_conf.yml"
    else:
        print("In Dev Environment")
        app_conf_file = "app_conf.yml"
        log_conf_file = "log_conf.yml"

    with open(app_conf_file, 'r') as f:
        app_config = yaml.safe_load(f.read())

    with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)

    logger = logging.getLogger('basicLogger')

    logger.info(f'App Conf File: {app_conf_file}')
    logger.info(f'Log Conf FIle: {log_conf_file}')

    kafka_server = app_config['events']['hostname']

    kafka_port = app_config['events']['port']

    topic = app_config['events']['topic']

    retries = app_config['events']['retries']

    sleep_sec = app_config['events']['sleep']

    return app_config, logger, kafka_server, kafka_port, topic, retries, sleep_sec

def post_trade(body):

    app_config, logger, kafka_server, kafka_port, topic, retries, sleep_sec = load_config()

    post_trade_url = app_config['posttrade']['url']

    headers = {"Content-Type": "application/json; charset=utf-8"}

    trace_id = body['trace_id']

    logger.info(f'Received event post_trade request with a trace id of {trace_id}')

    client, topic = create_kafka_connection()
    producer = topic.get_sync_producer()
    msg = {"type": "posted_trade",
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Returned event post_trade response (Id: {trace_id}) with status code 201')

    return NoContent, 201

def accept_trade(body):

    app_config, logger, kafka_server, kafka_port, topic, retries, sleep_sec = load_config()

    accept_trade_url = app_config['accepttrade']['url']

    headers = {"Content-Type": "application/json; charset=utf-8"}

    trace_id = body['trace_id']

    logger.info(f'Received event accept_trade request with a trace id of {trace_id}')

    client, topic = create_kafka_connection()
    producer = topic.get_sync_producer()
    msg = {"type": "accepted_trade",
            "datetime": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))

    logger.info(f'Returned event accept_trade response (Id: {trace_id}) with status code 201')

    return NoContent, 201

def health_check():
    """ Health Check """

    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api('pokeTrader.yaml', base_path="/receiver", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    app.run(port=8080)
