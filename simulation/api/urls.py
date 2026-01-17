from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('start', views.start_simulation, name="start"),
    path('stop', views.stop_simulation, name="stop"),
    path('status', views.get_simulation_status, name="status"),
]