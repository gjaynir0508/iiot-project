from kafka import KafkaConsumer, KafkaProducer
import requests
import json
import time

# Kafka setup
SENSOR_TOPIC = 'sensor-data'
PREDICTION_TOPIC = 'predictions'
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'

consumer = KafkaConsumer(
    SENSOR_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='rul_predictor'
)

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda m: json.dumps(m).encode('utf-8')
)

# FastAPI inference server endpoint
INFERENCE_URL = "http://localhost:8000/predict"

print("Kafka RUL prediction service started...")

# Buffer to hold the last 50 cycles (for the sliding window)
cycle_buffer = []


def publish_prediction(prediction_result):
    """Publish predictions to Kafka."""
    producer.send(PREDICTION_TOPIC, prediction_result)
    print(f"[✓] Published prediction: {prediction_result}")


FEATURES = [
    'cycle',
    'op_setting_1',
    'op_setting_2',
    'op_setting_3',
    'sensor_2',
    'sensor_3',
    'sensor_4',
    'sensor_7',
    'sensor_8',
    'sensor_11',
    'sensor_15',
    'sensor_17',
    'sensor_20',
    'sensor_21']

for msg in consumer:
    sensor_data = msg.value
    try:
        # Each message contains 1 cycle (1 timestep)
        cycle = sensor_data.get("sensor_data")
        useful_features_only = [cycle[f] for f in FEATURES]
        cycle = useful_features_only if useful_features_only else None

        # 14 features per cycle (14 sensor readings)
        if not cycle or len(cycle) != len(FEATURES):
            # Skip this cycle if it doesn't have the right number of features
            print(
                f"[✗] Invalid cycle data. Skipping this cycle.")
            continue

        # TODO Complete: Remove below line. (removing the cycle number from the features until the model is updated)
        # cycle = cycle[1:]
        # Append cycle to buffer
        cycle_buffer.append(cycle)

        # If we have 50 cycles in the buffer, send the sequence for prediction
        if len(cycle_buffer) >= 50:
            # Prepare the sequence for inference (50 cycles, each with 13 features)
            sequence_data = {
                "unit_id": sensor_data["unit_id"], "timestamp": sensor_data["timestamp"], "sequence": cycle_buffer[-50:]}

            # Print the first 100 characters of the sequence data
            print(str(sequence_data)[:120] + "...")

            # Send to inference server
            response = requests.post(INFERENCE_URL, json=sequence_data)

            if response.status_code == 200:
                prediction_result = response.json()
                print(
                    f"[✓] Inference result: {prediction_result}")
                publish_prediction(prediction_result)
            else:
                print(
                    f"[✗] Error from inference server: {response.status_code}, {response.text}")

            # Slide the window by 1 (remove the first cycle and add a new cycle in the next iteration)
            cycle_buffer = cycle_buffer[1:]

    except Exception as e:
        producer.flush()
        print(f"[!] Exception while processing message: {e}")

    time.sleep(0.1)  # Optional: throttle processing
