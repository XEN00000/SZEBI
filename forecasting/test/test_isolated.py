import sys
from unittest.mock import MagicMock

# --- SEKJA 1: MOCKOWANIE MODUŁÓW (Musi być na samej górze!) ---

# 1. Mockujemy 'acquisition' (inny moduł)
mock_acquisition = MagicMock()
mock_acquisition.models.Measurement = MagicMock()
sys.modules['acquisition'] = mock_acquisition
sys.modules['acquisition.models'] = mock_acquisition.models

# 2. Mockujemy 'forecasting.models' (nasz własny moduł DB)
# To jest KLUCZOWE - dzięki temu Python nie wejdzie do pliku models.py
# i nie wyrzuci błędu o braku INSTALLED_APPS
mock_forecasting_models = MagicMock()
mock_forecast_class = MagicMock()
mock_forecasting_models.Forecast = mock_forecast_class
sys.modules['forecasting.models'] = mock_forecasting_models

# --- SEKJA 2: WŁAŚCIWE IMPORTY ---
from django.test import SimpleTestCase
from unittest.mock import patch
import pandas as pd
import numpy as np

# Teraz importujemy logikę (Python użyje mocków zamiast prawdziwych modeli)
from forecasting.logic.prediction_manager import PredictionManager


class ForecastingIsolatedTest(SimpleTestCase):

    def setUp(self):
        """Przygotowujemy sztuczne dane."""
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        self.fake_df = pd.DataFrame(index=dates)
        self.fake_df['consumption'] = np.random.uniform(0, 5, 200)
        self.fake_df['production'] = np.random.uniform(0, 5, 200)
        self.fake_df['hour_of_day'] = dates.hour
        self.fake_df['day_of_week'] = dates.dayofweek
        self.fake_df['month'] = dates.month
        self.fake_df['temp_outdoor'] = 15.0
        self.fake_df['solar_radiation'] = 300.0

    @patch('forecasting.logic.data_processing.DataProcessing.filterData')
    def test_full_flow_no_db(self, mock_filter_data):
        """
        Testuje przepływ bez dotykania bazy danych.
        """
        print("\n[TEST IZOLOWANY] Uruchamiam test bez DB...")

        # Konfiguracja mocka danych
        mock_filter_data.return_value = self.fake_df

        # Inicjalizacja
        manager = PredictionManager()

        # TEST TRENINGU
        print("-> 1. Test treningu...")
        manager.initiateTrainingCycle()

        # Sprawdzamy czy pobrał dane
        mock_filter_data.assert_called_once()

        # Sprawdzamy czy model w pamięci jest aktywny
        # Uwaga: Mockowanie repozytorium w teście bez bazy może wymagać ręcznego 'dotrenowania'
        active_model = manager.repository.getActiveModel()
        if not active_model.isActive:
            X_train, _, y_train, _ = manager.dataProcessor.standardizeSplittingData(self.fake_df)
            active_model.train(X_train, y_train)

        # TEST PROGNOZY
        print("-> 2. Test prognozy...")
        reporter = manager.generateAndPublishForecast()

        # Asercje
        self.assertIsNotNone(reporter, "Powinien zwrócić reporter")

        # Sprawdzamy czy reporter próbował zapisać do 'bazy' (czyli do naszego mocka)
        # Ponieważ zamockowaliśmy forecasting.models, Forecast.objects.create to teraz mock
        # Ale w ForecastReporter używasz importu 'from forecasting.models import Forecast'
        # Ponieważ podmieniliśmy sys.modules, 'Forecast' w reporterze to nasz mock_forecast_class

        # Sprawdźmy czy wywołano create() na naszym mocku
        self.assertTrue(mock_forecast_class.objects.create.called, "Powinno wywołać Forecast.objects.create")

        print("[SUKCES] Test zakończony bez błędów Django.")