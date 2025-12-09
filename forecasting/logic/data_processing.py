import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from django.utils import timezone
from datetime import timedelta

from acquisition.logic.database_manager import DatabaseManager
from acquisition.services import AcquisitionDataService


class DataProcessing:
    def __init__(self):
        self.scaler = StandardScaler()

        # Inicjalizacja serwisu (API Akwizycji)
        self.db_manager = DatabaseManager()
        self.acq_service = AcquisitionDataService(self.db_manager)

    def _fetch_and_aggregate_via_api(self, sensor_type_name, start_date, end_date, value_column_name):
        """
        Metoda pomocnicza:
        1. Pyta API o listę czujników danego typu.
        2. Pobiera pomiary.
        3. Agreguje dane do godzinnych sum w Pandas.
        """

        # 1. Pobierz listę wszystkich czujników z API
        all_sensors_stats = self.acq_service.get_sensor_statistics()

        # 2. Wybierz ID czujników pasujących do typu
        target_sensor_ids = [
            s['id'] for s in all_sensors_stats
            if s.get('type_name') == sensor_type_name
        ]

        if not target_sensor_ids:
            return pd.DataFrame()

        # 3. Pobierz pomiary dla każdego znalezionego czujnika
        all_measurements = []
        for sensor_id in target_sensor_ids:
            measurements = self.acq_service.get_measurements_by_time_range(
                sensor_id, start_date, end_date
            )
            all_measurements.extend(measurements)

        if not all_measurements:
            return pd.DataFrame()

        # 4. Konwersja listy na Pandas DataFrame
        data_list = [{'timestamp': m.timestamp, 'value': m.value} for m in all_measurements]
        df = pd.DataFrame(data_list)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)

        # 5. Agregacja godzinowa (suma)
        df_resampled = df.resample('h').sum()

        df_resampled.rename(columns={'value': value_column_name}, inplace=True)
        df_resampled.index.name = 'hour'

        return df_resampled

    def filterData(self):
        """
        Główna metoda pobierająca dane historyczne.
        Zakres: Ostatnie 90 dni.
        Dane: Tylko Zużycie i Produkcja (bez magazynu).
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)  # WYMÓG: 3 miesiące

        # 1. Pobierz Zużycie (Licznik Energii)
        df_cons = self._fetch_and_aggregate_via_api(
            sensor_type_name='Licznik Energii',
            start_date=start_date,
            end_date=end_date,
            value_column_name='consumption'
        )

        # 2. Pobierz Produkcję (Inverter)
        df_prod = self._fetch_and_aggregate_via_api(
            sensor_type_name='Inverter',
            start_date=start_date,
            end_date=end_date,
            value_column_name='production'
        )

        # Sprawdzenie czy mamy jakiekolwiek dane
        if df_cons.empty and df_prod.empty:
            print("Brak danych (Zużycie/Produkcja) w module Akwizycji!")
            return None

        dataset = pd.DataFrame()

        if not df_cons.empty and not df_prod.empty:
            dataset = df_cons.join(df_prod, how='outer')
        elif not df_cons.empty:
            dataset = df_cons
            dataset['production'] = 0.0
        elif not df_prod.empty:
            dataset = df_prod
            dataset['consumption'] = 0.0

        # Wypełniamy braki zerami
        dataset = dataset.fillna(0)

        # Feature Engineering (Cechy Czasowe)
        dataset['hour_of_day'] = dataset.index.hour
        dataset['day_of_week'] = dataset.index.dayofweek
        dataset['month'] = dataset.index.month

        # MOCK Pogody
        dataset['temp_outdoor'] = 15.0
        dataset['solar_radiation'] = dataset['hour_of_day'].apply(lambda h: 500 if 8 <= h <= 18 else 0)

        return dataset.dropna()

    def standardizeSplittingData(self, dataset):
        """
        Przygotowuje dane do modelu ML.
        """
        # Y (Target) - Przewidujemy 2 rzeczy: Zużycie i Produkcję
        y = dataset[['consumption', 'production']]

        # X (Features) - Czas + Pogoda
        X = dataset[['hour_of_day', 'day_of_week', 'month', 'temp_outdoor', 'solar_radiation']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=False)

        # Skalowanie danych
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train.values, y_test.values

    def getTrainingData(self):
        dataset = self.filterData()
        if dataset is None:
            return None, None, None, None
        return self.standardizeSplittingData(dataset)

    def getPredictionInput(self):
        """
        Przygotowuje dane wejściowe (X) na przyszłość.
        WYMÓG: Prognoza na 7 dni (168 godzin).
        """
        import datetime

        # Startujemy od "następnej pełnej godziny"
        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        # Generujemy 168 godzin w przód (7 dni * 24h)
        future_dates = [now + datetime.timedelta(hours=i) for i in range(1, 169)]

        df_future = pd.DataFrame({'timestamp': future_dates})
        df_future.set_index('timestamp', inplace=True)

        # Te same cechy co przy treningu
        df_future['hour_of_day'] = df_future.index.hour
        df_future['day_of_week'] = df_future.index.dayofweek
        df_future['month'] = df_future.index.month

        # Mock Pogody
        df_future['temp_outdoor'] = 10.0
        df_future['solar_radiation'] = df_future['hour_of_day'].apply(lambda h: 300 if 9 <= h <= 17 else 0)

        # Skalujemy dane (fit_transform na potrzeby demo)
        return self.scaler.fit_transform(df_future)