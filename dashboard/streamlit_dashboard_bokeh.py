import streamlit as st
import time
import pandas as pd
from kafka import KafkaConsumer
import json
from threading import Thread
from collections import defaultdict, deque
from queue import Queue
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource
from bokeh.layouts import column
from bokeh.io import push_notebook


# Kafka topics
SENSOR_TOPIC = 'sensor-data'
PRED_TOPIC = 'predictions'
BOOTSTRAP_SERVERS = ['localhost:9092']

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
    'sensor_21'
]

OP_SETTINGS = FEATURES[1:4]
SENSORS = FEATURES[4:]

sensor_data = defaultdict(lambda: deque(maxlen=100))
prediction_data = defaultdict(lambda: deque(maxlen=100))

sensor_queue = Queue()
prediction_queue = Queue()

# Kafka Consumer thread for consuming data


def consume_kafka(topic, queue):
    consumer = KafkaConsumer(
        topic,
        group_id=f'dashboard-group-{int(time.time())}',
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        auto_offset_reset='earliest',
        consumer_timeout_ms=1000  # retry if no messages
    )
    print(f"[{topic}] Consumer started. Subscription: {consumer.subscription()}")

    while True:
        msg_pack = consumer.poll(timeout_ms=1000)
        for tp, messages in msg_pack.items():
            for message in messages:
                queue.put(message.value)


# Start Kafka consumers in background threads
Thread(target=consume_kafka, args=(
    SENSOR_TOPIC, sensor_queue), daemon=True).start()
Thread(target=consume_kafka, args=(
    PRED_TOPIC, prediction_queue), daemon=True).start()

# Streamlit app
st.set_page_config(
    page_title="Predictive Maintenance Dashboard", layout="wide")
st.title("🛠️ Predictive Maintenance - Live Dashboard")
st.markdown(
    "This dashboard visualizes sensor data and predicted RUL for each machine unit.")

# Live data storage
sensor_data = defaultdict(lambda: deque(maxlen=100))
prediction_data = defaultdict(lambda: deque(maxlen=100))

# Create Bokeh plot
sensor_source = ColumnDataSource(data=dict(x=[], y=[]))
rul_source = ColumnDataSource(data=dict(x=[], y=[]))

# Initialize Bokeh plot
sensor_plot = figure(title="Sensor Data", x_axis_label='Time',
                     y_axis_label='Sensor Value', tools="pan,box_zoom,reset,save")
sensor_plot.line('x', 'y', source=sensor_source, line_width=2,
                 color="blue", legend_label="Sensor Value")

rul_plot = figure(title="Predicted RUL", x_axis_label='Time',
                  y_axis_label='Predicted RUL', tools="pan,box_zoom,reset,save")
rul_plot.line('x', 'y', source=rul_source, line_width=2,
              color="red", legend_label="Predicted RUL")

# Layout
layout = column(sensor_plot, rul_plot)
st.bokeh_chart(layout, use_container_width=True)

placeholder = st.empty()

# Function to update data


def update_data():
    while not sensor_queue.empty():
        data = sensor_queue.get()
        uid = data["unit_id"]
        sensor_data[uid].append(
            {"timestamp": data["timestamp"], **data["sensor_data"]})

    while not prediction_queue.empty():
        pred = prediction_queue.get()
        uid = pred["unit_id"]
        prediction_data[uid].append(
            {"timestamp": pred["timestamp"], "rul": pred["predicted_rul"]})

    # Prepare data for Bokeh
    for unit_id in sorted(sensor_data.keys()):
        sensor_list = list(sensor_data[unit_id])
        if sensor_list:
            df_sensors = pd.DataFrame(sensor_list)
            df_sensor_melted = df_sensors.melt(
                id_vars=["timestamp"], value_vars=SENSORS, var_name="Sensor", value_name="Value")
            latest_sensor_data = df_sensor_melted[['timestamp', 'Value']].tail(
                100)  # Latest 100 data points
            sensor_source.data = {
                'x': latest_sensor_data['timestamp'],
                'y': latest_sensor_data['Value']
            }

        rul_list = list(prediction_data[unit_id])
        if rul_list:
            df_rul = pd.DataFrame(rul_list)
            latest_rul_data = df_rul[['timestamp', 'rul']].tail(
                100)  # Latest 100 data points
            rul_source.data = {
                'x': latest_rul_data['timestamp'],
                'y': latest_rul_data['rul']
            }


# Update loop
while True:
    update_data()
    push_notebook()
    time.sleep(1)
