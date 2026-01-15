from django.shortcuts import render, redirect
from django.contrib import messages
from . import mqtt_runner

def control_panel(request):
    status = "Działa (ON)" if mqtt_runner.is_running() else "Zatrzymany (OFF)"
    status_class = "success" if mqtt_runner.is_running() else "danger"

    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "start":
            msg = mqtt_runner.start_mqtt_worker()
            messages.success(request, msg)
        elif action == "stop":
            msg = mqtt_runner.stop_mqtt_worker()
            messages.warning(request, msg)
            
        return redirect('control_panel')

    context = {
        'status': status,
        'status_class': status_class
    }
    return render(request, 'acquisition/control_panel.html', context)