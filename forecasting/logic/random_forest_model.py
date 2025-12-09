from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from .prediction_model import PredictionModel


class RandomForestModel(PredictionModel):
    def __init__(self, target_variable="unknown", numTrees=100, maxDepth=None):
        super().__init__(target_variable)
        self.numTrees = numTrees
        self.maxDepth = maxDepth

        # MultiOutputRegressor pozwala przewidywać [zużycie, produkcja] jednocześnie
        self.internalModel = RandomForestRegressor(n_estimators=self.numTrees, max_depth=self.maxDepth, random_state=42)

    def train(self, X_train, y_train):
        self.internalModel.fit(X_train, y_train)

    def predict(self, X_input):
        return self.internalModel.predict(X_input)