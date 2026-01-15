from django.urls import path
from .views import AlarmWebhookView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlarmWebhookView, 
    DeviceListView, 
    RunOptimizationView,
    OptimizationRuleViewSet, 
    UserPreferenceViewSet
)
# Router automatycznie tworzy ścieżki dla ViewSetów (
router = DefaultRouter()
router.register(r'rules', OptimizationRuleViewSet)
router.register(r'preferences', UserPreferenceViewSet)

urlpatterns = [
    # API operacyjne (Alarmy, Uruchamianie, Lista urządzeń)
    path('alarm/', AlarmWebhookView.as_view(), name='receive_alarm'),
    path('devices/', DeviceListView.as_view(), name='list_devices'),
    path('run/', RunOptimizationView.as_view(), name='run_optimization'),

    # API konfiguracyjne (dołączamy router)
    path('', include(router.urls)),
]