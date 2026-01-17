# from rest_framework.views import APIView
# from rest_framework.response import Response
#
#
# class Index(APIView):
#     def post(self, request):
#         return Response({
#             "status": "success"
#         })
import json


from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from simulation.logic.src.base.devices.energysources.energystorage import EnergyStorage
from simulation.logic.src.base.devices.energysources.photovoltaic import PhotoVoltaic
from simulation.logic.src.base.devices.smartdevices.airconditioning import AirConditioning
from simulation.logic.src.base.devices.smartdevices.lighting import Lighting
from simulation.logic.src.base.electricgrid import ElectricGrid
from simulation.logic.src.base.simulation import Simulation
from simulation.logic.src.base.weatherTypes.insideWeather import InsideWeather
from simulation.logic.src.base.weatherTypes.outsideWeather import OutsideWeather

simulation = None

@require_http_methods(['GET'])
def index(request):
    return JsonResponse({"status": "success"})

@require_http_methods(['GET'])
def start_simulation (request):
    global simulation
    simulation = Simulation('simulation-1')
    if simulation is None:
        simulation = Simulation('simulation-1')
    if simulation.is_running():
        return JsonResponse({"status": "simulation is already running"}, status=400)

    simulation.base_millis_per_tick = 15 * 60 * 1000
    simulation.simulated_millis_per_tick = 5 * 1000

    outside_weather = OutsideWeather("out1", simulation)
    inside_weather = InsideWeather("in1", simulation, outside_weather)
    ac = AirConditioning("ac1", inside_weather, 3000,100)
    bulb1 = Lighting('bulb1', inside_weather, 15,1)
    bulb2 = Lighting('bulb2', inside_weather, 15,1)
    bulb3 = Lighting('bulb3', inside_weather, 15,1)
    bulb2.is_on = True
    bulb2.level = 0.5
    eg = ElectricGrid(simulation, 5000, 1.05)
    pv = PhotoVoltaic("pv1", outside_weather, 8000)
    es = EnergyStorage("main-battery", inside_weather, 150000, 8000, 5000)

    simulation.devices.append(bulb1)
    simulation.devices.append(bulb2)
    simulation.devices.append(bulb3)
    simulation.devices.append(ac)
    simulation.weathers.append(outside_weather)
    simulation.weathers.append(inside_weather)
    simulation.energy_generators.append(pv)
    simulation.energy_storages.append(es)
    simulation.electric_grid = eg

    simulation.start()
    return JsonResponse({"status": "simulation started"})

@require_http_methods(['GET'])
def stop_simulation (request):
    global simulation
    if simulation is None or not simulation.is_running():
        return JsonResponse({"status": "simulation is not running"}, status=400)

    simulation.stop()
    return JsonResponse({"status": "simulation stopped"})


@require_http_methods(['GET'])
def get_simulation_status (request):
    global simulation
    if simulation is None or not simulation.is_running():
        return JsonResponse({"status": "simulation is not running"}, status=400)

    weathers_data = []
    for weather in simulation.weathers:
        weathers_data.append({
            "name": weather.name,
            "type": weather.__class__.__name__,
            "temperature_celsius": weather.get_temperature(),
            "sunlight": weather.get_sunlight(),
            "brightness": weather.get_brightness(),
            "cloudiness": weather.get_cloudiness(),
            "wind": weather.get_wind_speed(),
        })
    return JsonResponse({
        "status": "simulation is running",
        "simulation": {
            "name": simulation.name,

            "base_millis_per_tick": simulation.base_millis_per_tick,
            "simulated_millis_per_tick": simulation.simulated_millis_per_tick,
            "current_tick": simulation.current_tick,
            "current_date": simulation.get_current_date(),

            "total_energy_required": simulation.calculate_total_energy_required(simulation.base_millis_per_tick),
            "calculate_total_energy_available": simulation.calculate_total_energy_available(simulation.base_millis_per_tick),

            "consumption_mode": simulation.mode,
            "weathers": weathers_data,
            "devices": [{
                "name": d.name,
                "is_active": d.is_active,
                "uuid": d.uuid,
            } for d in simulation.devices],
            "energy_storages": [{
                "name": d.name,
                "is_active": d.is_active,
                "uuid": d.uuid,
                "capacity_watts": d.capacity,
                "max_charge_watts": d.max_charge,
                "max_discharge_watts": d.max_discharge,
                "charge": d.charge,
            } for d in simulation.energy_storages],
            "energy_generators": [

            ],
            "electric_grid": [

            ],



        }
    })
