from simulation.logic.base.devices.energysources.energystorage import EnergyStorage

def test_battery_charging():
    battery = EnergyStorage("bat", 10, 2, 2)

    charged = battery.charge_battery(5)
    assert charged == 2   # max 2 kW per tick
    assert battery.charge == 2


def test_battery_discharging():
    battery = EnergyStorage("bat", 10, 2, 2)
    battery.charge = 5     # naładowana

    discharged = battery.discharge_battery(3)
    assert discharged == 2  # max discharge limit
    assert battery.charge == 3