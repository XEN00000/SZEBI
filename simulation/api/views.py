import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie

from .models import SimulationConfig, WeatherConfig, DeviceConfig
from . import services
from ..logic.src.base.electricgrid import ElectricGrid


def _get_sim_cfg(request):
    sim_id = request.GET.get("id") or request.POST.get("id")
    if not sim_id:
        return None, JsonResponse({"status": "missing simulation id"}, status=400)
    sim_cfg = SimulationConfig.objects.filter(id=sim_id).first()
    if not sim_cfg:
        return None, JsonResponse({"status": "no simulation found"}, status=404)
    return sim_cfg, None


def _restart_if_running(sim_cfg):
    if sim_cfg.id in services._simulation_runtime:
        services._simulation_runtime.pop(sim_cfg.id)
        services.start_simulation(sim_cfg)


@ensure_csrf_cookie
@require_http_methods(['GET'])
def index(request):
    return JsonResponse({"status": "success"})


@require_http_methods(['POST'])
def create_simulation(request):
    payload = json.loads(request.body or "{}")
    name = payload.get("name", "simulation-1")
    sim_cfg, _ = SimulationConfig.objects.get_or_create(name=name)
    return JsonResponse({"status": "simulation created", "id": str(sim_cfg.id), "name": sim_cfg.name})


@require_http_methods(['GET'])
def start_simulation(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.start_simulation(sim_cfg)
    return JsonResponse({"status": "simulation started", "id": str(sim_cfg.id), "running": sim.is_running()})


@require_http_methods(['GET'])
def stop_simulation(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    services.stop_simulation(sim_cfg)
    return JsonResponse({"status": "simulation stopped", "id": str(sim_cfg.id)})


@require_http_methods(['GET'])
def start_default_simulation(request):
    sim_cfg, _ = SimulationConfig.objects.get_or_create(name="simulation-1")
    # seed weathers/devices if empty
    if sim_cfg.weathers.count() == 0 and sim_cfg.devices.count() == 0:
        out_w = WeatherConfig.objects.create(simulation=sim_cfg, name="out1", type="outside")
        in_w = WeatherConfig.objects.create(simulation=sim_cfg, name="in1", type="inside", outside_ref=out_w)
        DeviceConfig.objects.create(simulation=sim_cfg, name="ac1", type="airconditioning", weather_ref=in_w,
                                    extra={"power": 1500, "standby_power": 50})
        for b in ("bulb1", "bulb2", "bulb3"):
            DeviceConfig.objects.create(simulation=sim_cfg, name=b, type="lighting", weather_ref=in_w,
                                        extra={"power": 15, "light_output": 1})
        DeviceConfig.objects.create(simulation=sim_cfg, name="pv1", type="photovoltaic", weather_ref=out_w,
                                    extra={"peak_power": 8000})
        DeviceConfig.objects.create(simulation=sim_cfg, name="main-battery", type="energystorage", weather_ref=in_w,
                                    extra={"capacity": 150000, "max_charge": 8000, "max_discharge": 5000})
        DeviceConfig.objects.create(simulation=sim_cfg, name="electric-grid", type="electricgrid", weather_ref=in_w,
                                    extra={"connection_power": 4000})
        DeviceConfig.objects.create(simulation=sim_cfg, name="heating", type="heating", weather_ref=in_w,
                                    extra={"power": 1500, "standby_power": 50})
        DeviceConfig.objects.create(simulation=sim_cfg, name="wind1", type="windturbine", weather_ref=in_w,
                                    extra={"rated_power": 3000})
    sim = services.start_simulation(sim_cfg)
    return JsonResponse({"status": "simulation started", "id": str(sim_cfg.id), "running": sim.is_running()})


@require_http_methods(['GET'])
def get_simulation_status(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.load_simulation(sim_cfg)
    if not sim.is_running():
        return JsonResponse({"status": "simulation is not running"}, status=400)

    return JsonResponse({
        "status": "simulation is running",
        "simulation": {
            "id": str(sim_cfg.id),
            "name": sim.name,
            "base_millis_per_tick": sim.base_millis_per_tick,
            "simulated_millis_per_tick": sim.simulated_millis_per_tick,
            "current_tick": sim.current_tick,
            "current_date": sim.get_current_date().isoformat(),
            "total_energy_required": sim.calculate_total_energy_required(sim.base_millis_per_tick),
            "total_energy_available": sim.calculate_total_energy_available(sim.base_millis_per_tick),
            "consumption_mode": sim.consumption_mode,
            "charging_mode": sim.charging_mode,
            "weathers": [{
                "name": w.name,
                "uuid": str(w.get_uuid()),
                "type": w.__class__.__name__,
                "temperature_celsius": w.get_temperature(),
                "sunlight": w.get_sunlight(),
                "brightness": w.get_brightness(),
                "cloudiness": w.get_cloudiness(),
                "wind": w.get_wind_speed(),
            } for w in sim.weathers],
            "devices": [{
                "name": d.name,
                "uuid": str(d.uuid),
                "type": d.__class__.__name__,
                "is_active": getattr(d, "is_active", True),
                "level": getattr(d, "level", None),
                "is_on": getattr(d, "is_on", None),
            } for d in sim.devices],
            "energy_storages": [{
                "name": d.name,
                "uuid": str(d.uuid),
                "capacity_watts": d.capacity,
                "max_charge_watts": d.max_charging_power,
                "max_discharge_watts": d.max_discharging_power,
                "charge": d.charge,
            } for d in sim.energy_storages],
            "energy_generators": [{
                "name": d.name,
                "uuid": str(d.uuid),
                "type": d.__class__.__name__,
                "peak_power": getattr(d, "peak_power", None),
            } for d in sim.energy_generators],
        }
    })


@require_http_methods(['GET'])
def get_simulation_summary(request):
    total = SimulationConfig.objects.count()
    last = SimulationConfig.objects.last()
    return JsonResponse({
        "total_simulations": total,
        "last_simulation_date": str(last.id) if last else None  # Using ID as proxy for now if date missing
    })


@require_http_methods(['GET'])
def get_simulation_history(request):
    # Using ID descending as proxy for recency if date field missing
    sims = SimulationConfig.objects.all().order_by('-id')[:10]
    return JsonResponse([{
        "id": str(s.id),
        "name": s.name,
        "date": "N/A" # Placeholder until model check
    } for s in sims], safe=False)


@require_http_methods(['GET'])
def list_devices(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.load_simulation(sim_cfg)
    if not sim.is_running():
        return JsonResponse({"status": "simulation is not running"}, status=400)
    return JsonResponse({
        "devices": [{
            "name": d.name,
            "uuid": str(d.uuid),
            "type": d.__class__.__name__,
            "is_active": getattr(d, "is_active", True),
            "level": getattr(d, "level", None),
            "is_on": getattr(d, "is_on", None),
        } for d in sim.devices]
    })


@require_http_methods(['GET'])
def device_status(request, device_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.load_simulation(sim_cfg)
    dev = next((d for d in sim.devices if str(d.uuid) == str(device_uuid)), None)
    if not dev:
        return JsonResponse({"status": "device not found"}, status=404)
    return JsonResponse({
        "device": {
            "name": dev.name,
            "uuid": str(dev.uuid),
            "type": dev.__class__.__name__,
            "is_active": getattr(dev, "is_active", True),
            "level": getattr(dev, "level", None),
            "is_on": getattr(dev, "is_on", None),
        }
    })


@require_http_methods(['POST'])
def add_device(request):
    data = json.loads(request.body or "{}")
    sim_id = data.get("simulation_id")
    sim_cfg = SimulationConfig.objects.filter(id=sim_id).first()
    if not sim_cfg:
        return JsonResponse({"status": "no simulation found"}, status=404)

    d_type = (data.get("type") or "").lower()
    name = data.get("name") or d_type or "device"
    weather_id = data.get("weather_id") or data.get("weather_uuid")
    if not weather_id:
        return JsonResponse({"status": "weather_id is required"}, status=400)

    weather = WeatherConfig.objects.filter(simulation=sim_cfg, id=weather_id).first()
    if not weather:
        return JsonResponse({"status": "weather not found"}, status=404)

    dc = DeviceConfig.objects.create(
        simulation=sim_cfg,
        name=name,
        type=d_type,
        weather_ref=weather,
        extra=data,
    )

    _restart_if_running(sim_cfg)
    return JsonResponse({"status": "device added", "uuid": str(dc.id)}, status=201)


@require_http_methods(['DELETE'])
def remove_device(request, device_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    qs = DeviceConfig.objects.filter(simulation=sim_cfg, id=device_uuid)
    if not qs.exists():
        return JsonResponse({"status": "device not found"}, status=404)
    qs.delete()
    _restart_if_running(sim_cfg)
    return JsonResponse({"status": "device deleted", "uuid": str(device_uuid)})


@require_http_methods(['GET'])
def list_weathers(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.load_simulation(sim_cfg)
    if not sim.is_running():
        return JsonResponse({"status": "simulation is not running"}, status=400)
    return JsonResponse({
        "weathers": [{
            "name": w.name,
            "uuid": str(w.get_uuid()),
            "type": w.__class__.__name__,
            "temperature_celsius": w.get_temperature(),
            "sunlight": w.get_sunlight(),
            "brightness": w.get_brightness(),
            "cloudiness": w.get_cloudiness(),
            "wind": w.get_wind_speed(),
        } for w in sim.weathers]
    })


@require_http_methods(['GET'])
def weather_status(request, weather_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    sim = services.load_simulation(sim_cfg)
    w = next((w for w in sim.weathers if str(w.get_uuid()) == str(weather_uuid)), None)
    if not w:
        return JsonResponse({"status": "weather not found"}, status=404)
    return JsonResponse({
        "weather": {
            "name": w.name,
            "uuid": str(w.get_uuid()),
            "type": w.__class__.__name__,
            "temperature_celsius": w.get_temperature(),
            "sunlight": w.get_sunlight(),
            "brightness": w.get_brightness(),
            "cloudiness": w.get_cloudiness(),
            "wind": w.get_wind_speed(),
        }
    })


@require_http_methods(['POST'])
def add_weather(request):
    data = json.loads(request.body or "{}")
    sim_id = data.get("simulation_id")
    sim_cfg = SimulationConfig.objects.filter(id=sim_id).first()
    if not sim_cfg:
        return JsonResponse({"status": "no simulation found"}, status=404)

    w_type = (data.get("type") or "").lower()
    name = data.get("name") or w_type or "weather"
    outside_id = data.get("outside_weather_id") or data.get("outside_id") or data.get(
        "outside_weather_uuid") or data.get("outside_uuid")

    outside = None
    if outside_id:
        outside = WeatherConfig.objects.filter(simulation=sim_cfg, id=outside_id,
                                               type=WeatherConfig.TYPE_OUTSIDE).first()
        if not outside:
            return JsonResponse({"status": "outside weather not found"}, status=404)

    if w_type == WeatherConfig.TYPE_INSIDE and outside is None:
        return JsonResponse({"status": "inside weather requires outside_weather_id"}, status=400)


    wc = WeatherConfig.objects.create(
        simulation=sim_cfg,
        name=name,
        type=w_type,
        outside_ref=outside, extra=data,
    )
    _restart_if_running(sim_cfg)
    return JsonResponse({"status": "weather added", "uuid": str(wc.id)}, status=201)


@require_http_methods(['DELETE'])
def remove_weather(request, weather_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    qs = WeatherConfig.objects.filter(simulation=sim_cfg, id=weather_uuid)
    if not qs.exists():
        return JsonResponse({"status": "weather not found"}, status=404)
    qs.delete()
    _restart_if_running(sim_cfg)
    return JsonResponse({"status": "weather deleted", "uuid": str(weather_uuid)})