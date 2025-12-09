from __future__ import annotations
from simulation.logic.src.base.devices.energysource import EnergySource
from simulation.logic.src.base.weather import Weather



class WindTurbine(EnergySource):
    def __init__(self, name: str, env, rated_power_watt: float, rated_speed: float = 12.0):
        super().__init__(name, env)
        self.rated_power = rated_power_watt
        self.rated_speed = rated_speed

    def calculate_production(self, weather: Weather, millis_passed: int) -> float:
        if not self.is_active:
            return 0.0
        wind = weather.get_wind_speed()

        if wind <= 0:
            power = 0.0
        elif wind > self.rated_speed:
            power = self.rated_power
        else:
            power = self.rated_power * (wind / self.rated_speed)

        hours = millis_passed / 3600000
        return (power * hours) / 1000.0
