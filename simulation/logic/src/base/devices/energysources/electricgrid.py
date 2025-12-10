from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather


class ElectricGrid(EnergySource):
    def __init__(self, env, price_per_kwh: float = 0.8):
        super().__init__("electric-grid", env)
        self.price_per_kwh = price_per_kwh

    def calculate_production(self, weather: Weather, millis_passed: int) -> float:
        return 0.0

    def update(self, millis_passed: int) -> None:
        pass

    def supply(self, needed_kwh: float) -> float:
        return needed_kwh
