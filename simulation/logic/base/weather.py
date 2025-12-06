import math
import random
from datetime import datetime, timedelta


class Weather:
    def __init__(self):
        self.datetime = datetime.now()

        self.sunlight = 0.0
        self.brightness = 0.0
        self.cloudiness = 0.3
        self.wind = 2.0
        self.temperature = 15.0
        self.rainfall = 0.0

        self.wind_trend = random.uniform(-0.05, 0.05)
        self.temp_offset = random.uniform(-3.0, 3.0)

    def update(self, millis: int):
        self.datetime += timedelta(milliseconds=millis)

        self.update_sunlight()
        self.update_cloudiness()
        self.update_rainfall()
        self.update_wind()
        self.update_temperature()

    def update_sunlight(self):
        hour = self.datetime.hour + self.datetime.minute / 60.0
        day_phase = (hour - 6) / 12 * math.pi
        sun = math.sin(day_phase)

        self.sunlight = max(0.0, min(1.0, sun))
        self.brightness = self.sunlight * (1 - self.cloudiness * 0.8)

    def update_cloudiness(self):
        self.cloudiness += random.uniform(-0.02, 0.02)
        self.cloudiness = max(0.0, min(1.0, self.cloudiness))

    def update_rainfall(self):
        if self.cloudiness > 0.6:
            if random.random() < 0.1:
                self.rainfall = random.uniform(0.5, 5.0)
        else:
            self.rainfall = 0.0

    def update_wind(self):
        self.wind_trend += random.uniform(-0.02, 0.02)
        self.wind_trend = max(-0.1, min(0.1, self.wind_trend))

        self.wind += self.wind_trend
        self.wind = max(0.0, self.wind)

    def update_temperature(self):
        hour = self.datetime.hour + self.datetime.minute / 60
        day_cycle = math.sin((hour - 5) / 24 * 2 * math.pi)

        base = 12 + day_cycle * 8
        noise = random.uniform(-0.3, 0.3)

        self.temperature = base + self.temp_offset + noise

    def get_temperature(self):
        return self.temperature

    def get_sunlight(self):
        return self.sunlight

    def get_brightness(self):
        return self.brightness

    def get_cloudiness(self):
        return self.cloudiness

    def get_rainfall(self):
        return self.rainfall

    def get_wind_speed(self):
        return self.wind

    def get_datetime(self):
        return self.datetime