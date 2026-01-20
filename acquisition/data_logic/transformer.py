from typing import Dict, Callable

from ..logic.database_manager import DatabaseManager
from ..models import Measurement, DataLog, DataLogLevel

class Transformer:
    def __init__(self, db_manager: DatabaseManager):

        self.db_manager = db_manager

        # Tabela konwersji jednostek: Simulation → Measurement / DB
        self.conversion_table: Dict[str, Callable[[float], float]] = {
            # --- Temperatura ---
            "C": lambda x: x,  # C → C
            "F": lambda x: (x - 32) * 5 / 9,  # F → C

            # --- Prędkość wiatru ---
            "m/s": lambda x: x,  # m/s → m/s
            "km/h": lambda x: x / 3.6,  # km/h → m/s

            # --- Opady ---
            "mm": lambda x: x,  # mm → mm
            "mm/h": lambda x: x,  # mm/h → mm/h
            "mmh": lambda x: x,  # "mmh" → mm/h

            # --- Światło / jasność ---
            "lux": lambda x: x,  # lux → lux
            "lumen": lambda x: x / 100,  # lumeny → lux

            # --- Moc i energia ---
            "W": lambda x: x,  # W → W
            "kW": lambda x: x * 1000,  # kW → W
            "kWh": lambda x: x,  # kWh → kWh

            # --- Procenty / ułamki ---
            "%": lambda x: x / 100.0,  # % → 0.0–1.0
            "percent": lambda x: x / 100.0, # % → 0–1
            "fraction": lambda x: x  # fraction → 0.0–1.0
        }

    def convert_units(self, measurement: Measurement) -> Measurement:
        unit = getattr(measurement, "unit", None)
        if unit in self.conversion_table:
            try:
                measurement.value = self.conversion_table[unit](measurement.value)
            except Exception as e:
                msg = f"TRANSFORMER ERROR: błąd konwersji {measurement.value} [{unit}]: {e}"
                print(msg)
                self._log(msg, DataLogLevel.ERROR, measurement)
        else:
            msg = f"TRANSFORMER WARNING: jednostka {unit} nie jest zdefiniowana w tabeli konwersji"
            print(msg)
            self._log(msg, DataLogLevel.WARNING, measurement)
        return measurement

    def _log(self, message: str, level: str, measurement: Measurement):
        self.db_manager.insert_data_log(DataLog(
            measurement=measurement,
            level=level,
            message=message[:255]
        ))
