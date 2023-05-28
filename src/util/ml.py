"""
------------WayAhead: Predicting a person's routine------------
 University of Coimbra
 Masters in Intelligent Systems
 Ubiquitious Systems
 1st year, 2nd semester
 Authors:
 Alexandre Gameiro Leopoldo, 2019219929, uc2019219929@student.uc.pt
 Sancho Amaral Simões, 2019217590, uc2019217590@student.uc.pt
 Tiago Filipe Santa Ventura, 2019243695, uc2019243695@student.uc.pt
 Credits to:
 Carlos Bento
 Coimbra, 29th May 2023
 ---------------------------------------------------------------------------
"""

import joblib
import numpy as np
from keras.models import load_model


def predict_next_point(lstm_file_path: str, scaler_file_path: str, past_points: list):
    """
       Predicts the next point based on the given LSTM model and scaler.

       Parameters:
       -----------
       lstm_file_path: str
           The file path of the saved LSTM model.
       scaler_file_path: str
           The file path of the saved scaler.
       past_points: list
           A list of past points used as input for prediction.

       Returns:
       --------
       np.ndarray
           An array representing the predicted next point.
    """
    scaler = joblib.load(scaler_file_path)

    # Normalize
    past_points_norm = scaler.transform(past_points)
    # Reshape for LSTM
    past_points_norm = np.expand_dims(past_points_norm, 0)

    lstm_model = load_model(lstm_file_path)
    next_point_norm = lstm_model.predict(past_points_norm)

    next_point = scaler.inverse_transform(next_point_norm)

    return next_point
