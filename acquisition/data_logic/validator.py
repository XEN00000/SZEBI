from typing import Dict
from ..models import Measurement, SensorType

class Validator:
    def validate(self, data: Measurement) -> bool:
        if data.value is None:
            return False

        try:
            sensor_type = data.sensor.type 
            
            if sensor_type.min_value is not None and data.value < sensor_type.min_value:
                print(f"VALIDATION ERROR: Wartość {data.value} poniżej minimum ({sensor_type.min_value})")
                return False
                
            if sensor_type.max_value is not None and data.value > sensor_type.max_value:
                print(f"VALIDATION ERROR: Wartość {data.value} powyżej maksimum ({sensor_type.max_value})")
                return False
                
        except Exception as e:
            print(f"VALIDATION WARNING: Nie udało się sprawdzić limitów: {e}")

        return True