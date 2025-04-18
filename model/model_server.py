from fastapi import FastAPI, Request
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras.initializers import Orthogonal
import uvicorn

app = FastAPI()

# Load model
model = tf.keras.models.load_model(
    "./model/lstm_fd001.keras", custom_objects={'Orthogonal': Orthogonal})

# Define input shape expected by model
SEQ_LENGTH = 50
N_FEATURES = 13  # number of sensors you're using

# Define request schema


class SensorData(BaseModel):
    unit_id: int
    sequence: list  # list of sensor readings, each is a list of floats


@app.post("/predict")
async def predict(data: SensorData):
    seq = np.array(data.sequence, dtype=np.float32)

    # Shape: (1, SEQ_LENGTH, N_FEATURES)
    if seq.shape != (SEQ_LENGTH, N_FEATURES):
        return {"error": f"Expected shape ({SEQ_LENGTH}, {N_FEATURES}), got {seq.shape}"}

    seq = seq.reshape(1, SEQ_LENGTH, N_FEATURES)

    # Predict RUL
    prediction = model.predict(seq)
    rul = prediction[0][0]

    return {
        "unit_id": data.unit_id,
        "predicted_rul": float(rul)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
