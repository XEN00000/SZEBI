from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather


class ElectricGrid(EnergySource):
    def __init__(self, weather: Weather, connection_power: float, price_per_kwh: float = 0.8):
        super().__init__("electric-grid", weather)
        self.price_per_kwh = price_per_kwh

        if connection_power < 100 or connection_power > 1000000:
            raise ValueError("Connection power must be reasonable, so between 100W and 1MW")
        self.connection_power = connection_power

    def get_available_energy(self) -> float:
        return self.available_energy

    def update(self, millis_passed: int) -> None:
        if not self.is_active:
            return
        hours = millis_passed / 3600000
        self.available_energy = self.connection_power * hours
        self.publish_state()

    def supply(self, needed_watthours: float) -> float:
        if not self.is_active:
            return 0.0
        consumed_watthours = min(needed_watthours, self.available_energy)
        self.available_energy -= consumed_watthours
        self.publish_state({
            "consumed_watthours": consumed_watthours,
        })
        return consumed_watthours
        # TODO: wpis do bazy danych ile pradu zuzyto