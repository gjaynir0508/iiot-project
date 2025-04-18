import time
import json
import paho.mqtt.client as mqtt
from sensor_simulator import SensorDataSimulator

MQTT_BROKER = "localhost"          # Or your MQTT broker IP
MQTT_PORT = 1883
MQTT_TOPIC = "factory/sensors"

# Initialize MQTT Client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Initialize sensor simulator
simulator = SensorDataSimulator("./CMAPSSData/train_FD001.txt")

# Publish simulated data
try:
    while True:
        sensor_data = simulator.get_sensor_data()
        if sensor_data is None:
            print("Simulation complete.")
            break

        payload = json.dumps({"unit_id": 1, "sensor_data": sensor_data})
        client.publish(MQTT_TOPIC, payload)
        print(f"Published: {payload}")

        time.sleep(1)  # Simulate 1-second interval between sensor reads

except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.disconnect()
