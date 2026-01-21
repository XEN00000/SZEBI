from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny

from .models import Forecast
from .serializers import ForecastSerializer
from .services import ForecastingService


class TrainModelView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service = ForecastingService()
        result = service.train_models()
        if result == "SUCCESS":
            return Response(
                {"status": "Sukces", "message": "Modele zostały wytrenowane."},
                status=status.HTTP_200_OK
            )
        return Response({"error": result}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateForecastView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        service = ForecastingService()
        forecast_data = service.generate_new_forecast()
        if forecast_data:
            return Response({
                "status": "Sukces",
                "message": "Nowa prognoza gotowa."
            }, status=status.HTTP_200_OK)
        return Response({"error": "Brak modeli"}, status=status.HTTP_400_BAD_REQUEST)


class LatestForecastView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        service = ForecastingService()
        data = service.get_latest_forecast()

        if data:
            formatted_data = []
            timestamps = data.get('timestamps', [])
            consumption = data.get('consumption', [])
            production = data.get('production', [])

            for i in range(len(timestamps)):
                formatted_data.append({
                    "date": timestamps[i],
                    "consumption": round(consumption[i], 2),
                    "production": round(production[i], 2)
                })
            return Response(formatted_data)

        return Response([], status=200)


class ForecastViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Forecast.objects.all().order_by('-created_at')
    serializer_class = ForecastSerializer