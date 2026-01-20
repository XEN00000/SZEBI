from django.urls import path
from . import views

urlpatterns = [
    path('control/', views.acquisition_status_api, name='control_panel'),
    path('api/status/', views.acquisition_status_api, name='api_status'),
    path('api/stats/', views.acquisition_stats_api, name='api_stats'),
    path('api/logs/', views.acquisition_logs_api, name='api_logs'),
]