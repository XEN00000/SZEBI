import datetime
from typing import List, Optional, Dict, Any
from acquisition.models import Measurement, DataLog, Sensor, SensorStatus

class DatabaseManager:
    def insert_measurements(self, measurement: Measurement) -> None:
        try:
            measurement.save()
            print(f"DB: ZAPISANO POMIAR: ID={measurement.pk} Value={measurement.value}")
        except Exception as e:
            print(f"DB ERROR przy zapisie pomiaru: {e}")

    def insert_data_log(self, log: DataLog) -> None:
        try:
            log.save()
            print(f"DB: ZAPISANO LOG: {log.level} - {log.message[:30]}...")
        except Exception as e:
            print(f"DB ERROR przy zapisie logu: {e}")

    def update_sensor(self, sensor_id: int, timestamp: datetime.datetime) -> None:
        try:
            Sensor.objects.filter(pk=sensor_id).update(last_communication=timestamp)
        except Exception as e:
            print(f"DB ERROR przy aktualizacji sensora: {e}")


    def insert_data_log(self, log: DataLog) -> None:
        """
        Rejestruje błędy walidacji, połączenia lub przetwarzania w tabeli data_logs.
        """
        print(f"DB: INSERT DATA_LOG: Level: {log.level}, Message: {log.message[:30]}...")

    def update_sensor(self, sensor_id: int, timestamp: datetime.datetime) -> None:
        """
        Aktualizuje last_communication w tabeli sensors.
        """
        print(f"DB: UPDATE SENSOR {sensor_id}: last_communication updated to {timestamp}")

    def get_sensor(self, sensor_id: int) -> Optional[Sensor]:
        """
        Pobiera obiekt Sensor na podstawie sensor_id..
        """
        print(f"DB: GET SENSOR {sensor_id}: Fikcyjny obiekt zwrócony.")

        return Sensor(
            pk=sensor_id,
            name=f"Sensor-{sensor_id}",
            status=SensorStatus.ACTIVE
        )

    def get_measurements(self, sensor_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Measurement]:
        return list(Measurement.objects.filter(
            sensor_id=sensor_id,
            timestamp__range=(start, end)
        ).order_by('timestamp'))

    def get_last_measurement(self, sensor_id: int) -> Optional[Measurement]:
        return Measurement.objects.filter(sensor_id=sensor_id).order_by('-timestamp').first()

    def get_sensor_statistics(self) -> List[Dict[str, Any]]:
        stats = []
        for sensor in Sensor.objects.all():
            count = Measurement.objects.filter(sensor=sensor).count()
            stats.append({
                'sensor_name': sensor.name,
                'status': sensor.status,
                'total_measurements': count,
                'last_seen': sensor.last_communication
            })
        return stats

    def get_logs(self, level: str) -> List[DataLog]:
        """
        Pobiera logi błędów według poziomu (np. ERROR).
        """
        return []

    def get_sensor_statistics(self) -> list:
        """
        Pobiera statystyki czujników.
        """
        return []

    def get_filtered_measurements(
            self,
            room: Optional[str] = None,
            metric: Optional[str] = None,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Pobiera pomiary z opcjonalnym filtrowaniem po pokoju, metryce(sensor_type) i czasie.
        """
        return []