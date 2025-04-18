import streamlit as st
import time
import pandas as pd
from kafka import KafkaConsumer
import json
from threading import Thread
from collections import defaultdict
import pandas as pd


# Kafka topics
SENSOR_TOPIC = 'sensor-data'
PRED_TOPIC = 'predictions'
BOOTSTRAP_SERVERS = ['localhost:9092']

sensor_data = defaultdict(lambda: pd.DataFrame())
prediction_data = defaultdict(lambda: pd.DataFrame())


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

# Live data storage
sensor_data = []
prediction_data = []

sensor_placeholder = st.empty()
prediction_placeholder = st.empty()

while True:
    # Collect sensor data
    while not sensor_queue.empty():
        data = sensor_queue.get()
        sensor_data.append(data)
        if len(sensor_data) > 100:
            sensor_data.pop(0)

    # Collect predictions
    while not prediction_queue.empty():
        pred = prediction_queue.get()
        prediction_data.append(pred)
        if len(prediction_data) > 100:
            prediction_data.pop(0)

    # Convert to DataFrame
    df_sensors = pd.DataFrame(sensor_data)
    df_preds = pd.DataFrame(prediction_data)

    # Draw sensor data chart
    with sensor_placeholder.container():
        st.subheader("📊 Live Sensor Readings")
        if not df_sensors.empty:
            for col in df_sensors.columns:
                if col != "timestamp":
                    st.line_chart(df_sensors[col])

    # Draw prediction
    with prediction_placeholder.container():
        st.subheader("🔮 Remaining Useful Life Prediction")
        if not df_preds.empty:
            st.dataframe(df_preds.tail(1))

    time.sleep(1)
