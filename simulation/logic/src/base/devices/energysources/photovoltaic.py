from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather



class PhotoVoltaic(EnergySource):
    def __init__(self, name: str, env, peak_power_watt: float):
        super().__init__(name, env)
        self.peak_power = peak_power_watt

    def calculate_production(self, weather: Weather, millis_passed: int) -> float:
        if not self.is_active:
            return 0.0

        brightness = weather.get_brightness()
        power = self.peak_power * brightness

        hours = millis_passed / 3600000
        return (power * hours) / 1000.0  #
