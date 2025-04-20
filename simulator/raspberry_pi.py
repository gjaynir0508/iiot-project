import time
import json
import paho.mqtt.client as mqtt
from sensor_simulator_random_bounded import SensorDataSimulator

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
        engine_id, sensor_data = simulator.get_sensor_data()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        if sensor_data is None:
            print("Simulation complete.")
            break

        payload = json.dumps(
            {"unit_id": str(engine_id), "timestamp": timestamp, "sensor_data": sensor_data})
        client.publish(MQTT_TOPIC, payload)
        # Print first 150 chars of payload
        print(f"Published: {payload[:120]} ...")

        time.sleep(0.2)  # Simulate an interval between sensor reads

except KeyboardInterrupt:
    print("Simulation stopped.")
finally:
    client.disconnect()
