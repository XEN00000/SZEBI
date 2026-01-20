import datetime
import requests
import os
from typing import List, Optional, Dict, Any

from .logic.database_manager import DatabaseManager
from .models import Measurement, DataLog

class AcquisitionDataService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        # self.alarms_url = "http://localhost:8000/api/data-inspection/check_rules/"
        self.alarms_url = os.getenv('INSPECTION_API_URL', "http://localhost:8000/api/data-inspection/check_rules/")

    def post_to_alarms(self, measurement: Measurement):

        metric_name = measurement.sensor.type.name

        # payload = {
        #     "metric_name": metric_name,
        #     "value": measurement.value,
        #     "timestamp": measurement.timestamp.isoformat()
        # }

        payload = {
            "metric_name": metric_name,
            "value": measurement.value,
            "timestamp": measurement.timestamp.isoformat(),
            "details": {
                "sensor_id": measurement.sensor.id,
                "room": measurement.sensor.location.room,
                "status": measurement.status
            }
        }

        try:
            response = requests.post(self.alarms_url, json=payload, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Błąd wysyłki do alarmów: {e}")

    def get_measurements_by_time_range(
        self,
        sensor_id: int,
        start_time: datetime.datetime,
        end_time: datetime.datetime
    ) -> List[Measurement]:
        """
        Pobiera wszystkie pomiary dla danego czujnika
        w określonym zakresie czasu.
        """
        return self.db_manager.get_measurements(sensor_id, start_time, end_time)

    def get_latest_measurement(self, sensor_id: int) -> Optional[Measurement]:
        """
        Pobiera najnowszy, pojedynczy pomiar dla czujnika, niezależnie od tego, kiedy wpłynął.
        """
        return self.db_manager.get_last_measurement(sensor_id)

    def get_filtered_analysis_data(
            self,
            room: Optional[str] = None,
            metric: Optional[str] = None,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None,
    ) -> List[Measurement]:
        """
        Udostępnia dane z zaawansowanym filtrowaniem. Umożliwia filtrowanie po lokalizacji (room)
        i typie sensora.
        """

        return self.db_manager.get_filtered_measurements(
            room=room,
            metric=metric,
            start_time=start_time,
            end_time=end_time
        )

    # --- Pobieranie logów ---
    def get_logs_by_level(self, level: str) -> List[DataLog]:
        return self.db_manager.get_logs(level)

    # --- Statystyki czujników ---
    def get_sensor_statistics(self) -> List[Dict[str, Any]]:
        return self.db_manager.get_sensor_statistics()

    # --- Lista wszystkich pokojów ---
    def get_all_rooms(self) -> List[str]:
        return self.db_manager.get_all_rooms()

    # --- Lista wszystkich typów pomiarów ---
    def get_all_metrics(self) -> List[str]:
        return self.db_manager.get_all_metrics()