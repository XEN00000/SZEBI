from django.urls import path
from . import views

urlpatterns = [
    path('control/', views.control_panel, name='control_panel'),
]