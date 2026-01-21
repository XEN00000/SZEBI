import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from django.utils import timezone
from datetime import timedelta

# Importy z Twojego modułu akwizycji
from acquisition.logic.database_manager import DatabaseManager
from acquisition.services import AcquisitionDataService


class DataProcessing:
    def __init__(self):
        """
        Inicjalizacja z wykorzystaniem serwisu akwizycji.
        """
        self.scaler = StandardScaler()
        self.db_manager = DatabaseManager()
        self.acq_service = AcquisitionDataService(self.db_manager)

    def _get_metric_as_df(self, metric_name, start_date, end_date, column_name):
        """
        Pomocnicza metoda pobierająca realne pomiary.
        Kluczowe: Ustawienie DatetimeIndex, aby resample() działało.
        """
        raw_data = self.acq_service.get_filtered_analysis_data(
            metric=metric_name,
            start_time=start_date,
            end_time=end_date
        )

        if not raw_data:
            return pd.DataFrame(columns=[column_name], index=pd.to_datetime([], utc=True))

        data_list = [{'ts': m.timestamp, column_name: m.value} for m in raw_data]
        df = pd.DataFrame(data_list)

        df['ts'] = pd.to_datetime(df['ts'], utc=True)
        df.set_index('ts', inplace=True)
        return df

    def filterData(self):
        """
        Pobiera dane historyczne z bazy
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=90)

        df_cons = self._get_metric_as_df('consumed_kwh', start_date, end_date, 'consumption')
        df_prod = self._get_metric_as_df('peak_power', start_date, end_date, 'production')
        df_temp = self._get_metric_as_df('temperature', start_date, end_date, 'temp_outdoor')
        df_cloud = self._get_metric_as_df('cloudiness', start_date, end_date, 'cloud_cover')
        df_wind = self._get_metric_as_df('wind', start_date, end_date, 'wind_speed')
        df_sun = self._get_metric_as_df('sunlight', start_date, end_date, 'sunlight')

        dataset = df_cons.resample('h').sum()

        for df_metric in [df_prod.resample('h').sum(), df_temp.resample('h').mean(),
                          df_cloud.resample('h').mean(), df_wind.resample('h').mean(), df_sun.resample('h').mean()]:
            dataset = dataset.join(df_metric, how='outer')

        dataset = dataset.ffill().fillna(0)

        dataset['hour_of_day'] = dataset.index.hour
        dataset['day_of_week'] = dataset.index.dayofweek
        dataset['month'] = dataset.index.month

        print("DEBUG: filterData result head:\n", dataset.head())
        print("DEBUG: filterData result description:\n", dataset.describe())

        return dataset.dropna()

    def standardizeSplittingData(self, dataset, target_column):
        """
        Przygotowuje dane do modeli ML: podział i skalowanie.
        """
        if target_column not in dataset.columns:
            return None, None, None, None

        y = dataset[[target_column]]
        # Cechy wejściowe (Pogoda + Czas)
        X = dataset[['hour_of_day', 'day_of_week', 'month', 'temp_outdoor', 'cloud_cover', 'wind_speed', 'sunlight']]

        # Podział chronologiczny (ważne dla szeregów czasowych)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0, shuffle=False)

        # Dopasowanie skalera do danych treningowych
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train.values, y_test.values

    def getTrainingData(self, target_variable='consumption'):
        """Zwraca gotowe pakiety danych do treningu."""
        dataset = self.filterData()
        if dataset.empty:
            return None, None, None, None
        return self.standardizeSplittingData(dataset, target_variable)

    def getPredictionInput(self, external_scaler=None):
        """
        Tworzy unikalną prognozę na 168h bazując na danych historycznych.
        """
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        future_dates = [now + timedelta(hours=i) for i in range(1, 169)]

        hist_data = self.filterData()

        # Budowanie profilu: średnia wartość dla każdego dnia tygodnia i każdej godziny
        weather_profile = hist_data.groupby(['day_of_week', 'hour_of_day'])[
            ['temp_outdoor', 'cloud_cover', 'wind_speed', 'sunlight']].mean().reset_index()

        df_future = pd.DataFrame(index=future_dates)
        df_future['day_of_week'] = df_future.index.dayofweek
        df_future['hour_of_day'] = df_future.index.hour
        df_future['month'] = df_future.index.month

        df_future = df_future.merge(weather_profile, on=['day_of_week', 'hour_of_day'], how='left')
        df_future.index = future_dates

        df_future['temp_outdoor'] += np.random.normal(0, 0.5, size=len(df_future))
        df_future['cloud_cover'] = (df_future['cloud_cover'] + np.random.normal(0, 5, size=len(df_future))).clip(0, 100)
        df_future['wind_speed'] = (df_future['wind_speed'] + np.random.normal(0, 0.2, size=len(df_future))).clip(0, 25)
        df_future['sunlight'] = (df_future['sunlight'] + np.random.normal(0, 0.05, size=len(df_future))).clip(0, None)


        feature_cols = ['hour_of_day', 'day_of_week', 'month', 'temp_outdoor', 'cloud_cover', 'wind_speed', 'sunlight']
        df_future = df_future[feature_cols]

        scaler_to_use = external_scaler if external_scaler else self.scaler
        if external_scaler is None:
            # Fit scaler on historical data to ensure it's ready for transformation
            scaler_to_use.fit(hist_data[feature_cols])

        return scaler_to_use.transform(df_future), future_dates