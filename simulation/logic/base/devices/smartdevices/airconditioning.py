from ..smartdevice import SmartDevice


class AirConditioning(SmartDevice):
    def __init__(self, name: str, power_usage_watt: float, target_temp: float = 24):
        super().__init__(name, power_usage_watt)
        self.target_temp = target_temp
        self.is_cooling = False

    def update(self, millis_passed: int, environment=None, **kwargs):
        if not self.is_active or environment is None:
            self.is_cooling = False
            return

        if environment.get_temperature() > self.target_temp:
            self.is_cooling = True
            environment.apply_cooling(self.power_usage)
        else:
            self.is_cooling = False

    def get_power_usage(self, millis_passed: int) -> float:
        if not self.is_active or not self.is_cooling:
            return 0.0
        return super().get_power_usage(millis_passed)
