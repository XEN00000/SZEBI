from django.urls import path
from .views import test_statistics, statistics_view, report_pdf_view, plot_png_view


urlpatterns = [
    path("test/", test_statistics),
    path("statistics/", statistics_view),
    path("report/", report_pdf_view),
    path("plot/", plot_png_view)
]