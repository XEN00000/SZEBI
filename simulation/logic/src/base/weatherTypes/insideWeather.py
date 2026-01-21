from __future__ import annotations
import math
from numpy import random

from simulation.logic.src.base.simulation import Simulation
from simulation.logic.src.base.weather import Weather
from simulation.logic.src.base.weatherTypes.outsideWeather import OutsideWeather


class InsideWeather(Weather):
    def __init__(self, name:str, simulation: Simulation, outsideWeather: OutsideWeather):
        super().__init__(name, simulation)

        if outsideWeather is None:
            raise ValueError("OutsideWeather must be provided")
        
        self.outsideWeather = outsideWeather
        
        self.sunlight: float = 0.0
        self.brightness: float = 0.0
        self.cloudiness: float = 1

        self.wind: float = 0.0
        self.temperature: float = 22.0
        self.rainfall: float = 0.0

        self.isolation: float = 0.95
        self.transfer_rate: float = 1.5

        self.curr_lighting_power = 0.0
        self.curr_heating_power = 0.0
        self.celsius_per_kwh = 0.35

        self.wind_trend: float = random.uniform(-0.05, 0.05)
        self.temp_offset: float = random.uniform(-3.0, 3.0)

    def update_sunlight(self, millis: int) -> None:
        date = self.sim().get_current_date()
        hour = date.hour + date.minute / 60.0
        day_phase = (hour - 6) / 12 * math.pi
        sun = math.sin(day_phase)

        self.sunlight = max(0.0, min(1.0, sun))
        self.brightness = self.sunlight * (1 - self.cloudiness * 0.6) * 0.5 * 25000
        self.brightness += self.curr_lighting_power

    def update_cloudiness(self, millis: int) -> None:
        pass

    def update_rainfall(self, millis: int) -> None:
        pass

    def update_wind(self, millis: int) -> None:
        pass

    def update_temperature(self, millis: int) -> None:
        outside_temp = self.outsideWeather.temperature

        hours_passed = millis / 3600000.0
        exchange_factor = (1.0 - self.isolation) * self.transfer_rate
        temp_diff = outside_temp - self.temperature

        self.temperature += temp_diff * exchange_factor * hours_passed

        energy_kwh = (self.curr_heating_power / 1000.0) * hours_passed
        self.temperature += energy_kwh * self.celsius_per_kwh # maybe necessary to split into heating_celcius_per_kwh and cooling_celcius_per_kwh