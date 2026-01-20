from __future__ import annotations
from simulation.logic.src.base.devices.energysources.energygenerator import EnergyGenerator
from simulation.logic.src.base.weather import Weather



class WindTurbine(EnergyGenerator):
    def __init__(self, name: str, weather: Weather, rated_power_watt: float, rated_speed: float = 12.0):
        super().__init__(name, weather, rated_power_watt)
        self.rated_power = rated_power_watt
        self.rated_speed = rated_speed

    def update(self, millis_passed: int) -> None:
        super().update(millis_passed)
        if not self.is_active:
            self.available_energy = 0.0
            return
        wind = self.weather.get_wind_speed()

        if wind <= 0:
            power = 0.0
        elif wind > self.rated_speed:
            power = self.rated_power
        else:
            power = self.rated_power * (wind / self.rated_speed)

        hours = millis_passed / 3600000
        energy_generated = (power * hours)
        self.available_energy = energy_generated
        self.publish_state({
            "rated_speed": self.rated_speed,
        })
