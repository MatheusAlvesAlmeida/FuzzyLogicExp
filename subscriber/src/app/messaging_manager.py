from controller.rules.rules_generator import GeneticAlgorithm
from controller.fuzzy_controller import FuzzyController
from shared.shared import (
    PREFETCH_COUNT
)
from utils.core_functions import save_data_to_csv
import json
import time
import pika
import sys
import concurrent.futures

sys.path.append('/home/matheus/Documentos/GIT/FuzzyLogicExp/subscriber/src')

SETPOINT = 3000

def run_genetic_algorithm(fuzzy_controller: FuzzyController):
    ga = GeneticAlgorithm()
    best_rule_set = ga.improve_rules(setpoint=SETPOINT)
    fuzzy_controller.update_rules(best_rule_set)
    print("Updated Fuzzy Controller with new rules.")
    time.sleep(2)
    return best_rule_set


def update_fuzzy_controller_parallel(fuzzy_controller: FuzzyController):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_genetic_algorithm, fuzzy_controller)


def start_consuming(queue_name, rabbitmq_host, rabbitmq_port):
    fuzzy_controller = FuzzyController(setpoint=SETPOINT)
    consuming_time = 0
    count_messages = 0
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
            update_fuzzy_controller_parallel(fuzzy_controller)
            for method, properties, body in channel.consume(queue=queue_name, inactivity_timeout=1):
                if consuming_time == 0:
                    consuming_time = time.time()

                if body is not None:
                    # Process the message
                    count_messages += 1

                    channel.basic_ack(method.delivery_tag)
                    time_passed = time.time() - consuming_time
                    if time_passed >= 5:
                        channel.cancel()
                        print("Consumer stopped to save metrics.")
                        save_data_to_csv(
                            prefetch_count=prefetch_count,
                            arrival_rate=count_messages / time_passed,
                            sample_number=sample_id,
                            setpoint=SETPOINT
                        )
                        print(f"""
                            Sample {sample_id}:
                            Prefetch count: {prefetch_count}
                            Arrival rate: {count_messages / time_passed}
                            Setoint: {SETPOINT}
                        """)
                        sample_id += 1
                        # Evaluate new prefetch count
                        new_prefetch_count = fuzzy_controller.evaluate_new_prefetch_count(prefetch_count, count_messages / time_passed)
                        channel.basic_qos(prefetch_count=new_prefetch_count)
                        if sample_id == 450:
                            continue_consuming = False
                            sys.exit(0)
                        consuming_time = 0
                        count_messages = 0
                        prefetch_count = new_prefetch_count
        except pika.exceptions.ChannelClosedByBroker:
            print("Channel was closed by broker. Continuing to next iteration.")
            break
