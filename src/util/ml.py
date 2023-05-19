import joblib
import numpy as np
from keras.models import load_model


def predict_next_point(lstm_file_path: str, scaler_file_path: str, past_points: list):
    scaler = joblib.load(scaler_file_path)

    # Normalize
    past_points_norm = scaler.transform(past_points)
    # Reshape for LSTM
    past_points_norm = np.expand_dims(past_points_norm, 0)

    lstm_model = load_model(lstm_file_path)
    next_point_norm = lstm_model.predict(past_points_norm)

    next_point = scaler.inverse_transform(next_point_norm)

    return next_point
