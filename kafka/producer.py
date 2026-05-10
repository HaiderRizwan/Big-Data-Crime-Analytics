import csv
import json
import time
import yaml
from kafka import KafkaProducer

# Load configuration
with open("config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

def json_serializer(data):
    return json.dumps(data).encode("utf-8")

def main():
    print("Starting Kafka Producer (Crime Simulator)...")
    
    # Initialize Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=[config['kafka']['bootstrap_servers']],
        value_serializer=json_serializer
    )

    topic_name = config['kafka']['topic_name']
    rate = config['kafka']['producer_rate']
    csv_file = "data/crime_data.csv"

    try:
        with open(csv_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Prepare message with mandatory fields
                try:
                    message = {
                        "case_number": row.get("case_number"),
                        "date": row.get("date"),
                        "block": row.get("block"),
                        "primary_type": row.get("primary_type"),
                        "district": row.get("district"),
                        "arrest": row.get("arrest"),
                        "latitude": row.get("latitude"),
                        "longitude": row.get("longitude")
                    }
                    
                    # Publish to Kafka
                    producer.send(topic_name, value=message)
                    print(f"Sent: {message['case_number']} from District {message['district']}")
                    
                    # Control the rate
                    time.sleep(rate)
                except Exception as e:
                    print(f"Error processing row: {e}")
                    continue

    except FileNotFoundError:
        print(f"Error: {csv_file} not found. Please ensure the data is in the 'data/' directory.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        producer.close()

if __name__ == "__main__":
    main()
