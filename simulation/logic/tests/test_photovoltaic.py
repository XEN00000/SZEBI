from simulation.logic.base.devices.energysources.photovoltaic import PhotoVoltaic
from simulation.logic.base.weather import Weather

def test_pv_produces_energy():
    pv = PhotoVoltaic("pv1", peak_power_watt=5000)
    pv.enable()

    w = Weather()
    w.brightness = 1.0

    produced = pv.calculate_production(w, 3600000)
    assert 4.5 <= produced <= 5.1  # 5 kWh ± noise
