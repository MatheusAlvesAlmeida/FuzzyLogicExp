import csv

def save_data_to_csv(prefetch_count, average_latency, arrival_rate, sample_number):
    data = [prefetch_count, average_latency, arrival_rate, sample_number]
    try:
        with open('results.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)
    except Exception as e:
        print(f"Error saving data to CSV: {e}")

def calculate_latency(publish_time, receive_time):
    return receive_time - publish_time

