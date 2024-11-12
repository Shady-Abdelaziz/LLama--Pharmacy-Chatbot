import uuid
import logging

logging.basicConfig(filename='system.log', level=logging.INFO)

def create_new_session():
    return str(uuid.uuid4())

def log_event(message):
    logging.info(message)