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
import pickle
import warnings

import joblib
import numpy as np
import pandas as pd
from hyperopt import Trials, fmin, tpe, hp
from keras.callbacks import EarlyStopping
from keras.models import load_model
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.models import Sequential
from keras.layers import Dense, LSTM, Bidirectional
from keras.optimizers import Adam
from bayes_opt import BayesianOptimization, UtilityFunction

USER_ID = 353
PATH_DATA = '../data/user_sequences/'
EXTENSION_TEXT = '.txt'
PATH_USER_DATA = PATH_DATA + f'user_{USER_ID}_sequence' + EXTENSION_TEXT
SEQUENCE_LENGTH = 3
COUNTER = 1
FRACTION_TEST = 0.2
FRACTION_VALIDATION = 0.2


def build_lstm_model(data_shape, sequence_length, learning_rate, num_layers, num_nodes):
    """
       Builds an LSTM model for sequence prediction.

       Parameters:
       -----------
       data_shape: tuple
           A tuple representing the shape of the input data.
       sequence_length: int
           The length of the input sequence.
       learning_rate: float
           The learning rate for the optimizer.
       num_layers: int
           The number of LSTM layers in the model.
       num_nodes: int
           The number of nodes in each LSTM layer.

       Returns:
       --------
       keras.models.Sequential
           The constructed LSTM model.
    """
    lstm_model = Sequential()
    for i in range(num_layers):
        if i == 0:
            lstm_model.add(LSTM(num_nodes, input_shape=(sequence_length, data_shape[1]), return_sequences=True))
        elif i == num_layers - 1:
            lstm_model.add(LSTM(num_nodes))
        else:
            lstm_model.add(LSTM(num_nodes, return_sequences=True))

    lstm_model.add(Dense(2))
    opt = Adam(learning_rate=learning_rate)
    lstm_model.compile(optimizer=opt, loss='mse')

    return lstm_model


def train_model(data_shape, sequence_length, train_data, val_data):
    """
       Trains an LSTM model using the provided training and validation data.

       Parameters:
       -----------
       data_shape: tuple
           A tuple representing the shape of the input data.
       sequence_length: int
           The length of the input sequence.
       train_data: numpy.ndarray
           The training data used for model training.
       val_data: numpy.ndarray
           The validation data used for model evaluation.

       Returns:
       --------
       float
           The negative validation loss achieved by the trained model.
    """

    def train_model_(params):
        """
            Trains the LSTM model with the specified hyperparameters and returns the negative validation loss.

            Parameters:
            -----------
            params: dict
                A dictionary containing the hyperparameters.

            Returns:
            --------
            float
                The negative validation loss achieved by the trained model.
        """
        global COUNTER
        learning_rate = params['learning_rate']
        num_layers = int(params['num_layers'])
        num_nodes = int(params['num_nodes'])

        lstm_model = build_lstm_model(data_shape, sequence_length, learning_rate, num_layers, num_nodes)
        early_stop = EarlyStopping(monitor='val_loss', patience=3)
        history = lstm_model.fit(train_data, epochs=200, verbose=1, validation_data=val_data, callbacks=[early_stop])
        val_loss = np.min(history.history['val_loss'])

        filename = 'lstm_model_' + str(COUNTER) + '.h5'
        lstm_model.save(filename)
        COUNTER += 1

        return -val_loss

    return train_model_


def eval_model(model, test_data):
    """
        Evaluates the trained model on the test data and prints the test loss.

        Parameters:
        -----------
        model: keras.models.Sequential
            The trained LSTM model to evaluate.
        test_data: numpy.ndarray
            The test data used for evaluation.
    """
    # train_loss = model.history['loss'][-1]
    # val_loss = model.history['val_loss'][-1]
    test_loss = model.evaluate(test_data)
    # print('Train loss: ', train_loss)
    # print('Validation loss: ', val_loss)
    print('Test loss: ', test_loss)


def main():
    """
       Main function that executes the routine prediction workflow.

       It preprocesses the data, splits it into training, validation, and test sets.
       Then, it performs Hyperopt optimization to search for the best LSTM model hyperparameters.
       Finally, it evaluates the best model on the test data and prints the results.
    """
    warnings.filterwarnings('ignore', category=DeprecationWarning)

    data = pd.read_csv(PATH_USER_DATA, header=None)
    data = data.to_numpy()[:, 1:]  # Discard weekday, just for now
    data_shape = data.shape
    print(data.shape)

    X = data
    y = data.copy()
    scaler = MinMaxScaler()

    scaler.fit(X)
    X = scaler.transform(X)
    y = scaler.transform(y)

    scaler_filename = f'scaler_{USER_ID}.pkl'
    with open(scaler_filename, 'wb') as file:
        joblib.dump(scaler, file)

    X_dev, X_test, y_dev, y_test = train_test_split(X, y, shuffle=False, stratify=None, test_size=FRACTION_TEST)
    X_train, X_val, y_train, y_val = train_test_split(X_dev, y_dev, shuffle=False, stratify=None,
                                                      test_size=FRACTION_VALIDATION)

    train_data = TimeseriesGenerator(X_train, y_train, length=SEQUENCE_LENGTH, batch_size=4)
    val_data = TimeseriesGenerator(X_val, y_val, length=SEQUENCE_LENGTH, batch_size=4)
    test_data = TimeseriesGenerator(X_test, y_test, length=SEQUENCE_LENGTH, batch_size=4)

    space = {
        'learning_rate': hp.uniform('learning_rate', 1e-4, 3e-1),
        'num_layers': hp.quniform('num_layers', 2, 8, 1),
        'num_nodes': hp.quniform('num_nodes', 32, 128, 1)
    }

    opt_callback = train_model(data_shape, SEQUENCE_LENGTH, train_data, val_data)
    trials = Trials()
    best = fmin(fn=opt_callback, space=space, algo=tpe.suggest, max_evals=100, trials=trials)

    best_model_index = np.argmin(trials.losses()) + 1
    best_model_filename = 'lstm_model_' + str(best_model_index) + '.h5'
    best_lstm_model = load_model(best_model_filename)

    print('Best LSTM params (%s):' % best_lstm_model)
    print(best)

    best_lstm_model.summary()
    eval_model(best_lstm_model, test_data)


if __name__ == '__main__':
    main()
