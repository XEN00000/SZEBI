import uuid
import pickle
import os
from typing import Dict, List, Optional
from .prediction_model import PredictionModel


# UWAGA: USUNĘLIŚMY IMPORTY RandomForestModel, XGBoostModel, LSTMModel
# Repozytorium nie zna tych klas bezpośrednio!

class ModelRepository:
    def __init__(self):
        self.modelCache: Dict[uuid.UUID, PredictionModel] = {}
        self.active_models: Dict[str, uuid.UUID] = {}
        self.storage_path = "trained_models/"
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

    def create_fresh_candidates(self, target_variable: str) -> List[PredictionModel]:
        candidates = []

        # Pobieramy wszystkie klasy, które dziedziczą po PredictionModel
        subclasses = PredictionModel.__subclasses__()

        for model_class in subclasses:
            instance = model_class(target_variable=target_variable)
            candidates.append(instance)

        return candidates

    def save(self, model: PredictionModel):
        self.modelCache[model.modelID] = model
        file_path = os.path.join(self.storage_path, f"{model.modelID}.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(model, f)

    def selectBestModel(self, target_variable: str) -> PredictionModel:
        relevant = [m for m in self.modelCache.values() if m.target_variable == target_variable]
        if not relevant:
            return None
        return min(relevant, key=lambda m: m.MAPE_Result)

    def deployModel(self, model: PredictionModel):
        self.active_models[model.target_variable] = model.modelID
        for m in self.modelCache.values():
            if m.target_variable == model.target_variable:
                m.isActive = (m.modelID == model.modelID)

    def getActiveModel(self, target_variable: str) -> Optional[PredictionModel]:
        mid = self.active_models.get(target_variable)
        if mid and mid in self.modelCache:
            return self.modelCache[mid]
        return None