from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status

from .models import Forecast
from .serializers import ForecastSerializer

from .services import ForecastingService


class TrainModelView(APIView):
    """
    POST /api/forecasting/train/
    """

    def post(self, request):
        service = ForecastingService()

        result = service.train_models()

        if result == "SUCCESS":
            return Response(
                {"status": "Sukces", "message": "Modele (Zużycie i Produkcja) zostały wytrenowane."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"error": f"Błąd treningu: {result}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GenerateForecastView(APIView):
    """
    GET /api/forecasting/predict/
    """

    def get(self, request):
        service = ForecastingService()

        forecast_data = service.generate_new_forecast()

        if forecast_data:
            return Response({
                "status": "Prognoza wygenerowana",
                "data": forecast_data
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Nie udało się wygenerować prognozy. Sprawdź, czy modele są wytrenowane."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/forecasting/history/
    """
    queryset = Forecast.objects.all().order_by('-created_at')
    serializer_class = ForecastSerializer