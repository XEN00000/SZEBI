from __future__ import annotations

from fontTools.subset import usage

from ..smartdevice import SmartDevice


class Heating(SmartDevice):
    def __init__(self, name: str, env, power_usage_watt: float):
        super().__init__(name, env, power_usage_watt)
        self.is_heating = False

    def update(self, millis_passed: int):

        if self.is_active:
            usage = 1.0
            if self.is_heating:
                usage += 5.0 * self.level

            if not super().env().declare_usage(usage, millis_passed):
                self.is_heating = False
            else:
                if self.is_heating:
                    self.env().weather.apply_heating(self.power_usage * self.level)
                self.publish_state({
                    "is_heating": self.is_heating,
                    "power_usage": self.get_power_usage(millis_passed)
                })

    def get_power_usage(self, millis_passed: int) -> float:
        if not self.is_active or not self.is_heating:
            return 0.0
        return super().get_power_usage(millis_passed)
