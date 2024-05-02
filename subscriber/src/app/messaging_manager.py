import pika
import sys

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from shared.shared import (
    RABBITMQ_HOST,
    EXCHANGE_NAME
)

class MessagingManager():
    def __init__(self, *args, **kwargs):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(
            exchange=EXCHANGE_NAME, 
            exchange_type='topic'
        )

    def consume(self, keys, callback):
        result = self.channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue
        for key in keys:
            self.channel.queue_bind(
                exchange=EXCHANGE_NAME, 
                queue=queue_name, 
                routing_key=key)

        self.channel.basic_consume(
            queue=queue_name, 
            on_message_callback=callback, 
            auto_ack=True)

        self.channel.start_consuming()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()
