from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ForecastViewSet, TrainModelView, GenerateForecastView

router = DefaultRouter()
router.register(r'history', ForecastViewSet, basename='forecast-history')

urlpatterns = [
    path('train/', TrainModelView.as_view(), name='train-model'),
    path('predict/', GenerateForecastView.as_view(), name='generate-forecast'),
    path('', include(router.urls)),
]