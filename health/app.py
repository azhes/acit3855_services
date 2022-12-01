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
from datetime import datetime

from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

filename = app_config['datastore']['filename']
timeout_sec = app_config['scheduler']['period sec']
url = app_config['eventstore']['url']

with open(log_conf_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
  
logger = logging.getLogger('basicLogger')
logger.info(f'Log Conf FIle: {log_conf_file}')

def health_check():
    # Poll GET /health endpoints of each service

    logger.info("Start Periodic Health Check")

    receiver = requests.get(f"{url}/receiver/health", timeout=5)
    storage = requests.get(f"{url}/storage/health", timeout=5)
    processing = requests.get(f"{url}/processing/health", timeout=5)
    audit = requests.get(f"{url}/audit_log/health", timeout=5)

    receiver_health = "Down"
    storage_health = "Down"
    processing_health = "Down"
    audit_health = "Down"

    if receiver.status_code == 200:
        receiver_health = "Running"
    if storage.status_code == 200:
        storage_health = "Running"
    if processing.status_code == 200:
        processing_health = "Running"
    if audit.status_code == 200:
        audit_health = "Running"

    health_check_json = {"health_checks:": [
                            {
                            "receiver": receiver_health,
                            "storage": storage_health,
                            "processing": processing_health,
                            "audit": audit_health,
                            "last_update": str(datetime.now())
                            }
                            ]
                        }

    logger.info('Health status of all services retrieved.')
    logger.debug(health_check_json)

    json_string = json.dumps(health_check_json)

    with open(filename, 'r+') as f:
        data = json.load(f)
        data["health_checks"].append(json_string)
        f.seek(0)
        json.dump(data, f, indent=4)
    
    logger.info('Health check written to JSON')

    return health_check_json
    

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