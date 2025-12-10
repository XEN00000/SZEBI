from __future__ import annotations

from simulation.logic.src.base.weatherTypes.insideWeather import InsideWeather
from simulation.logic.src.base.weatherTypes.outsideWeather import OutsideWeather
from simulation.logic.src.base.weather import Weather
from simulation.logic.src.base.device import Device

from simulation.logic.src.util.utils import validate_name
import paho.mqtt.client as mqtt
from uuid import UUID, uuid4

import weakref


class Environment:
    weather: Weather
    devices: list[Device] = []
    name: str

    def __init__(self, name: str, simulation, inside: bool = False):
        self._simulation = weakref.ref(simulation)
        self.weather = InsideWeather(self) if inside else OutsideWeather(self)
        self.uuid = uuid4()
        self.name = name
        self.mqtt = mqtt.Client(f"env-{self.uuid}")
        self.mqtt.connect("localhost")
        self.mqtt.loop_start()

    def sim(self):
        s = self._simulation()
        if s is None:
            raise RuntimeError('Environment exists outside of Simulation context')
        return s

    def update(self, millis_passed: int):
        self.weather.update(millis_passed)
        for d in self.devices:
            d.update(millis_passed)

    def set_name(self, name: str) -> None:
        validate_name(name)
        self.name = name
