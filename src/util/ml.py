import joblib
from keras.saving.save import load_model


def predict_next_point(lstm_file_path: str, scaler_file_path: str, past_points: list):
    scaler = joblib.load(scaler_file_path)
    scaler.fit_transform(past_points)
    lstm_model = load_model(lstm_file_path)
    next_point = lstm_model.predict(past_points)
    scaler.inverse_transform(next_point)

    return next_point
