from __future__ import annotations
import math
from numpy import random
from simulation.logic.src.base.weather import Weather


class OutsideWeather(Weather):
    def __init__(self, simulation):
        super().__init__(simulation)

        self.sunlight: float = 0.0
        self.brightness: float = 0.0
        self.cloudiness: float = 0.3

        self.wind: float = 2.0
        self.temperature: float = 15.0
        self.rainfall: float = 0.0

        self.isolation: float = 0.80

        self.curr_heating_power = 0.0

        self.wind_trend: float = random.uniform(-0.05, 0.05)
        self.temp_offset: float = random.uniform(-3.0, 3.0)

    def update_sunlight(self, millis: int) -> None:
        date = self.sim().get_current_date()
        hour = date.hour + date.minute / 60.0
        day_phase = (hour - 6) / 12 * math.pi
        sun = math.sin(day_phase)

        self.sunlight = max(0.0, min(1.0, sun))
        self.brightness = self.sunlight * (1 - self.cloudiness * 0.6)

    def update_cloudiness(self, millis: int) -> None:
        self.cloudiness += (random.uniform(-0.02, 0.02) / (60 * 1000)) * millis
        self.cloudiness = max(0.0, min(1.0, self.cloudiness))

    def update_rainfall(self, millis: int) -> None:
        if self.cloudiness > 0.6:
            if random.random() < 0.1:
                self.rainfall = random.uniform(0.5, 5.0)
        else:
            self.rainfall = 0.0

    def update_wind(self, millis: int) -> None:
        self.wind_trend += (random.uniform(-0.05, 0.05) / (60 * 1000)) * millis
        self.wind_trend = max(-0.1, min(0.1, self.wind_trend))

        self.wind += self.wind_trend
        self.wind = max(0.0, self.wind)

    def update_temperature(self, millis: int) -> None:
        date = self.sim().get_current_date()
        hour = date.hour + date.minute / 60
        day_cycle = math.sin((hour - 5) / 24 * 2 * math.pi)

        base = 12 + day_cycle * 8
        noise = random.uniform(-0.3, 0.3)

        self.temperature = base + self.temp_offset + noise
