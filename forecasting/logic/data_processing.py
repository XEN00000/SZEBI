import pandas as pd
import numpy as np
import datetime
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

    def filterData(self):
        """
        Główna metoda pobierająca dane historyczne (X i Y).
        """
        # Wywołanie na cele integracji
        real_stats = self.acq_service.get_sensor_statistics()

        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)  # 3 miesiące wstecz

        # Generujemy wspólną oś czasu (godzinową) dla wszystkich danych
        dates = pd.date_range(start=start_date, end=end_date, freq='h')


        # Generujemy losowe dane zużycia (0.5 - 5.0 kWh)
        cons_values = np.random.uniform(0.5, 5.0, size=len(dates))
        df_cons = pd.DataFrame(data={'consumption': cons_values}, index=dates)

        # Agregacja godzinowa
        df_cons = df_cons.resample('h').sum()

        # Generujemy produkcję zależną od godziny (słońce 8-18)
        hours = dates.hour
        prod_values = np.where(
            (hours >= 8) & (hours <= 18),
            np.random.uniform(0, 8.0, size=len(dates)),
            0.0
        )
        df_prod = pd.DataFrame(data={'production': prod_values}, index=dates)
        df_prod = df_prod.resample('h').sum()


        dataset = df_cons.join(df_prod, how='outer').fillna(0)

        dataset['hour_of_day'] = dataset.index.hour
        dataset['day_of_week'] = dataset.index.dayofweek
        dataset['month'] = dataset.index.month

        # MOCK temperatury
        dataset['temp_outdoor'] = 15.0

        # MOCK Zachmurzenia (0-100%) - zamiast Solar Radiation
        dataset['cloud_cover'] = np.random.uniform(0, 100, size=len(dataset))

        # MOCK Wiatru (0-20 m/s)
        dataset['wind_speed'] = np.random.uniform(0, 20, size=len(dataset))

        return dataset.dropna()

    def standardizeSplittingData(self, dataset, target_column):
        """
        Przygotowuje dane do modelu ML.
        """
        # Y = Co przewidujemy (Zużycie i Produkcja)
        y = dataset[[target_column]]

        # X = Cechy (Czas + Pogoda: temperatura, chmury, wiatr)
        X = dataset[['hour_of_day', 'day_of_week', 'month', 'temp_outdoor', 'cloud_cover', 'wind_speed']]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=False)

        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train.values, y_test.values

    def getTrainingData(self, target_variable='consumption'):
        dataset = self.filterData()
        if dataset is None:
            return None, None, None, None
        return self.standardizeSplittingData(dataset, target_variable)

    def getPredictionInput(self):
        """
        Przygotowuje dane wejściowe (X) na przyszłość (7 dni).
        """

        now = timezone.now().replace(minute=0, second=0, microsecond=0)

        # 168 godzin = 7 dni
        future_dates = [now + datetime.timedelta(hours=i) for i in range(1, 169)]

        df_future = pd.DataFrame({'timestamp': future_dates})
        df_future.set_index('timestamp', inplace=True)

        df_future['hour_of_day'] = df_future.index.hour
        df_future['day_of_week'] = df_future.index.dayofweek
        df_future['month'] = df_future.index.month

        # MOCK Danych pogodowych na przyszłość
        df_future['temp_outdoor'] = 10.0

        # Losowe prognozy pogody na przyszły tydzień
        df_future['cloud_cover'] = np.random.uniform(0, 100, size=len(df_future))
        df_future['wind_speed'] = np.random.uniform(0, 20, size=len(df_future))

        return self.scaler.fit_transform(df_future)