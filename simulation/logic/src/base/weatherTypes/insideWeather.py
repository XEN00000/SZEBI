from __future__ import annotations
import math
from numpy import random
from simulation.logic.src.base.weather import Weather


class InsideWeather(Weather):
    def __init__(self, simulation):
        super().__init__(simulation)

        self.sunlight: float = 0.0
        self.brightness: float = 0.0
        self.cloudiness: float = 1

        self.wind: float = 0.0
        self.temperature: float = 22.0
        self.rainfall: float = 0.0

        self.isolation: float = 0.80
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

    # do poprawy bo dom bedzie mial chyba z 10000 stopni
    def update_temperature(self, millis: int) -> None:
        SPEED_OF_CHILLING = 0.5
        self.temperature -= (SPEED_OF_CHILLING * self.isolation / (60 * 60 * 1000)) * millis
        self.temperature += self.curr_heating_power * (millis / 3600) * self.celsius_per_kwh
