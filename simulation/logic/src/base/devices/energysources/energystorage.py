from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather



class EnergyStorage(EnergySource):
    def __init__(self, name: str, weather: Weather, capacity_watts: float, max_charge_watts: float, max_discharge_watts: float) -> None:
        super().__init__(name, weather)
        self.capacity = capacity_watts
        self.charge = 0.0 # watts
        self.max_charge = max_charge_watts
        self.max_discharge = max_discharge_watts

    def charge_battery(self, supplied_watts: float, millis: float) -> float:
        hours = millis / 3600000
        accepted = min(self.capacity - self.charge, self.max_charge * hours, supplied_watts)
        self.charge += accepted
        return accepted

    def discharge_battery(self, needed_watts: float, millis: float) -> float:
        hours = millis / 3600000
        provided = min(self.charge, self.max_discharge * hours, needed_watts)
        self.charge -= provided
        return provided

    def calculate_available_energy(self, millis_passed: int) -> float:
        hours = millis_passed / 3600000
        return min((self.max_discharge * hours), self.charge)
