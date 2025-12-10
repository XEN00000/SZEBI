from __future__ import annotations
import math
import random
import weakref
from simulation import Simulation
from abc import abstractmethod, ABC
import json
import paho.mqtt.client as mqtt


class Weather(ABC):
    sunlight: float
    brightness: float
    cloudiness: float
    curr_lighting_power: float

    temperature: float
    temp_offset: float

    rainfall: float

    # should go into negative if env is being cooled
    curr_heating_power: float
    isolation: float

    wind: float
    wind_trend: float

    def __init__(self, env):
        self._simulation = weakref.ref(env.sim())
        self._environment = weakref.ref(env)
        self.wind_trend: float = random.uniform(-0.05, 0.05)
        self.temp_offset: float = random.uniform(-3.0, 3.0)

    def sim(self):
        s = self._simulation()

    def env(self):
        s = self._environment()
        if s is None:
            raise RuntimeError('Weather exists outside of Environment context')
        return s

    def publish_metric(self, metric: str, value, unit=""):
        payload = {
            "value": value,
            "unit": unit,
            "ts": int(self.sim().get_current_date().timestamp())
        }

        topic = f"szebi/{self.env().uuid}/weather/{metric}"
        self.env().mqtt.publish(topic, json.dumps(payload), qos=1, retain=True)

    def update(self, millis: int) -> None:
        self.curr_heating_power = 0
        self.curr_lighting_power = 0

        self.update_sunlight(millis)
        self.update_cloudiness(millis)
        self.update_rainfall(millis)
        self.update_wind(millis)
        self.update_temperature(millis)
        self.curr_heating_power = 0.0
        self.curr_lighting_power = 0.0

        self.publish_metric("temperature", self.temperature, "C")
        self.publish_metric("temperature", self.temperature, "C")
        self.publish_metric("sunlight", self.sunlight, "")
        self.publish_metric("brightness", self.brightness, "lumen")
        self.publish_metric("cloudiness", self.cloudiness, "percent")
        self.publish_metric("rainfall", self.rainfall, "mmh")
        self.publish_metric("wind", self.wind, "m/s")

    @abstractmethod
    def update_sunlight(self, millis: int) -> None:
        pass

    @abstractmethod
    def update_cloudiness(self, millis: int) -> None:
        pass

    @abstractmethod
    def update_rainfall(self, millis: int) -> None:
        pass

    @abstractmethod
    def update_wind(self, millis: int) -> None:
        pass

    @abstractmethod
    def update_temperature(self, millis: int) -> None:
        pass

    def apply_heating(self, watt: float):
        self.curr_heating_power += watt

    def apply_cooling(self, watt: float):
        self.curr_heating_power -= watt

    def apply_lighting(self, lumens: float):
        self.curr_lighting_power += lumens

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
