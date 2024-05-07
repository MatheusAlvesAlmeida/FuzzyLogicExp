import json
import time
import pika
import sys

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    QUEUE_NAME,
    EXCHANGE_NAME,
    PREFETCH_COUNT
)

global consuming_time

# def on_message_received(channel, method, properties, body):
#     print(f"Received message: {body.decode()}")
#     if consuming_time == 0:
#         consuming_time = time.time()
#     channel.basic_ack(delivery_tag=method.delivery_tag)
#     if time.time() - consuming_time > 9:
#         print("Consumer stopped due to timeout.")
#         channel.stop_consuming()

def start_consuming(queue_name, rabbitmq_host, rabbitmq_port):
    consuming_time = 0
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
    )
    channel = connection.channel()

    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=1)
    #channel.basic_consume(queue=queue_name, on_message_callback=on_message_received)

    print(f"Started consuming messages from queue '{queue_name}'")
    for method, properties, body in channel.consume(queue=queue_name, inactivity_timeout=1):
        print(f"Received message: {body.decode()}")
        channel.basic_ack(method.delivery_tag)
        if consuming_time == 0:
            consuming_time = time.time()
        if time.time() - consuming_time > 9:
            print("Consumer stopped due to timeout.")
            channel.cancel()

if __name__ == "__main__":
    queue_name = QUEUE_NAME
    rabbitmq_host = RABBITMQ_HOST
    rabbitmq_port = RABBITMQ_PORT

    start_consuming(queue_name, rabbitmq_host, rabbitmq_port)

