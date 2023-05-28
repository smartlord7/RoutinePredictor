import joblib
import os.path
import pandas as pd
import numpy as np
from keras.models import load_model

def predict_next_point(model, scaler, past_points):
    # Normalize
    past_points_norm = scaler.transform(past_points)
    # Reshape for LSTM
    past_points_norm = np.expand_dims(past_points_norm, 0)

    next_point_norm = model.predict(past_points_norm, verbose=0)

    next_point = scaler.inverse_transform(next_point_norm)

    return next_point


USER_ID = 353
PATH_DATA = 'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_sequences\\' # Complete path because of QGis Interpreter
LSTM_DATA = f'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\models\\user_{USER_ID}\\'
EXTENSION_TEXT = '.txt'
PATH_USER_DATA = PATH_DATA + f'user_{USER_ID}_sequence' + EXTENSION_TEXT

SCALER_PATH = LSTM_DATA + 'MinMaxScaler'
MODEL_PATH = LSTM_DATA + 'lstm_model_1.h5'

test_model_path = f'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\models\\test\\model.h5'
test_scaler_path = f'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\models\\test\\scaler'
predict_file_path = f'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_predictions\\{USER_ID}_pred.txt'
true_file_path = f'C:\\Users\\alexl\\Desktop\\Mestrado\\Cadeiras 1 ano\\Semestre 2\\SU\\Project\\data\\user_predictions\\{USER_ID}_true.txt'

# Load LSTM model and Scaler
#model = load_model(MODEL_PATH)
#scaler = joblib.load(SCALER_PATH)
model = load_model(test_model_path)
scaler = joblib.load(test_scaler_path)

sequence_length = 3
tmp_index = 3

weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

prev = None
lst = []

# Read the whole sequence
with open(PATH_USER_DATA, 'r') as file:
    for index, line in enumerate(file.readlines()):
        vals = line.strip().split(',')
        day = int(vals[0])
        lat = float(vals[1])
        lon = float(vals[2])

        lst.append([lat, lon])

lst = np.array(lst)

predict_file = open(predict_file_path, 'w')
true_file = open(true_file_path, 'w')

# Write starting point of prediction, which is the same point
predict_file.write(f'{lst[sequence_length - 1, 0]},{lst[sequence_length - 1, 1]}\n')
true_file.write(f'{lst[sequence_length - 1, 0]},{lst[sequence_length - 1, 1]}\n')

for i in range(sequence_length, len(lst)):
    # Past points are always the TRUE points
    past_points = lst[i - sequence_length: i, :]

    pred = predict_next_point(model, scaler, past_points)[0]
    true = lst[i]
    predict_file.write(f'{pred[0]},{pred[1]}\n')
    true_file.write(f'{true[0]},{true[1]}\n')

predict_file.close()
true_file.close()
