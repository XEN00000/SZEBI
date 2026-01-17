from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('create', views.create_simulation, name="create"),
    path('start', views.start_simulation, name="start_created"),
    path('startdefault', views.start_default_simulation, name="start_default"),
    path('stop', views.stop_simulation, name="stop"),
    path('status', views.get_simulation_status, name="status"),
    
    path('device/list', views.list_devices, name="device_list"),
    path('device/status/<uuid:device_uuid>', views.device_status, name="device_status"),
    path('device/add', views.add_device, name="device_add"),
    path('device/remove/<uuid:device_uuid>', views.remove_device, name="device_remove"),

    path('weather/list', views.list_weathers, name="weather_list"),
    path('weather/status/<weather_uuid>', views.weather_status, name="weather_status"),
    path('weather/add', views.add_weather, name="weather_add"),
    path('weather/remove/weather_uuid>', views.remove_weather, name="weather_remove"),

]