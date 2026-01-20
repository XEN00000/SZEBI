from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from optimization.models import OptimizationRule, UserPreference, OptimizationLog
from optimization.logic.controller import OptimizationController
from optimization.integration.repositories import DeviceRepository

from .serializers import (
    ExternalAlarmSerializer,     
    DeviceSerializer, 
    OptimizationResultSerializer,
    OptimizationRuleSerializer, 
    UserPreferenceSerializer,
    OptimizationLogSerializer
)

# Dostępne warunki dla reguł optymalizacji
AVAILABLE_CONDITIONS = [
    {"value": "price", "label": "Cena energii"},
    {"value": "time", "label": "Czas"},
    {"value": "temperature", "label": "Temperatura"},
    {"value": "humidity", "label": "Wilgotność"},
    {"value": "power_consumption", "label": "Zużycie mocy"},
    {"value": "grid_load", "label": "Obciążenie sieci"},
    {"value": "solar_output", "label": "Moc z paneli słonecznych"},
    {"value": "battery_level", "label": "Poziom baterii"},
]

class AlarmWebhookView(APIView):
    """
    Endpoint: /api/optimization/alarm/

    Kompatybilność z modułem Alarmów:
    - alarms/services.py wysyła GET na /api/optimization/alarm/ z params w URL
      (requests.get(..., params=alert_data))

    Dlatego obsługujemy GET (query params) + zostawiamy POST (body) do testów.
    """
    permission_classes = [AllowAny]  # serwer->serwer, bez logowania/CSRF

    def get(self, request):
        # Alarmy wysyłają dane w query params
        serializer = ExternalAlarmSerializer(data=request.query_params)

        if serializer.is_valid():
            controller = OptimizationController()
            controller.receive_alarm(serializer.validated_data)
            return Response({"status": "received"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        # POST zostawiamy do testów (np. Postman / curl z JSON body)
        serializer = ExternalAlarmSerializer(data=request.data)

        if serializer.is_valid():
            controller = OptimizationController()
            controller.receive_alarm(serializer.validated_data)
            return Response({"status": "received"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeviceListView(APIView):
    permission_classes = [AllowAny]  # serwer->serwer, bez logowania/CSRF
    def get(self, request):
        repo = DeviceRepository()
        devices = repo.get_all_active_devices()
        # devices to lista dictów z MQTT cache, zwracamy je bezpośrednio
        return Response(devices)

class AvailableConditionsView(APIView):
    """Endpoint zwracający dostępne warunki do wyboru w regułach"""
    permission_classes = [AllowAny]
    def get(self, request):
        return Response(AVAILABLE_CONDITIONS)

class AvailableActionsView(APIView):
    """Endpoint zwracający dostępne akcje dla reguł"""
    permission_classes = [AllowAny]
    def get(self, request):
        actions = [
            {"value": "reduce_power", "label": "Zmniejsz moc", "description": "Zmniejszy zużycie urządzenia do 50%"},
            {"value": "shutdown", "label": "Wyłącz", "description": "Całkowicie wyłączy urządzenie"},
            {"value": "shift_time", "label": "Przesuń w czasie", "description": "Opóźni uruchomienie urządzenia"},
            {"value": "increase_power", "label": "Zwiększ moc", "description": "Zwiększy zużycie do maksimum"},
            {"value": "priority_high", "label": "Wysoki priorytet", "description": "Ustawi wysoki priorytet wykonania"},
        ]
        return Response(actions)

class RunOptimizationView(APIView):
    def post(self, request):
        try:
            controller = OptimizationController()
            controller.run_optimization_cycle()

            # Utwórz log sukcesu
            log = OptimizationLog.objects.create(
                status='success',
                action='cycle_run',
                message='Cykl optymalizacji wykonany pomyślnie',
                affected_devices_count=0
            )

            return Response({
                "status": "success",
                "message": "Cykl uruchomiony",
                "log_id": log.id
            }, status=status.HTTP_200_OK)
        except Exception as e:
            # Utwórz log błędu
            log = OptimizationLog.objects.create(
                status='failed',
                action='cycle_run',
                message=f'Błąd podczas uruchomiania cyklu: {str(e)}',
                affected_devices_count=0
            )
            return Response({
                "status": "error",
                "message": str(e),
                "log_id": log.id
            }, status=status.HTTP_400_BAD_REQUEST)

class OptimizationRuleViewSet(viewsets.ModelViewSet):
    queryset = OptimizationRule.objects.all().order_by('-priority')
    serializer_class = OptimizationRuleSerializer

class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer

class OptimizationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OptimizationLog.objects.all().order_by('-timestamp')
    serializer_class = OptimizationLogSerializer