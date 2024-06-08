import json
import time
import pika
import sys

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')
from utils.core_functions import save_data_to_csv, calculate_latency
from shared.shared import (
    RABBITMQ_HOST,
    RABBITMQ_PORT,
    QUEUE_NAME,
    PREFETCH_COUNT
)
from controllers.fuzzy_controller import FuzzyController


def start_consuming(queue_name, rabbitmq_host, rabbitmq_port):
    fuzzy_controller = FuzzyController()
    consuming_time = 0
    count_messages = 0
    latency_sum = 0
    sample_id = 1
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)
    )
    channel = connection.channel()
    prefetch_count = PREFETCH_COUNT
    channel.queue_declare(queue=queue_name)
    channel.basic_qos(prefetch_count=prefetch_count)

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
                #print(f"Received message: {received_message}")
                count_messages += 1
                latency_sum += calculate_latency(
                    publish_time=received_message["timestamp"], received_time=received_time)
                channel.basic_ack(method.delivery_tag)
                time_passed = time.time() - consuming_time
                if time_passed >= 5:
                    channel.cancel()
                    print("Consumer stopped to save metrics.")
                    save_data_to_csv(
                        prefetch_count=prefetch_count,
                        #average_latency=latency_sum / count_messages,
                        arrival_rate=count_messages / time_passed,
                        sample_number=sample_id
                    )
                    print(f"""
                        Sample {sample_id}:
                        Prefetch count: {prefetch_count}
                        Average latency: {latency_sum / count_messages}
                        Arrival rate: {count_messages / time_passed}
                    """)
                    sample_id += 1
                    if sample_id % 30 == 0:
                        prefetch_count = prefetch_count + 1
                        channel.basic_qos(prefetch_count=prefetch_count)
                    if sample_id == 450:
                        continue_consuming = False
                        sys.exit(0)
                    consuming_time = 0
                    count_messages = 0
                    latency_sum = 0
        except pika.exceptions.ChannelClosedByBroker:
            print("Channel was closed by broker. Continuing to next iteration.")
            break
