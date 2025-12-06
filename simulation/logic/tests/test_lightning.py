from simulation.logic.base.devices.smartdevices.lighting import Lighting
from simulation.logic.base.weather import Weather

def test_lighting_turns_on_when_dark():
    w = Weather()
    w.brightness = 0.1

    light = Lighting("light", power_usage_watt=50, brightness_threshold=0.3)
    light.enable()

    light.update(1000, weather=w)
    assert light.is_on is True