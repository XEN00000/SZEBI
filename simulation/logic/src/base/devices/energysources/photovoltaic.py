from __future__ import annotations
from simulation.logic.src.base.devices.energysources.energygenerator import EnergyGenerator
from simulation.logic.src.base.weather import Weather



class PhotoVoltaic(EnergyGenerator):
    def __init__(self, name: str, weather: Weather, rated_power_watt: float):
        super().__init__(name, weather, rated_power_watt)

    def calculate_available_energy(self, millis_passed: int) -> float:
        if not self.is_active:
            return 0.0

        brightness = self.weather.get_brightness()
        power = self.peak_power * brightness

        hours = millis_passed / 3600000
        energy_generated = (power * hours)
        self.publish_state({
            "energy_generated": energy_generated
        })
        return energy_generated
