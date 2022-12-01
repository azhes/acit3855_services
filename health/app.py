import json
import os
import swagger_ui_bundle
import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from base import Base
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"

with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
  
logger = logging.getLogger('basicLogger')
logger.info(f'Log Conf FIle: {log_conf_file}')

def health_check():
    pass

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(health_check, 'interval', seconds=20)

    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api('pokeTrader.yaml', base_path="/health", strict_validation=True, validate_responses=True)

if __name__ == '__main__':
    init_scheduler()
    app.run(port=8120)