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

with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

kafka_hostname = app_config['events']['hostname']
kafka_port = app_config['events']['port']
kafka_topic = app_config['events']['topic']

with open('log_conf.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    
logger = logging.getLogger('basicLogger')

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

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                        reset_offset_on_start=True,
                                        consumer_timeout_ms=1000)

    logger.info(f'Retrieving posted trade at {index}')
    logger.debug(f'Requested trade: {consumer[index]}')
    try:
        for msg in consumer:
            
            msg_str = msg.value.decode('utf-8')
            msg_json = json.loads(msg_str)

            # Find the event at the index you want and return code 200
            return msg_json, 200
    except:
        logger.error("No more messages found")

    logger.error(f"could not find a posted trade at index {index}")
    return {"message": "Not Found"}, 404

def get_accepted_trade(index):
    """ Get accepted trade in history """
    hostname = kafka_hostname
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
            msg_str = msg.value.decode('utf-8')
            msg_json = json.loads(msg_str)

            # Find the event at the index you want and return code 200
            if msg == consumer[index]:
                return msg_json, 200
    except:
        logger.error("No more messages found")

    logger.error(f"could not find an accepted trade at index {index}")
    return {"message": "Not Found"}, 404

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('pokeTrader.yaml', strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    app.run(port=8110)