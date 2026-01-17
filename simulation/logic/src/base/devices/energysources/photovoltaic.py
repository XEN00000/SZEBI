from __future__ import annotations
from simulation.logic.src.base.devices.energysources.energygenerator import EnergyGenerator
from simulation.logic.src.base.weather import Weather



class PhotoVoltaic(EnergyGenerator):
    def __init__(self, name: str, weather: Weather, rated_power_watt: float):
        super().__init__(name, weather, rated_power_watt)

    def update(self, millis_passed: int) -> None:
        if not self.is_active:
            self.available_energy = 0.0
            return

        power = self.peak_power * self.weather.get_brightness()
        hours = millis_passed / 3600000
        energy_generated = (power * hours)
        self.available_energy = energy_generated
        self.publish_state()
