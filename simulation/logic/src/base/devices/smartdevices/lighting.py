from __future__ import annotations
from ..smartdevice import SmartDevice
from ...weather import Weather


class Lighting(SmartDevice):
    def __init__(self, name: str, weather: Weather, power_usage_watt: float, standby_usage_watt: float):
        super().__init__(name, weather, power_usage_watt, standby_usage_watt)

    def update(self, millis_passed: int):
        if not self.is_active or self.level == 0.0:
            self.is_on = False

        if self.is_on:
            self.weather.apply_lighting(1200 * self.level)
        self.publish_state()