import uuid
from abc import ABC, abstractmethod
from sklearn.metrics import mean_absolute_percentage_error

class PredictionModel(ABC):
    def __init__(self, target_variable="unknown"):
        self.modelID = uuid.uuid4()
        self.MAPE_Result = 0.0
        self.isActive = False
        self.target_variable = target_variable

    @abstractmethod
    def train(self, X_train, y_train):
        pass
    @abstractmethod
    def predict(self, X_input):
        pass

    def validate(self, X_test, y_test):
        y_pred = self.predict(X_test)

        error = mean_absolute_percentage_error(y_test, y_pred)

        self.MAPE_Result = float(error)
