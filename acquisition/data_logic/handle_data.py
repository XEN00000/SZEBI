import datetime
import traceback
from typing import Dict, Optional
from ..logic.database_manager import DatabaseManager
from ..models import Measurement, DataLog, MeasurementStatus, DataLogLevel, Location, SensorType, Sensor
from .validator import Validator
from .deduplicator import Deduplicator
from .transformer import Transformer
from django.utils import timezone

class HandleData:
    def __init__(self, db_manager: DatabaseManager, validator: Validator, deduplicator: Deduplicator, transformer: Transformer):
        self.validator = validator
        self.deduplicator = deduplicator
        self.transformer = transformer
        self.db_manager = db_manager

    def process(self, raw_data: Dict) -> Optional[Measurement]:
        try:
            return self._convert_raw_to_measurement(raw_data)
        except Exception as e:
            print(f"!!! BŁĄD PRZETWARZANIA: {raw_data}")
            print(traceback.format_exc())
            
            try:
                self.db_manager.insert_data_log(DataLog(
                    level=DataLogLevel.CRITICAL,
                    message=f"BŁĄD DANYCH: {str(e)[:100]}"
                ))
            except:
                pass
            return None

    def _convert_raw_to_measurement(self, raw_data: Dict) -> Optional[Measurement]:
        sensor = self._find_or_create_sensor(raw_data['location_uuid'], raw_data['param_name'])
        
        try:
            ts = datetime.datetime.fromisoformat(raw_data['timestamp'])
        except:
            ts = timezone.now()

        measurement = Measurement(
            sensor=sensor,
            timestamp=ts,
            value=raw_data['value'],
            status=MeasurementStatus.OK
        )
        
        if not self.validator.validate(measurement):
            measurement.status = MeasurementStatus.ERROR
        
        self.db_manager.insert_measurements(measurement)
        return measurement

    def _find_or_create_sensor(self, location_uuid: str, param_name: str) -> Sensor:
        sensor_type_obj, _ = SensorType.objects.get_or_create(
            name__iexact=param_name,
            defaults={'name': param_name, 'default_unit': 'raw'}
        )
        
        location, _ = Location.objects.get_or_create(
            room=location_uuid,
            defaults={'room': location_uuid}
        )

        sensor, created = Sensor.objects.get_or_create(
            location=location,
            type=sensor_type_obj,
            defaults={
                'name': f"{sensor_type_obj.name} w {location.room}", 
                'status': 'ACTIVE'
            }
        )
        
        if created:
            print(f"INFO: Utworzono nowy sensor: {sensor.name}")
            
        return sensor