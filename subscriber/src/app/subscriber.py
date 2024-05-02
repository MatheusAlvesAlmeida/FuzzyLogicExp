import json
import threading
import time
import sys
import os
import logging

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    RABBITMQ_USERNAME,
    QUEUE_NAME,
    PREFETCH_COUNT
)
from utils.core_functions import save_data_to_csv, calculate_latency
from messaging_manager import MessagingManager

logging.basicConfig(level=logging.INFO)
global consumer_thread 

def main():
    msg_count = [0]
    latency_data = []
    is_consuming = True  # Flag to control consumer

    def start_consuming():
        def callback(ch, method, properties, body):
            receive_time = time.time()
            msg_count[0] += 1

            message_data = json.loads(body)
            publish_time = message_data.get('timestamp')

            latency = calculate_latency(publish_time, receive_time)
            latency_data.append(latency)

            logging.info(f"""
                [x] 
                The publish time is: {publish_time}.
                Received message with timestamp: {receive_time}.
                Latency: {latency:.5f} seconds
            """)
        with MessagingManager() as consumer:
            consumer.consume([QUEUE_NAME], callback)

    arrival_rate = 0
    sample = 0
    start_counting_time = 0
    
    consumer_thread = threading.Thread(target=start_consuming)
    consumer_thread.start()
    while True:
        print("Start consuming")
        print(f"msg_count: {msg_count[0]}")
        if start_counting_time == 0:
            start_counting_time = time.time()

        if time.time() - start_counting_time >= 10:
            print("Stop consuming")
            is_consuming = False  # Set flag to stop the consumer thread loop
            consumer_thread.join()  # Wait for the thread to finish consuming messages

            arrival_rate = msg_count[0] / 10
            average_latency = sum(latency_data) / msg_count[0]

            save_data_to_csv(
                PREFETCH_COUNT,
                average_latency,
                arrival_rate,
                sample
            )

            # Reset the counting
            start_counting_time = 0
            msg_count[0] = 0
            latency_data = []
            arrival_rate = 0
            sample += 1

            is_consuming = True  # Reset flag for next consumption cycle

            if sample == 30:
                break

            print("Start consuming again")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            is_consuming = False  # Set flag to stop consumer thread before exiting
            consumer_thread.join()
            sys.exit(0)
        except SystemExit:
            os._exit(0)
