import pickle
import warnings

import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping
from keras.models import load_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional
from keras.optimizers import Adam
from bayes_opt import BayesianOptimization

USER_ID = 353
PATH_DATA = '../data/user_sequences/'
EXTENSION_TEXT = '.txt'
PATH_USER_DATA = PATH_DATA + f'user_{USER_ID}_sequence' + EXTENSION_TEXT
SEQUENCE_LENGTH = 2
COUNTER = 1
FRACTION_TEST = 0.2
FRACTION_VALIDATION = 0.2


def build_lstm_model(data_shape, sequence_length, learning_rate, num_layers, num_nodes):
    lstm_model = Sequential()
    for i in range(num_layers):
        if i == 0:
            lstm_model.add(LSTM(num_nodes, input_shape=(sequence_length, data_shape[1]), return_sequences=True))
        elif i == num_layers - 1:
            lstm_model.add(LSTM(num_nodes))
        else:
            lstm_model.add(LSTM(num_nodes, return_sequences=True))

    lstm_model.add(Dense(data_shape[1]))
    opt = Adam(learning_rate=learning_rate)
    lstm_model.compile(optimizer=opt, loss='mse')

    return lstm_model


def train_model(data_shape, sequence_length, train_data, val_data):
    def train_model_(learning_rate, num_layers, num_nodes):
        global COUNTER
        lstm_model = build_lstm_model(data_shape, sequence_length, learning_rate, int(num_layers), int(num_nodes))
        early_stop = EarlyStopping(monitor='val_loss', patience=3)
        history = lstm_model.fit(train_data, epochs=5, verbose=1, validation_data=val_data, callbacks=[early_stop])
        val_loss = np.min(history.history['val_loss'])

        filename = 'lstm_model_' + str(COUNTER) + '.h5'
        lstm_model.save(filename)
        COUNTER += 1

        return -val_loss

    return train_model_


def eval_model(model, test_data):
    #train_loss = model.history['loss'][-1]
    #val_loss = model.history['val_loss'][-1]
    test_loss = model.evaluate(test_data)
    #print('Train loss: ', train_loss)
    #print('Validation loss: ', val_loss)
    print('Test loss: ', test_loss)



def main():
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    data = pd.read_csv(PATH_USER_DATA, header=None)
    data = data.to_numpy()[:, 1:]  # Discard weekday, just for now
    data_shape = data.shape
    print(data.shape)

    X = data
    y = data
    scaler = MinMaxScaler()

    scaler.fit(X)
    X = scaler.transform(X)
    y = scaler.transform(y)

    X_dev, X_test, y_dev, y_test = train_test_split(X, y, shuffle=False, stratify=None, test_size=FRACTION_TEST)
    X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, shuffle=False, stratify=None, test_size=FRACTION_VALIDATION)

    train_data = TimeseriesGenerator(X_train, y_train, length=SEQUENCE_LENGTH, batch_size=8) # reduce batch size
    val_data = TimeseriesGenerator(X_val, y_val, length=SEQUENCE_LENGTH, batch_size=8)
    test_data = TimeseriesGenerator(X_test, y_test, length=SEQUENCE_LENGTH, batch_size=8)

    pbounds = {'learning_rate': (1e-4, 3e-1),
               'num_layers': (2, 8),
               'num_nodes': (32, 128)}

    opt_callback = train_model(data_shape, SEQUENCE_LENGTH, train_data, val_data)
    lstm_bo = BayesianOptimization(f=opt_callback,  pbounds=pbounds, verbose=2, random_state=42)
    lstm_bo.maximize(init_points=0, n_iter=1, acq='ei')
    best_model_index = max(range(len(lstm_bo.res)), key=lambda i: lstm_bo.res[i]['target']) + 1
    best_model_filename = 'lstm_model_' + str(best_model_index) + '.h5'
    best_lstm_model = load_model(best_model_filename)

    print('Best LSTM params:')
    best_params = lstm_bo.max['params']
    print(best_params)

    best_lstm_model.summary()
    eval_model(best_lstm_model, test_data)


if __name__ == '__main__':
    main()