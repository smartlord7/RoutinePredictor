import numpy as np
import pandas as pd
from keras.callbacks import EarlyStopping
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
        lstm_model = build_lstm_model(data_shape, sequence_length, learning_rate, int(num_layers), int(num_nodes))
        early_stop = EarlyStopping(monitor='val_loss', patience=3)
        history = lstm_model.fit(train_data, epochs=30, verbose=1, validation_data=val_data, callbacks=[early_stop])
        val_loss = np.min(history.history['val_loss'])

        return -val_loss

    return train_model_


def eval_model(model, test_data, y_test):
    train_loss = model.history['loss'][-1]
    val_loss = model.history['val_loss'][-1]

    y_pred = model.predict(test_data)
    y_pred = np.concatenate(y_pred)  # flatten the predictions
    y_test = np.concatenate(y_test)  # flatten the true labels
    mse = np.mean(np.square(y_pred - y_test))
    mae = np.mean(np.abs(y_pred - y_test))
    r2 = 1 - np.sum(np.square(y_pred - y_test)) / np.sum(np.square(y_test - np.mean(y_test)))

    print('Train loss: ', train_loss)
    print('Validation loss: ', val_loss)
    print('R-squared: ', r2)
    print('MSE: ', mse)
    print('MAE: ', mae)


def main():
    data = pd.read_csv(PATH_USER_DATA, header=None)
    data = data.to_numpy()[:, 1:]  # Discard weekday, just for now
    data_shape = data.shape
    print(data.shape)

    X = data[0:-1, :]
    scaler = MinMaxScaler()
    X = scaler.fit_transform(X)
    y = data[1:, :]

    X_dev, X_test, y_dev, y_test = train_test_split(X, y, shuffle=False, stratify=None, test_size=0.2)
    X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, shuffle=False, stratify=None, test_size=0.2)

    train_data = TimeseriesGenerator(X_train, y_train, length=SEQUENCE_LENGTH, batch_size=4) # reduce batch size
    val_data = TimeseriesGenerator(X_val, y_val, length=SEQUENCE_LENGTH, batch_size=4)
    test_data = TimeseriesGenerator(X_test, y_test, length=SEQUENCE_LENGTH, batch_size=4)

    pbounds = {'learning_rate': (1e-4, 3e-1),
               'num_layers': (2, 8),
               'num_nodes': (32, 128)}

    opt_callback = train_model(data_shape, SEQUENCE_LENGTH, train_data, val_data)
    lstm_bo = BayesianOptimization(f=opt_callback,  pbounds=pbounds, verbose=2, random_state=42)
    lstm_bo.maximize(init_points=5, n_iter=20, acq='ei')

    best_params = lstm_bo.max['params']
    best_learning_rate = best_params['learning_rate']
    best_num_layers = int(best_params['num_layers'])
    best_num_nodes = int(best_params['num_nodes'])

    best_lstm_model = build_lstm_model(data_shape, SEQUENCE_LENGTH, best_learning_rate, best_num_layers, best_num_nodes)
    best_lstm_model.summary()
    #eval_model(best_lstm_model, test_data, y_test)


if __name__ == '__main__':
    main()