import csv

def logging_pc_changes(setpoint, arrival_rate, error_value, prefetch_count, new_prefetch_count):
    data = [setpoint, arrival_rate, error_value, prefetch_count, new_prefetch_count]
    try:
        with open('pc_changes.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
        print(f"Prefetch count changed from {prefetch_count} to {new_prefetch_count} based on error value {error_value}. The setpoint is {setpoint}")
    except Exception as e:
        print(f"Error logging PC changes: {e}")

def save_data_to_csv(prefetch_count, average_latency, arrival_rate, sample_number):
    data = [prefetch_count, average_latency, arrival_rate, sample_number]
    try:
        with open('results.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def calculate_latency(publish_time, received_time):
    return received_time - publish_time

