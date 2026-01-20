# analysis/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("test/", views.test_statistics),
    path("statistics/", views.statistics_view),

    path("report/", views.report_pdf_view),
    path("report/save/", views.report_pdf_save_view),

    path("plot/", views.plot_png_view),
    path("plot/save/", views.plot_png_save_view),

    path("archive/list/", views.archived_reports_list_view),
    path("archive/<str:report_id>/", views.archived_report_download_view),
]