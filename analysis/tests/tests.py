from django.test import TestCase
from datetime import datetime
from .services import  DataManager, Statistics, Measurement

class StatisticsTest(TestCase):
    def test_calculate_statistics_temperature(self):
        dm= DataManager()
        statistics = Statistics(dm)
        df = statistics.calculateStatistics(
            "101",
            datetime(2025, 12, 1, 8, 0),
            datetime(2025, 12, 1, 10, 0),
            Measurement.TEMPERATURE,
        )
        row = df.iloc[0]
        self.assertEqual(row["room_id"], "101")
        self.assertEqual(row["metric"], Measurement.TEMPERATURE)
        self.assertEqual(row["mean"], (22.5+23.0+23.5)/3)
        self.assertEqual(row["min"], 22.5)
        self.assertEqual(row["max"], 23.5)

    def test_calculate_statistics_humidity(self):
        dm = DataManager()
        statistics = Statistics(dm)
        df = statistics.calculateStatistics(
            "102",
            datetime(2025, 12, 1, 8, 0),
            datetime(2025, 12, 1, 9, 0),
            Measurement.HUMIDITY,
            )
        row = df.iloc[0]
        self.assertEqual(row["room_id"], "102")
        self.assertEqual(row["metric"], Measurement.HUMIDITY)
        self.assertEqual(row["mean"], (45+44)/2)
        self.assertEqual(row["min"], 44)
        self.assertEqual(row["max"], 45)


class AnalysisViewTest(TestCase):
    def test_statistics_endpoint(self):
        response = self.client.get("/analysis/test/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

        row = data[0]
        self.assertEqual(row["room_id"], "101")
        self.assertEqual(row["metric"], Measurement.TEMPERATURE)
        self.assertEqual(row["mean"], 23.0)
        self.assertEqual(row["min"], 22.5)
        self.assertEqual(row["max"], 23.5)

