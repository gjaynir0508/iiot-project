import json
from kafka import KafkaProducer
import paho.mqtt.client as mqtt

# MQTT settings
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "factory/sensors"

# Kafka settings
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "sensor-data"

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# MQTT callback


def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"[MQTT] Received: {payload}")
        producer.send(KAFKA_TOPIC, value=payload)
        print(f"[Kafka] Sent to topic '{KAFKA_TOPIC}'")
    except Exception as e:
        print(f"[Error] {e}")


# MQTT client setup
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever()
