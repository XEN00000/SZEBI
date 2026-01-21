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


def _get_sim_cfg_from_payload(payload, request):
    sim_id = payload.get("simulation_id") or payload.get("id") or request.GET.get("id") or request.POST.get("id")
    if not sim_id:
        return None, JsonResponse({"status": "missing simulation id"}, status=400)
    sim_cfg = SimulationConfig.objects.filter(id=sim_id).first()
    if not sim_cfg:
        return None, JsonResponse({"status": "no simulation found"}, status=404)
    return sim_cfg, None


def _parse_int(value, *, field_name):
    if value is None or value == "":
        return None, None
    try:
        return int(value), None
    except (TypeError, ValueError):
        return None, JsonResponse({"status": f"{field_name} must be an integer"}, status=400)


def _parse_float(value, *, field_name):
    if value is None or value == "":
        return None, None
    try:
        return float(value), None
    except (TypeError, ValueError):
        return None, JsonResponse({"status": f"{field_name} must be a number"}, status=400)


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
            "speed_ratio": (sim.base_millis_per_tick / sim.simulated_millis_per_tick)
            if sim.simulated_millis_per_tick else None,
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
def get_simulation_timing(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    base_tick = sim_cfg.base_millis_per_tick
    simulated_tick = sim_cfg.simulated_millis_per_tick
    speed_ratio = (base_tick / simulated_tick) if simulated_tick else None
    return JsonResponse({
        "status": "ok",
        "simulation": {
            "id": str(sim_cfg.id),
            "name": sim_cfg.name,
            "base_millis_per_tick": base_tick,
            "simulated_millis_per_tick": simulated_tick,
            "speed_ratio": speed_ratio,
        }
    })


@require_http_methods(['POST'])
def update_simulation_timing(request):
    payload = json.loads(request.body or "{}")
    sim_cfg, err = _get_sim_cfg_from_payload(payload, request)
    if err:
        return err

    base_tick, base_err = _parse_int(payload.get("base_millis_per_tick"), field_name="base_millis_per_tick")
    if base_err:
        return base_err
    speed_ratio, speed_err = _parse_float(payload.get("speed_ratio"), field_name="speed_ratio")
    if speed_err:
        return speed_err

    if base_tick is None and speed_ratio is None:
        return JsonResponse({"status": "nothing to update"}, status=400)

    if base_tick is not None:
        if base_tick < 1 or base_tick > 7 * 24 * 60 * 60 * 1000:
            return JsonResponse({
                "status": "base_millis_per_tick must be between 1 and 604800000"
            }, status=400)
        sim_cfg.base_millis_per_tick = base_tick

    if speed_ratio is not None:
        if speed_ratio < 0.01 or speed_ratio > 100.0:
            return JsonResponse({
                "status": "speed_ratio must be between 0.01 and 100.0"
            }, status=400)
        base_for_calc = sim_cfg.base_millis_per_tick
        simulated_tick = int(round(base_for_calc / speed_ratio))
        if simulated_tick < 1:
            return JsonResponse({
                "status": "speed_ratio results in invalid simulated_millis_per_tick"
            }, status=400)
        sim_cfg.simulated_millis_per_tick = simulated_tick

    sim_cfg.save(update_fields=["base_millis_per_tick", "simulated_millis_per_tick"])
    _restart_if_running(sim_cfg)

    speed_ratio_out = (sim_cfg.base_millis_per_tick / sim_cfg.simulated_millis_per_tick)
    return JsonResponse({
        "status": "timing updated",
        "simulation": {
            "id": str(sim_cfg.id),
            "name": sim_cfg.name,
            "base_millis_per_tick": sim_cfg.base_millis_per_tick,
            "simulated_millis_per_tick": sim_cfg.simulated_millis_per_tick,
            "speed_ratio": speed_ratio_out,
        }
    })


@require_http_methods(['GET'])
def list_devices(request):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    return JsonResponse({
        "devices": [{
            "name": d.name,
            "uuid": str(d.id),
            "type": d.type,
            "is_active": d.is_active,
            "level": d.initial_level,
            "is_on": d.initial_is_on,
            "weather_id": str(d.weather_ref.id),
        } for d in sim_cfg.devices.all()]
    })


@require_http_methods(['GET'])
def device_status(request, device_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    dev = DeviceConfig.objects.filter(simulation=sim_cfg, id=device_uuid).first()
    if not dev:
        return JsonResponse({"status": "device not found"}, status=404)
    return JsonResponse({
        "device": {
            "name": dev.name,
            "uuid": str(dev.id),
            "type": dev.type,
            "is_active": dev.is_active,
            "level": dev.initial_level,
            "is_on": dev.initial_is_on,
            "weather_id": str(dev.weather_ref.id),
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
    return JsonResponse({
        "weathers": [{
            "name": w.name,
            "uuid": str(w.id),
            "type": w.type,
            "outside_id": str(w.outside_ref.id) if w.outside_ref else None,
        } for w in sim_cfg.weathers.all()]
    })


@require_http_methods(['GET'])
def weather_status(request, weather_uuid):
    sim_cfg, err = _get_sim_cfg(request)
    if err:
        return err
    w = WeatherConfig.objects.filter(simulation=sim_cfg, id=weather_uuid).first()
    if not w:
        return JsonResponse({"status": "weather not found"}, status=404)
    return JsonResponse({
        "weather": {
            "name": w.name,
            "uuid": str(w.id),
            "type": w.type,
            "outside_id": str(w.outside_ref.id) if w.outside_ref else None,
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