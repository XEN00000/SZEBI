from django.http import JsonResponse, HttpResponse
from datetime import datetime
from .services import DataManager, Statistics, Measurement, Reporting, Controller

dm = DataManager()
stats = Statistics(dm)
reporting = Reporting(stats)
controller = Controller(reporting, dm)


# GET /analysis/test/
# http://localhost:8000/analysis/test/
def test_statistics(request):
    df = stats.calculateStatistics(
        "101",
        datetime(2025, 12, 1, 8, 0),
        datetime(2025, 12, 1, 10, 0),
        Measurement.TEMPERATURE,
    )
    return JsonResponse(df.to_dict(orient="records"), safe=False)


#GET /analysis/statistics
#  http://localhost:8000/analysis/statistics/
def statistics_view(request):
    room = request.GET.get("room", "101")
    metric = request.GET.get("metric", "temperature")
    start = request.GET.get("start", "2025-12-01 00:00")
    end = request.GET.get("end", "2025-12-01 12:00")

    metric = Measurement(metric)
    start = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M")

    df = stats.calculateStatistics(room, start, end, metric)
    return JsonResponse(df.to_dict(orient="records"), safe=False)

#GET /analysis/report
# http://localhost:8000/analysis/
def report_pdf_view(request):
    room = request.GET.get("room", "101")
    metric = request.GET.get("metric", "temperature")
    start = request.GET.get("start", "2025-12-01 00:00")
    end = request.GET.get("end", "2025-12-01 12:00")

    metric = Measurement(metric)
    start = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M")

    df = stats.calculateStatistics(room, start, end, metric)
    pdf_bytes = reporting.createPdf(df)

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response

#GET /analysis/plot/
# http://localhost:8000/analysis/plot/
def plot_png_view(request):
    room=request.GET.get("room", "101")
    metric = request.GET.get("metric", "temperature")
    start = request.GET.get("start", "2025-12-01 00:00")
    end = request.GET.get("end", "2025-12-01 12:00")

    metric = Measurement(metric)
    start = datetime.strptime(start, "%Y-%m-%d %H:%M")
    end = datetime.strptime(end, "%Y-%m-%d %H:%M")

    df = stats.calculateStatistics(room, start, end, metric)
    png_bytes = reporting.createPng(df)

    response = HttpResponse(png_bytes, content_type="image/png")
    return response

