from simulation.logic.base.devices.energysources.electricgrid import ElectricGrid

def test_electric_grid_supplies_energy():
    grid = ElectricGrid()

    assert grid.supply(5) == 5