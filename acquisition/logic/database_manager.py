# import datetime
# from typing import List, Optional, Dict, Any
# from acquisition.models import Measurement, DataLog, Sensor, SensorStatus
#
# class DatabaseManager:
#     def insert_measurements(self, measurement: Measurement) -> None:
#         try:
#             measurement.save()
#             print(f"DB: ZAPISANO POMIAR: ID={measurement.pk} Value={measurement.value}")
#         except Exception as e:
#             print(f"DB ERROR przy zapisie pomiaru: {e}")
#
#     def insert_data_log(self, log: DataLog) -> None:
#         try:
#             log.save()
#             print(f"DB: ZAPISANO LOG: {log.level} - {log.message[:30]}...")
#         except Exception as e:
#             print(f"DB ERROR przy zapisie logu: {e}")
#
#     def update_sensor(self, sensor_id: int, timestamp: datetime.datetime) -> None:
#         try:
#             Sensor.objects.filter(pk=sensor_id).update(last_communication=timestamp)
#         except Exception as e:
#             print(f"DB ERROR przy aktualizacji sensora: {e}")
#
#
#     # def insert_data_log(self, log: DataLog) -> None:
#     #     """
#     #     Rejestruje błędy walidacji, połączenia lub przetwarzania w tabeli data_logs.
#     #     """
#     #     print(f"DB: INSERT DATA_LOG: Level: {log.level}, Message: {log.message[:30]}...")
#
#     # def update_sensor(self, sensor_id: int, timestamp: datetime.datetime) -> None:
#     #     """
#     #     Aktualizuje last_communication w tabeli sensors.
#     #     """
#     #     print(f"DB: UPDATE SENSOR {sensor_id}: last_communication updated to {timestamp}")
#
#     def get_sensor(self, sensor_id: int) -> Optional[Sensor]:
#         """
#         Pobiera obiekt Sensor na podstawie sensor_id..
#         """
#         return Sensor.objects.filter(pk=sensor_id).first()
#         # print(f"DB: GET SENSOR {sensor_id}: Fikcyjny obiekt zwrócony.")
#         #
#         # return Sensor(
#         #     pk=sensor_id,
#         #     name=f"Sensor-{sensor_id}",
#         #     status=SensorStatus.ACTIVE
#         # )
#
#     def get_measurements(self, sensor_id: int, start: datetime.datetime, end: datetime.datetime) -> List[Measurement]:
#         return list(Measurement.objects.filter(
#             sensor_id=sensor_id,
#             timestamp__range=(start, end)
#         ).order_by('timestamp'))
#
#     def get_last_measurement(self, sensor_id: int) -> Optional[Measurement]:
#         return Measurement.objects.filter(sensor_id=sensor_id).order_by('-timestamp').first()
#
#     def get_sensor_statistics(self) -> List[Dict[str, Any]]:
#         stats = []
#         for sensor in Sensor.objects.all():
#             count = Measurement.objects.filter(sensor=sensor).count()
#             stats.append({
#                 'sensor_name': sensor.name,
#                 'status': sensor.status,
#                 'total_measurements': count,
#                 'last_seen': sensor.last_communication
#             })
#         return stats
#
#     def get_logs(self, level: str) -> List[DataLog]:
#         """
#         Pobiera logi błędów według poziomu (np. ERROR).
#         """
#         return list(DataLog.objects.filter(level=level).order_by('-timestamp'))
#
#     # def get_sensor_statistics(self) -> list:
#     #     """
#     #     Pobiera statystyki czujników.
#     #     """
#     #     return []
#
#     def get_filtered_measurements(
#             self,
#             room: Optional[str] = None,
#             metric: Optional[str] = None,
#             start_time: Optional[datetime.datetime] = None,
#             end_time: Optional[datetime.datetime] = None
#     ) -> List[Measurement]:
#         queryset = Measurement.objects.all()
#         """
#         Pobiera pomiary z opcjonalnym filtrowaniem po pokoju, metryce(sensor_type) i czasie.
#         """
#         if room:
#             queryset = queryset.filter(sensor__location__room=room)
#         if metric:
#             queryset = queryset.filter(sensor__type__name=metric)
#         if start_time:
#             queryset = queryset.filter(timestamp__gte=start_time)
#         if end_time:
#             queryset = queryset.filter(timestamp__lte=end_time)
#
#         return list(queryset.order_by('timestamp'))
import datetime
import threading
import queue
from typing import Optional, List, Dict, Any

from ..models import Measurement, DataLog
from acquisition.models import Sensor

class DatabaseManager:
    def __init__(self):
        # Kolejka do pomiarów
        self._measurement_queue = queue.Queue()
        self._worker_thread = threading.Thread(target=self._measurement_worker, daemon=True)
        self._worker_thread.start()

        # Kolejka dla DataLogs
        self._log_queue = queue.Queue()
        self._log_worker_thread = threading.Thread(target=self._log_worker, daemon=True)
        self._log_worker_thread.start()

    def insert_measurements(self, measurement: Measurement):
        """Wrzuć measurement do kolejki zamiast natychmiastowego zapisu"""
        self._measurement_queue.put(measurement)

    def _measurement_worker(self):
        batch = []
        batch_size = 50
        while True:
            measurement = self._measurement_queue.get()
            if measurement is None:  # sentinel do zamknięcia
                break
            batch.append(measurement)

            if len(batch) >= batch_size:
                try:
                    Measurement.objects.bulk_create(batch)
                except Exception as e:
                    print(f"DB ERROR przy bulk_create: {e}")
                batch.clear()
            self._measurement_queue.task_done()

        # zapis pozostałych elementów po zamknięciu kolejki
        if batch:
            try:
                Measurement.objects.bulk_create(batch)
            except Exception as e:
                print(f"DB ERROR przy bulk_create końcowym: {e}")



    def insert_data_log(self, data_log: DataLog):
        self._log_queue.put(data_log)

    def _log_worker(self):
        batch = []
        batch_size = 50
        while True:
            log = self._log_queue.get()
            if log is None:
                break
            batch.append(log)
            if len(batch) >= batch_size:
                try:
                    DataLog.objects.bulk_create(batch)
                except Exception as e:
                    print(f"DB ERROR przy bulk_create DataLog: {e}")
                batch.clear()

            self._log_queue.task_done()

        if batch:
            try:
                DataLog.objects.bulk_create(batch)
            except Exception as e:
                print(f"DB ERROR przy bulk_create DataLog końcowym: {e}")

    # -------------------
    # Pozostałe metody synchroniczne
    # -------------------
    def update_sensor(self, sensor_id: int, timestamp: datetime.datetime) -> None:
        try:
            Sensor.objects.filter(pk=sensor_id).update(last_communication=timestamp)
        except Exception as e:
            print(f"DB ERROR przy aktualizacji sensora: {e}")

    def get_sensor(self, sensor_id: int) -> Optional[Sensor]:
        return Sensor.objects.filter(pk=sensor_id).first()

    def get_measurements(self, sensor_id: int, start: datetime.datetime, end: datetime.datetime) -> List[
        Measurement]:
        return list(
            Measurement.objects.filter(sensor_id=sensor_id, timestamp__range=(start, end)).order_by(
                'timestamp'))

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
        return list(DataLog.objects.filter(level=level).order_by('-timestamp'))

    def get_filtered_measurements(
            self,
            room: Optional[str] = None,
            metric: Optional[str] = None,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None
    ) -> List[Measurement]:
        queryset = Measurement.objects.all()
        if room:
            queryset = queryset.filter(sensor__location__room=room)
        if metric:
            queryset = queryset.filter(sensor__type__name=metric)
        if start_time:
            queryset = queryset.filter(timestamp__gte=start_time)
        if end_time:
            queryset = queryset.filter(timestamp__lte=end_time)
        return list(queryset.order_by('timestamp'))

    def get_all_rooms(self) -> List[str]:
        return list(Sensor.objects.values_list('location__room', flat=True).distinct())

    def get_all_metrics(self) -> List[str]:
        return list(Sensor.objects.values_list('type__name', flat=True).distinct())

    def shutdown(self):
        self._measurement_queue.put(None)
        self._worker_thread.join()
        self._log_queue.put(None)
        self._log_worker_thread.join()

