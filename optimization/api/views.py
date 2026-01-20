from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from optimization.models import OptimizationRule, UserPreference
from optimization.logic.controller import OptimizationController
from optimization.integration.repositories import DeviceRepository

from .serializers import (
    ExternalAlarmSerializer,     
    DeviceSerializer, 
    OptimizationResultSerializer,
    OptimizationRuleSerializer, 
    UserPreferenceSerializer
)

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
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

class RunOptimizationView(APIView):
    def post(self, request):
        controller = OptimizationController()
        controller.run_optimization_cycle()
        return Response({"status": "success", "message": "Cykl uruchomiony"}, status=status.HTTP_200_OK)

class OptimizationRuleViewSet(viewsets.ModelViewSet):
    queryset = OptimizationRule.objects.all().order_by('-priority')
    serializer_class = OptimizationRuleSerializer

class UserPreferenceViewSet(viewsets.ModelViewSet):
    queryset = UserPreference.objects.all()
    serializer_class = UserPreferenceSerializer