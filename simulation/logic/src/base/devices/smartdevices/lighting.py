from __future__ import annotations
from ..smartdevice import SmartDevice



class Lighting(SmartDevice):
    def __init__(self, name: str, env, power_usage_watt: float):
        super().__init__(name, env, power_usage_watt)
        self.is_on = False

    def update(self, millis_passed: int):
        if not self.is_active:
            self.is_on = False

        if self.is_on:
            self.env().weather.apply_lighting(1200.0 * self.level)

        self.publish_state({
            "is_on": self.is_on,
            "power_usage": self.get_power_usage(millis_passed)
        })

    def get_power_usage(self, millis_passed: int) -> float:
        if not self.is_active or not self.is_on:
            return 0.0
        return super().get_power_usage(millis_passed)
