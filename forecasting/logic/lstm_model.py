from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from .prediction_model import PredictionModel


class LSTMModel(PredictionModel):
    def __init__(self, target_variable="unknown", numLayers=2, sequenceLength=10):
        super().__init__(target_variable)

        self.numLayers = numLayers
        self.sequenceLength = sequenceLength
        self.internalModel = None

    def _build_model(self, input_shape, output_shape):
        model = Sequential()

        for i in range(self.numLayers):
            is_last_layer = (i == self.numLayers - 1)
            return_seq = not is_last_layer

            if i == 0:
                model.add(LSTM(128, return_sequences=return_seq, input_shape=input_shape))
            else:
                model.add(LSTM(128, return_sequences=return_seq))

            model.add(Dropout(0.2))

        model.add(Dense(1))
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.internalModel = model

    def train(self, X_train, y_train):
        X_reshaped = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))

        if self.internalModel is None:
            self._build_model((1, X_train.shape[1]), y_train.shape[1])

        self.internalModel.fit(X_reshaped, y_train, epochs=20, batch_size=32, verbose=0)

    def predict(self, X_input):
        X_reshaped = X_input.reshape((X_input.shape[0], 1, X_input.shape[1]))
        return self.internalModel.predict(X_reshaped)