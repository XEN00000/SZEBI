from __future__ import annotations
from ..smartdevice import SmartDevice



class AirConditioning(SmartDevice):
    def __init__(self, name: str, env, power_usage_watt: float):
        super().__init__(name, env, power_usage_watt)
        self.is_cooling = False

    def update(self, millis_passed: int):
        if not self.is_active:
            self.is_cooling = False

        if self.is_cooling:
            self.env().weather.apply_cooling(self.power_usage * self.level)

        self.publish_state({
            "is_cooling": self.is_cooling,
            "power_usage": self.get_power_usage(millis_passed)
        })

    def get_power_usage(self, millis_passed: int) -> float:
        if not self.is_active or not self.is_cooling:
            return 0.0
        return super().get_power_usage(millis_passed)
