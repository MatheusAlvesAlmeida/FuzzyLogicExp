from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    QUEUE_NAME,
    PREFETCH_COUNT
)
from utils.core_functions import save_data_to_csv, calculate_latency
import json
import time
import pika
import sys

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')


def start_consuming(queue_name, rabbitmq_host, rabbitmq_port):
    consuming_time = 0
    count_messages = 0
    latency_sum = 0
    sample_id = 0
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
    )
    channel = connection.channel()
    initial_prefetch_count = PREFETCH_COUNT
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=initial_prefetch_count)

    print(f"Started consuming messages from queue '{queue_name}'")
    continue_consuming = True
    while continue_consuming:
        try:
            for method, properties, body in channel.consume(queue=queue_name, inactivity_timeout=1):
                if consuming_time == 0:
                    consuming_time = time.time()
                # Process the message
                received_time = time.time()
                received_message = json.loads(body.decode())
                print(f"Received message: {received_message}")
                count_messages += 1
                latency_sum += calculate_latency(
                    publish_time=received_message["timestamp"], received_time=received_time)

                channel.basic_ack(method.delivery_tag)
                if time.time() - consuming_time > 9:
                    channel.cancel()
                    print("Consumer stopped to save metrics.")
                    save_data_to_csv(
                        prefetch_count=1,
                        average_latency=latency_sum / count_messages,
                        arrival_rate=count_messages / 10,
                        sample_number=1
                    )
                    sample_id += 1
                    if sample_id % 10 == 1:
                        new_prefetch_count = initial_prefetch_count + 3
                        channel.basic_qos(prefetch_count=new_prefetch_count)
                        if sample_id == 70:
                            print("Finished consuming messages.")
                            break
                    consuming_time = 0
                    count_messages = 0
                    latency_sum = 0
        except pika.exceptions.ChannelClosedByBroker:
            print("Channel was closed by broker. Continuing to next iteration.")
            break
