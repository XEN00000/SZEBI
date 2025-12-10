from simulation.logic.base.weather import Weather

def test_weather_updates_time():
    w = Weather()
    before = w.get_datetime()
    w.update(15 * 60 * 1000)
    assert w.get_datetime() > before


def test_weather_brightness_range():
    w = Weather()
    w.update(1000)
    assert 0.0 <= w.get_brightness() <= 1.0


def test_weather_temp_changes():
    w = Weather()
    t1 = w.get_temperature()
    w.update(15 * 60 * 1000)
    t2 = w.get_temperature()
    assert isinstance(t2, float)
    assert t1 != t2  # temperatura musi się zmieniać
