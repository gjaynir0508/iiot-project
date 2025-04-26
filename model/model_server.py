from sklearn.preprocessing import MinMaxScaler
import pandas as pd
from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.initializers import Orthogonal
import uvicorn

import pickle

app = FastAPI()

# Load model
model = tf.keras.models.load_model(
    "./model/lstm_fd001.keras", custom_objects={'Orthogonal': Orthogonal})

# Load scaler
# Assuming the scaler was saved using pickle
scaler = pickle.load(open("./model/scaler.pkl", "rb"))

# Define input shape expected by model
SEQ_LENGTH = 50
N_FEATURES = 14  # number of sensors you're using
# TODO Complete: Update this to 14 once the model is trained with the new data

# Define request schema


class SensorData(BaseModel):
    unit_id: str  # Unique identifier for the unit
    timestamp: str  # ISO format string
    # Assuming the sequence is a list of lists, each containing float values
    # list of sensor readings, each is a list of floats
    sequence: list[list[float]]


@app.post("/predict")
async def predict(data: SensorData):
    seq = np.array(data.sequence, dtype=np.float32)

    # Shape: (1, SEQ_LENGTH, N_FEATURES)
    if seq.shape != (SEQ_LENGTH, N_FEATURES):
        return {"error": f"Expected shape ({SEQ_LENGTH}, {N_FEATURES}), got {seq.shape}"}

    # Normalize the sequence using the same scaler used for training
    seq = scaler.transform(seq)
    # Reshape the sequence to match the input shape of the model
    seq = seq.reshape(1, SEQ_LENGTH, N_FEATURES)

    # Predict RUL
    prediction = model.predict(seq)
    rul = prediction[0][0]
    # Inverse transform the prediction to get the actual RUL value
    rul_actual = np.clip(np.expm1(rul), 0, 125)

    return {
        "unit_id": data.unit_id,
        "timestamp": data.timestamp,
        "predicted_rul": float(rul_actual)
    }

if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("Server stopped.")
    except Exception as e:
        print(f"Error starting server: {e}")
        exit(1)
