import numpy as np

from .data_processing import DataProcessing
from .model_repository import ModelRepository
from .forecast_reporter import ForecastReporter


class PredictionManager:
    def __init__(self):
        self.repository = ModelRepository()
        self.dataProcessor = DataProcessing()
        self.forecastReporter = ForecastReporter()

    def initiateTrainingCycle(self):
        """
        Zarządza procesem treningu:
        1. Pobiera dane.
        2. Pobiera listę modeli do treningu (z Repozytorium).
        3. Trenuje i waliduje każdy model.
        4. Wybiera najlepszy.
        """

        targets = ['consumption', 'production']
        for target in targets:
            # 1. Dane dla konkretnego celu
            X_train, X_test, y_train, y_test = self.dataProcessor.getTrainingData(target_variable=target)

            if X_train is None:
                continue

            # 2. Kandydaci dla konkretnego celu
            candidates = self.repository.create_fresh_candidates(target_variable=target)

            # 3. Wyścig
            for model in candidates:
                model.train(X_train, y_train)
                model.validate(X_test, y_test)
                self.repository.save(model)

            # 4. Wybór zwycięzcy w tej kategorii
            self.deployBestModel(target)

    def deployBestModel(self, target_variable):
        best = self.repository.selectBestModel(target_variable)
        if best:
            self.repository.deployModel(best)

    def generateAndPublishForecast(self):
        # Unpack tuple from dataProcessor
        X_input, future_dates = self.dataProcessor.getPredictionInput()

        # 1. Prognoza Zużycia
        model_cons = self.repository.getActiveModel('consumption')
        # 2. Prognoza Produkcji
        model_prod = self.repository.getActiveModel('production')

        if not model_cons or not model_prod:
            print("Brak aktywnych modeli. Uruchamiam auto-trening...")
            self.initiateTrainingCycle()
            model_cons = self.repository.getActiveModel('consumption')
            model_prod = self.repository.getActiveModel('production')

        if not model_cons:
            print("Nadal brak modelu consumption mimo treningu!")
            return self.forecastReporter
        
        pred_cons = model_cons.predict(X_input)

        if not model_prod:
            print("Nadal brak modelu production mimo treningu!")
            return self.forecastReporter
        
        pred_prod = model_prod.predict(X_input)

        # 3. Łączenie wyników (kolumna obok kolumny)
        combined_result = np.column_stack((pred_cons, pred_prod))

        # Zapis
        self.forecastReporter.generateReport(
            predicted_values=combined_result, 
            model_id=f"{model_cons.modelID}|{model_prod.modelID}",
            timestamps=future_dates
        )
        self.forecastReporter.saveToDatabase()

        return self.forecastReporter