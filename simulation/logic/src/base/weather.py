from __future__ import annotations
import math
import random
import weakref
from abc import abstractmethod, ABC
import json
from uuid import uuid4

import paho.mqtt.client as mqtt

from simulation.logic.src.util.utils import validate_name


class Weather(ABC):
    name: str

    sunlight: float
    brightness: float
    cloudiness: float
    curr_lighting_power: float

    temperature: float
    temp_offset: float

    rainfall: float

    # should go into negative if env is being cooled
    curr_heating_power: float

    wind: float
    wind_trend: float

    def __init__(self, name: str, sim):
        self._simulation = weakref.ref(sim)
        self.set_name(name)
        self.uuid = uuid4()
        self.wind_trend: float = random.uniform(-0.05, 0.05)
        self.temp_offset: float = random.uniform(-3.0, 3.0)

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name

    def sim(self):
        return self._simulation()

    def publish_metric(self, metric: str, value, unit=""):
        topic = f"weather/{self.uuid}/{metric}"
        payload = {
            "weather_name": self.name,
            "metric_name": metric,
            "value": value,
            "unit": unit,
        }
        self.sim().publish_state(topic, payload)

    def update(self, millis: int) -> None:
        self.curr_heating_power = 0
        self.curr_lighting_power = 0

        self.update_sunlight(millis)
        self.update_cloudiness(millis)
        self.update_rainfall(millis)
        self.update_wind(millis)
        self.update_temperature(millis)


        self.publish_metric("temperature", self.temperature, "C")
        self.publish_metric("sunlight", self.sunlight, "")
        self.publish_metric("brightness", self.brightness, "lumen")
        self.publish_metric("cloudiness", self.cloudiness, "percent")
        self.publish_metric("rainfall", self.rainfall, "mmh")
        self.publish_metric("wind", self.wind, "m/s")
        self.publish_metric("heating_power", self.curr_heating_power, "W")
        self.publish_metric("lighting_power", self.curr_lighting_power, "W")
        self.curr_heating_power = 0.0
        self.curr_lighting_power = 0.0

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

    def get_name(self) -> str:
        return self.name

    def get_uuid(self) -> str:
        return str(self.uuid)
