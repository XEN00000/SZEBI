from ..logic.database_manager import DatabaseManager
from ..models import Measurement, DataLog, DataLogLevel

class Validator:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def validate(self, data: Measurement, topic: str = None, raw_message: str = None) -> bool:
        if data.value is None:
            self.db_manager.insert_data_log(DataLog(
                measurement=data,
                level=DataLogLevel.WARNING,
                message=f"Brak wartości pomiaru | topic: {topic} | raw: {raw_message}"[:255]
            ))
            return False

        try:
            sensor_type = data.sensor.type

            # Sprawdzenie minimum
            if sensor_type.min_value is not None and data.value < sensor_type.min_value:
                self.db_manager.insert_data_log(DataLog(
                    measurement=data,
                    level=DataLogLevel.WARNING,
                    message=f"Wartość {data.value} poniżej minimum {sensor_type.min_value} | topic: {topic} | raw: {raw_message}"[
                        :255]
                ))
                return False

            # Sprawdzenie maksimum
            if sensor_type.max_value is not None and data.value > sensor_type.max_value:
                self.db_manager.insert_data_log(DataLog(
                    measurement=data,
                    level=DataLogLevel.WARNING,
                    message=f"Wartość {data.value} powyżej maksimum {sensor_type.max_value} | topic: {topic} | raw: {raw_message}"[
                        :255]
                ))
                return False
                
        except (AttributeError, TypeError) as e:
            self.db_manager.insert_data_log(DataLog(
                measurement=data,
                level=DataLogLevel.ERROR,
                message=f"Błąd walidacji: {e} | topic: {topic} | raw: {raw_message}"[:255]
            ))
            return False

        return True