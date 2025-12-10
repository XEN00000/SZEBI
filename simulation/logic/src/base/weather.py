import math
import random
import weakref

from simulation import Simulation

class Weather:
    def __init__(self, simulation: Simulation):
        self._simulation = weakref.ref(simulation)

        self.sunlight: float = 0.0
        self.brightness: float = 0.0
        self.cloudiness: float = 0.3
        self.wind: float = 2.0
        self.temperature: float = 15.0
        self.rainfall: float = 0.0
        
        self.isolation: float = 0.85
        
        # should go into negative if env is being cooled
        self.curr_heating_power = 0.0

        self.wind_trend: float = random.uniform(-0.05, 0.05)
        self.temp_offset: float = random.uniform(-3.0, 3.0)

    def sim(self) -> Simulation:
        s = self._simulation() 
        if s is None:
            raise RuntimeError('Weather exists outside of Simulation context')
        return s

    def update(self, millis: int) -> None:
        self.update_sunlight()
        self.update_cloudiness()
        self.update_rainfall()
        self.update_wind()
        self.update_temperature()

    def update_sunlight(self) -> None:
        date = self.sim().get_current_date()
        hour = date.hour + date.minute / 60.0
        day_phase = (hour - 6) / 12 * math.pi
        sun = math.sin(day_phase)

        self.sunlight = max(0.0, min(1.0, sun))
        self.brightness = self.sunlight * (1 - self.cloudiness * 0.8)

    def update_cloudiness(self) -> None:
        self.cloudiness += random.uniform(-0.02, 0.02)
        self.cloudiness = max(0.0, min(1.0, self.cloudiness))

    def update_rainfall(self) -> None:
        if self.cloudiness > 0.6:
            if random.random() < 0.1:
                self.rainfall = random.uniform(0.5, 5.0)
        else:
            self.rainfall = 0.0

    def update_wind(self) -> None:
        self.wind_trend += random.uniform(-0.02, 0.02)
        self.wind_trend = max(-0.1, min(0.1, self.wind_trend))

        self.wind += self.wind_trend
        self.wind = max(0.0, self.wind)

    def update_temperature(self) -> None:
        date = self.sim().get_current_date()
        hour = date.hour + date.minute / 60
        day_cycle = math.sin((hour - 5) / 24 * 2 * math.pi)

        base = 12 + day_cycle * 8
        noise = random.uniform(-0.3, 0.3)

        self.temperature = base + self.temp_offset + noise
        
    def apply_heating(self, watt: float):
        self.curr_heating_power += watt

    def apply_cooling(self, watt: float):
        self.curr_heating_power -= watt

    def get_temperature(self) -> float:
        return self.temperature

    def get_sunlight(self) -> float:
        return self.sunlight

    def get_brightness(self) -> float:
        return self.brightness

    def get_cloudiness(self) -> float:
        return self.cloudiness

    def get_rainfall(self) -> float:
        return self.rainfall

    def get_wind_speed(self) -> float:
        return self.wind