import uuid
from django.utils import timezone
from forecasting.models import Forecast

class ForecastReporter:
    def __init__(self):
        self.forecastID = uuid.uuid4()
        self.predictedValues = None
        self.modelID = None
        self.creationTime = timezone.now()

    def generateReport(self, predicted_values=None, model_id=None):
        self.forecastID = uuid.uuid4()
        self.predictedValues = predicted_values
        self.modelID = model_id
        self.creationTime = timezone.now()

    def saveToDatabase(self):
        if self.predictedValues is None:
            return

        consumption = [float(row[0]) for row in self.predictedValues]
        production = [float(row[1]) for row in self.predictedValues]

        formatted_result = {
            "model_id": str(self.modelID),
            "generated_at": str(self.creationTime),
            "consumption": consumption,
            "production": production
        }

        Forecast.objects.create(
            horizon=len(consumption) * 60, # 24h * 60min
            result=formatted_result
        )

    def getPredictedValues(self):
        return self.predictedValues