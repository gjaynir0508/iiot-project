import streamlit as st
import time
import pandas as pd
from kafka import KafkaConsumer
import json
from threading import Thread
from collections import defaultdict, deque
from queue import Queue
import altair as alt


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

placeholder = st.empty()

while True:
    # Collect sensor data
    while not sensor_queue.empty():
        data = sensor_queue.get()
        uid = data["unit_id"]
        sensor_data[uid].append(
            {"timestamp": data["timestamp"], **data["sensor_data"]})

    # Collect predictions
    while not prediction_queue.empty():
        pred = prediction_queue.get()
        uid = pred["unit_id"]
        prediction_data[uid].append(
            {"timestamp": pred["timestamp"], "rul": pred["predicted_rul"]})

    # Draw sensor data chart
    with placeholder.container():
        for unit_id in sorted(sensor_data.keys()):
            st.markdown(f"### 🏭 Machine {unit_id}")
            cols = st.columns([1, 2])

            # Left: Predicted RUL metric and trend
            rul_list = list(prediction_data[unit_id])
            if rul_list:
                current_rul = rul_list[-1]['rul']
                df_rul = pd.DataFrame(rul_list)
                cols[0].metric(
                    "Predicted RUL", f"{current_rul:.2f}",
                    # current_rul - rul_list[-2]['rul'] if len(rul_list) > 1 else None
                )
                with cols[0].expander("RUL Trend"):
                    df_rul_melted = df_rul.melt(
                        id_vars=["timestamp"], value_vars=["rul"], var_name="Metric", value_name="Value")
                    chart = alt.Chart(df_rul_melted).mark_line().encode(
                        x='timestamp:T',
                        y='Value:Q',
                        color='Metric:N'
                    ).properties(
                        width=300,
                        height=300
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)

            # Right: Sensor Charts Grid (2 rows x 7 columns)
            sensor_list = list(sensor_data[unit_id])
            if sensor_list:
                df_sensors = pd.DataFrame(sensor_list)
                chart_cols = cols[1].columns(2)
                with chart_cols[0]:
                    st.subheader("Sensor Readings")
                    df_sensor_melted = df_sensors.melt(
                        id_vars=["timestamp"], value_vars=SENSORS, var_name="Sensor", value_name="Value")
                    chart = alt.Chart(df_sensor_melted).mark_line().encode(
                        x='timestamp:T',
                        y='Value:Q',
                        color='Sensor:N'
                    ).properties(
                        width=700,
                        height=300
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
                with chart_cols[1]:
                    st.subheader("Operational Settings")
                    df_op_settings_melted = df_sensors.melt(
                        id_vars=["timestamp"], value_vars=OP_SETTINGS, var_name="Setting", value_name="Value")
                    chart = alt.Chart(df_op_settings_melted).mark_line().encode(
                        x='timestamp:T',
                        y='Value:Q',
                        color='Setting:N'
                    ).properties(
                        width=700,
                        height=300
                    ).interactive()
                    st.altair_chart(chart, use_container_width=True)
            st.markdown("---")

    time.sleep(1)
