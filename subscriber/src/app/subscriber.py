import sys
import threading
import time

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    QUEUE_NAME
)

consumer_thread = None  # Global variable to store the consumer thread

def start_consumer():
    global consumer_thread
    consumer_thread = threading.Thread(target=run_consumer)
    consumer_thread.start()
    print("Consumer started.")

def run_consumer():
    import messaging_manager
    messaging_manager.start_consuming(queue_name=QUEUE_NAME, rabbitmq_host=RABBITMQ_HOST, rabbitmq_port=RABBITMQ_PORT)


if __name__ == "__main__":
    start_consumer()

    start_consuming_time = 0
    while True:
        time.sleep(1)
        

