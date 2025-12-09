from typing import List, Dict, Optional, Any
from .models import Forecast
from .logic.prediction_manager import PredictionManager


class ForecastingService:
    """
    Warstwa Usługowa: Publiczne API Modułu Prognozowania dla innych modułów SZEBI.
    """

    def __init__(self):
        self.manager = PredictionManager()

    def generate_new_forecast(self) -> Dict[str, List[float]]:
        """
        [API Write Method] Wymusza wygenerowanie nowej prognozy "na żądanie"
        i zwraca jej wyniki (rozdzielone na consumption i production).
        """
        # Manager zwraca reporter, który ma w sobie połączone wyniki (Nx2)
        reporter = self.manager.generateAndPublishForecast()

        if reporter and reporter.predictedValues is not None:
            values = reporter.getPredictedValues()
            return {
                "consumption": values[:, 0].tolist(),
                "production": values[:, 1].tolist()
            }
        return {}

    def get_latest_forecast(self) -> Optional[Dict[str, Any]]:
        """
        [API Read Method] Pobiera ostatnią zapisaną prognozę z bazy danych
        bez uruchamiania obliczeń.
        """
        last_forecast = Forecast.objects.order_by('-created_at').first()

        if last_forecast:
            return last_forecast.result
        return None

    def train_models(self) -> str:
        """
        [API Maintenance Method] Uruchamia proces treningu modeli.
        """
        try:
            self.manager.initiateTrainingCycle()

            return "SUCCESS"
        except Exception as e:
            return f"ERROR: {str(e)}"