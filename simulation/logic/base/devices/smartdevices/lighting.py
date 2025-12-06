from ..smartdevice import SmartDevice


class Lighting(SmartDevice):
    def __init__(self, name: str, power_usage_watt: float, brightness_threshold: float = 0.3):
        super().__init__(name, power_usage_watt)
        self.threshold = brightness_threshold
        self.is_on = False

    def update(self, millis_passed: int, weather=None, **kwargs):
        if weather is None:
            return

        if weather.get_brightness() < self.threshold:
            self.is_on = True
        else:
            self.is_on = False

    def get_power_usage(self, millis_passed: int) -> float:
        if not self.is_active or not self.is_on:
            return 0.0
        return super().get_power_usage(millis_passed)
