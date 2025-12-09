import uuid
import pickle
import os
from typing import Dict, Optional
from .prediction_model import PredictionModel
from .random_forest_model import RandomForestModel

class ModelRepository:
    def __init__(self):
        self.modelCache: Dict[uuid.UUID, PredictionModel] = {}
        self.activeModelID: Optional[uuid.UUID] = None
        self.storage_path = "trained_models/"
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def save(self, model: PredictionModel):
        self.modelCache[model.modelID] = model

        file_path = os.path.join(self.storage_path, f"{model.modelID}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(model, f)

        print(f"Model {model.modelID} został zapisany w repozytorium.")

    def selectBestModel(self) -> PredictionModel:
        if not self.modelCache:
            print("Brak modeli w cache! Zwracam nowy, niewytrenowany model.")
            return RandomForestModel()

        best_model = min(self.modelCache.values(), key=lambda m: m.MAPE_Result)

        print(f"Najlepszy model to {best_model.modelID} z MAPE: {best_model.MAPE_Result}")
        return best_model

    def deployModel(self, modelId: uuid.UUID):
        if modelId in self.modelCache:
            self.activeModelID = modelId

            for mid, model in self.modelCache.items():
                if mid == modelId:
                    model.isActive = True
                else:
                    model.isActive = False

            print(f"Model {modelId} został wdrożony (DEPLOY).")
        else:
            print(f"Błąd: Nie znaleziono modelu o ID {modelId} w repozytorium.")

    def getActiveModel(self) -> PredictionModel:
        if self.activeModelID and self.activeModelID in self.modelCache:
            return self.modelCache[self.activeModelID]

        print("Brak aktywnego modelu. Tworzę nowy domyślny model.")
        new_default_model = RandomForestModel()
        self.save(new_default_model)
        self.deployModel(new_default_model.modelID)
        return new_default_model
