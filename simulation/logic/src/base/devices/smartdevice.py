from __future__ import annotations
from abc import ABC
from simulation.logic.src.base.device import Device
import json

from simulation.logic.src.base.simulation import Simulation
from simulation.logic.src.base.weather import Weather


class SmartDevice(Device, ABC):
    power_usage: float
    level: float

    def __init__(self, name: str, weather: Weather, power_usage_watt: float, standby_usage_watt: float):
        if type(self) is SmartDevice:
            raise TypeError("SmartDevice is abstract")
        super().__init__(name, weather)
        self.level = 0.0
        self.is_on = False
        self.power_usage = power_usage_watt
        self.standby_usage = standby_usage_watt

    def set_level(self, level: float):
        if level < 0.0 or level > 1.0:
            raise ValueError("Level must be between 0.0 and 1.0")
        self.level = max(0.0, min(1.0, level))
    
    def current_usage_watt(self) -> float:
        if not self.is_active:
            return 0.0

        if not self.is_on:
            return self.standby_usage

        return self.standby_usage + (self.power_usage * self.level)

    def calculate_required_energy(self, millis_passed: int) -> float:
        if not self.is_active:
            return 0.0

        hours = millis_passed / 3600000
        return (self.current_usage_watt() * hours) / 1000.0

    def publish_state(self, extra=None):
        topic = f"szebi/{self.sim().name}/devices/{self.uuid}/state"

        payload = {
            "name": self.name,
            "is_active": self.is_active,
            "is_on": self.is_on,
            "level": round(self.level * 100, 1),
            "power_usage": self.current_usage_watt(),
            "ts": int(self.sim().get_current_date().timestamp())
        }

        if extra:
            payload.update(extra)

        self.sim().mqtt.publish(topic, json.dumps(payload), qos=1, retain=True)
