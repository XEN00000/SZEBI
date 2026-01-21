from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather



class EnergyStorage(EnergySource):
    def __init__(self, name: str, weather: Weather, capacity_watts: float, max_charging_watts: float, max_discharging_watts: float) -> None:
        super().__init__(name, weather)
        self.capacity = capacity_watts
        self.charge = 0.0 # watts
        self.max_charging_power = max_charging_watts
        self.max_discharging_power = max_discharging_watts
        self.max_energy_can_take = 0.0

    def charge_battery(self, supplied_watthours: float) -> float:
        if not self.is_active:
            return 0.0
        accepted = min(self.max_energy_can_take, supplied_watthours)
        self.max_energy_can_take -= accepted
        self.charge += accepted
        return accepted

    def get_max_energy_can_take(self) -> float:
        return self.max_energy_can_take

    def update(self, millis_passed: int) -> None:
        super().update(millis_passed)
        if not self.is_active:
            self.available_energy = 0.0
            return
        hours = millis_passed / 3600000
        self.available_energy = min((self.max_discharging_power * hours), self.charge)
        self.max_energy_can_take = min((self.max_charging_power * hours), self.capacity - self.charge)
        self.publish_state({
            "capacity": self.capacity,
            "charge": self.charge,
            "max_charge_power": self.max_charging_power,
            "max_discharge_power": self.max_discharging_power,
            "max_energy_can_take": self.max_energy_can_take,
        })
