import pika
import json
import time
import sys
import os

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/publisher/src')
from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
    QUEUE_NAME
)

def prepare_message():
    message_data = {
        "message": "Hello World!",
        "timestamp": time.time()
    }
    message_body = json.dumps(message_data).encode()
    return message_data, message_body

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME)

while True:
    message_data, message_body = prepare_message()
    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=message_body)
    print(f" [x] Sent message with timestamp: {message_data['timestamp']}") 

connection.close()
