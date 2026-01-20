from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
import json
from . import mqtt_runner
from .models import Sensor, DataLog, Measurement


@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def acquisition_status_api(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")
            msg = ""

            if action == "start":
                msg = mqtt_runner.start_mqtt_worker()
            elif action == "stop":
                msg = mqtt_runner.stop_mqtt_worker()

            return JsonResponse({
                "success": True,
                "message": msg,
                "running": mqtt_runner.is_running()
            })
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    is_running = mqtt_runner.is_running()
    return JsonResponse({
        "running": is_running,
        "status_text": "Działa (ON)" if is_running else "Zatrzymany (OFF)"
    })


@require_http_methods(["GET"])
def acquisition_stats_api(request):
    stats = []
    try:
        for sensor in Sensor.objects.all():
            count = Measurement.objects.filter(sensor=sensor).count()
            stats.append({
                'sensor_name': sensor.name,
                'status': str(sensor.status),
                'total_measurements': count,
                'last_seen': sensor.last_communication
            })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"stats": stats})


@require_http_methods(["GET"])
def acquisition_logs_api(request):
    level = request.GET.get("level", "ERROR")
    logs = DataLog.objects.filter(level=level).order_by('-timestamp')[:50]

    data = [{
        "id": l.pk,
        "timestamp": l.timestamp,
        "level": str(l.level),
        "message": l.message
    } for l in logs]

    return JsonResponse({"logs": data})