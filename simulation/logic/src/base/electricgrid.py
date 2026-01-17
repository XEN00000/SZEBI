from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather


class ElectricGrid(EnergySource):
    def __init__(self, sim, connection_power: float, price_per_kwh: float = 0.8):
        super().__init__("electric-grid", sim)
        self.price_per_kwh = price_per_kwh

        if connection_power < 100 or connection_power > 1000000:
            raise ValueError("Connection power must be reasonable, so between 100W and 1MW")
        self.connection_power = connection_power

    def calculate_required_energy(self, millis_passed: int) -> float:
        return 0.0

    def calculate_available_energy(self, millis_passed: int) -> float:
        hours = millis_passed / 3600000
        return (self.connection_power * hours) / 1000.0

    def update(self, millis_passed: int) -> None:
        pass

    def supply(self, needed_kwh: float) -> float:
        self.count_consumption(needed_kwh)
        return needed_kwh

    # wyslac do bazy danych / do mqtt w zaleznosci od tego co chca
    def count_consumption(self, consumed_kwh: float) -> float:
        pass