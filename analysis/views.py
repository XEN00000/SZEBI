# analysis/views.py
from datetime import datetime
from uuid import UUID

from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.utils import timezone

from .logic.data_manager import DataManager
from .logic.statistics import Statistics
from .logic.reporting import Reporting
from .logic.controller import Controller
from .logic.enums import Measurement, ReportType
from .models import FileType, StatisticElement

# DataManager -> Statistics -> Reporting -> Controller
dm = DataManager()
stats = Statistics(dm)
reporting = Reporting(stats)
controller = Controller(reporting, dm)


def _parse_dt(value: str) -> datetime:
    if not value:
        raise ValueError("missing datetime")

    value = value.strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M"):
        try:
            dt = datetime.strptime(value, fmt)
            return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
        except ValueError:
            continue

    raise ValueError(f"invalid datetime format: {value}")


def _parse_metric_list(metric_str: str):
    if not metric_str:
        return []
    return [Measurement(metric_str)]


def _has_plot_data(df) -> bool:
    # Sprawdza, czy mamy dane do narysowania wykresu.
    if df is None or df.empty:
        return False

    try:
        data_df = df.iloc[0].get("data")
    except Exception:
        return False

    return data_df is not None and hasattr(data_df, "empty") and not data_df.empty


def test_statistics(request):
    try:
        end = timezone.now()
        start = end - timezone.timedelta(hours=2)
        df = stats.calculateStatistics("101", start, end, [Measurement.TEMPERATURE])
        return JsonResponse(df.to_dict(orient="records"), safe=False)
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def statistics_view(request):
    """
       GET:
       Zwraca statystyki jako JSON (mean/min/max + metadane).
       Jeśli start/end brak -> domyślnie ostatnie 12h.
    """
    try:
        room = request.GET.get("room", "101")
        metric_str = request.GET.get("metric", "temperature")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        metric_list = _parse_metric_list(metric_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(hours=12))
        end = _parse_dt(end_str) if end_str else timezone.now()

        df = stats.calculateStatistics(room, start, end, metric_list)
        return JsonResponse(df.to_dict(orient="records"), safe=False)
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def report_pdf_view(request):
    """
        GET:
        Generuje PDF z raportem i zwraca jako response
    """
    try:
        room = request.GET.get("room", "101")
        metric_str = request.GET.get("metric", "temperature")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        metric_list = _parse_metric_list(metric_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(hours=12))
        end = _parse_dt(end_str) if end_str else timezone.now()

        df = stats.calculateStatistics(room, start, end, metric_list)
        pdf_bytes = reporting.createPdf(df)

        return HttpResponse(pdf_bytes, content_type="application/pdf")
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def report_pdf_save_view(request):
    """
       GET:
       Generuje PDF i zapisuje go w archiwum (StatisticElement) przez Controller.
    """
    try:
        room = request.GET.get("room", "101")
        metric_str = request.GET.get("metric", "temperature")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        metric_list = _parse_metric_list(metric_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(hours=12))
        end = _parse_dt(end_str) if end_str else timezone.now()

        pdf_bytes = controller.createReport(
            room,
            start,
            end,
            metric_list,
            createdBy=request.user if request.user.is_authenticated else None,
        )

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="report_saved.pdf"'
        return response
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def plot_png_view(request):
    """
    GET:
    Generuje wykres PNG
    Jeśli brak danych -> 404.
    """
    try:
        room = request.GET.get("room", "101")
        metric_str = request.GET.get("metric", "temperature")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        metric_list = _parse_metric_list(metric_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(hours=12))
        end = _parse_dt(end_str) if end_str else timezone.now()

        df = stats.calculateStatistics(room, start, end, metric_list)

        if not _has_plot_data(df):
            return HttpResponse("Brak danych do wykresu", status=404)

        png_bytes = reporting.createPng(df)
        return HttpResponse(png_bytes, content_type="image/png")
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def plot_png_save_view(request):
    try:
        room = request.GET.get("room", "101")
        metric_str = request.GET.get("metric", "temperature")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        metric_list = _parse_metric_list(metric_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(hours=12))
        end = _parse_dt(end_str) if end_str else timezone.now()

        df = stats.calculateStatistics(room, start, end, metric_list)

        if not _has_plot_data(df):
            return HttpResponse("Brak danych, nic nie zapisano", status=404)


        png_bytes = reporting.createPng(df)

        report_type = ReportType(df.iloc[0]["period"]) if not df.empty else ReportType.DAILY
        metric_value = metric_list[0].value if metric_list else None

        elem = StatisticElement(
            periodStart=start,
            periodEnd=end,
            createdBy=request.user if request.user.is_authenticated else None,
            reportType=report_type,
            roomId=room,
            metric=metric_value,
            fileType=FileType.PNG,
            fileContent=png_bytes,
        )
        dm.saveArchivedReport(elem)

        response = HttpResponse(png_bytes, content_type="image/png")
        response["Content-Disposition"] = 'attachment; filename="plot_saved.png"'
        return response
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def archived_reports_list_view(request):
    try:
        report_type_str = request.GET.get("reportType", "DAILY")
        start_str = request.GET.get("start", "")
        end_str = request.GET.get("end", "")

        room = request.GET.get("room")  # może być None
        metric_str = request.GET.get("metric")  # może być None

        report_type = ReportType(report_type_str)
        start = _parse_dt(start_str) if start_str else (timezone.now() - timezone.timedelta(days=1))
        end = _parse_dt(end_str) if end_str else timezone.now()
        metric_list = _parse_metric_list(metric_str) if metric_str else None

        reports = controller.getArchivedReportsList(
            roomId=room,
            periodStart=start,
            periodEnd=end,
            metric=metric_list or [],
            reportType=report_type,
        )

        payload = [
            {
                "id": str(r.id),
                "reportType": r.reportType,
                "roomId": r.roomId,
                "metric": r.metric,
                "fileType": r.fileType,
                "periodStart": r.periodStart.isoformat(),
                "periodEnd": r.periodEnd.isoformat(),
                "createdAt": r.createdAt.isoformat(),
            }
            for r in reports
        ]
        return JsonResponse(payload, safe=False)
    except Exception as e:
        return HttpResponseBadRequest(str(e))


def archived_report_download_view(request, report_id: str):
    try:
        rid = UUID(report_id)
        content = controller.getArchivedReport(rid)

        elem = dm.getArchivedReport(rid)
        if elem.fileType == FileType.PNG:
            return HttpResponse(content, content_type="image/png")
        return HttpResponse(content, content_type="application/pdf")
    except Exception as e:
        return HttpResponseBadRequest(str(e))