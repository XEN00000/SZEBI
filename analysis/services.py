from django.db import models
from uuid import uuid4
import io
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from .mock_db import *

class DataManager(object):
    def __init__(self):
        pass

    def aggregateRoomData(self, roomId, periodStart, periodEnd, metric):

        def get_measurements(roomId, periodStart, periodEnd, metric):
            return measurement_filter(
                timestamp_range=(periodStart, periodEnd),
                room=roomId,
                metric=metric
            )

        def get_period(periodStart, periodEnd):

            delta = periodEnd - periodStart

            if delta.days <= 1:
                return ReportType.DAILY
            elif delta.days <= 7:
                return ReportType.WEEKLY
            elif delta.days <= 31:
                return ReportType.MONTHLY
            elif delta.days <= 90:
                return ReportType.SEASONAL
            elif delta.days <= 183:
                return ReportType.SEMIANNUAL
            else:
                return ReportType.ANNUAL

        data = []
        unit = None

        measurements = get_measurements(roomId, periodStart, periodEnd, metric)

        for m in measurements:
            data.append(m["value"])
            unit = mock_sensor_types[mock_sensors[m["sensor_id"]]["type_id"]]["default_unit"]

        aggregated_data = Aggregate(roomId=roomId, metric=metric, unit=MeasurementUnit(unit),
                                    periodStart=periodStart, periodEnd=periodEnd,
                                    period=get_period(periodStart, periodEnd), mean=None, max=None,
                                    min=None, data=data)

        return aggregated_data

    def getArchivedReports(self, reportType, periodStart, periodEnd):
        return None

    def saveArchivedReport(self, report):
        return None

    def getArchivedReport(self, id):
        return None


class Statistics(object):
    def __init__(self, dataManager):
        self.dataManager = dataManager

    def calculateStatistics(self, roomId, periodStart, periodEnd, metric):
        element = self.dataManager.aggregateRoomData(roomId, periodStart,
                                                     periodEnd, metric)

        element.mean = sum(element.data) / len(element.data)
        element.min = min(element.data)
        element.max = max(element.data)

        df = pd.DataFrame({
            "room_id": element.roomId,
            "metric": element.metric,
            "unit": element.unit,
            "period_start": element.periodStart.isoformat(),
            "period_end": element.periodEnd.isoformat(),
            "period": element.period,
            "mean": element.mean,
            "min": element.min,
            "max": element.max,
            "data": [element.data]
        })

        return df


class Aggregate(object):
    def __init__(self, roomId, metric, unit, periodStart, periodEnd, period, mean, min, max, data):
        self.roomId = roomId
        self.metric = metric
        self.unit = unit
        self.periodStart = periodStart
        self.periodEnd = periodEnd
        self.period = period
        self.mean = mean
        self.min = min
        self.max = max
        self.data = data


class MeasurementUnit(models.TextChoices):
    CELSIUS = 'celsius'
    FAHRENHEIT = 'fahrenheit'
    KILOWATT_HOUR = 'kilowatt-hour'
    WATT = 'watt'
    PERCENT = 'percent'
    NONE = 'none'


class Measurement(models.TextChoices):
    TEMPERATURE = 'temperature'
    HUMIDITY = 'humidity'
    ENERGY = 'energy'
    POWER = 'power'
    VOLTAGE = 'voltage'


class ReportType(models.TextChoices):
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    SEASONAL = 'seasonal'
    SEMIANNUAL = 'semiannual'
    ANNUAL = 'annual'

class StatisticElement:
    def __init__(self, periodStart, periodEnd, createdBy, reportType, fileContent):
        self.id = uuid4()
        self.periodStart = periodStart
        self.periodEnd = periodEnd
        self.createdAt = None
        self.createdBy = createdBy
        self.reportType = reportType
        self.fileContent = fileContent


class Reporting:
    def __init__(self, statistics: Statistics):
        self.statistics = statistics

    def buildFileName(self, roomId, periodStart, periodEnd, metric):
        return f"report_{roomId}_{metric}_{periodStart.date()}_{periodEnd.date()}"

    def generateOnDemand(self, roomId, periodStart, periodEnd, metric):
        df = self.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.createPdf(df)

    def generateAutomatically(self, roomId, periodStart, periodEnd, metric):
        df = self.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.createPdf(df)

    def createPdf(self, stats_df: pd.DataFrame):
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        y = 800

        if not stats_df.empty:
            values = stats_df.iloc[0]["data"]
            unit = stats_df.iloc[0]["unit"]
            for v in values:
                pdf.drawString(50, y, f"{v} {unit}")
                y -= 20

        pdf.save()
        buffer.seek(0)
        return buffer.read()

    def createPng(self, stats_df: pd.DataFrame):
        buffer = io.BytesIO()

        if not stats_df.empty:
            values = stats_df.iloc[0]["data"]
            plt.plot(values)
            plt.savefig(buffer, format="png")

        buffer.seek(0)
        return buffer.read()


class Controller:
    def __init__(self, reporting: Reporting, dataManager: DataManager):
        self.reporting = reporting
        self.dataManager = dataManager

    def createPlot(self, roomId, periodStart, periodEnd, metric):
        df = self.reporting.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.reporting.createPng(df)

    def createReport(self, roomId, periodStart, periodEnd, metric):
        df = self.reporting.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        pdf_bytes = self.reporting.createPdf(df)

        report = StatisticElement(
            periodStart=periodStart,
            periodEnd=periodEnd,
            createdBy=uuid4(),
            reportType=df.iloc[0]["period"] if not df.empty else ReportType.DAILY,
            fileContent=pdf_bytes,
        )
        self.dataManager.saveArchivedReport(report)
        return pdf_bytes

    def getArchivedReportsList(self, reportType, start, end):
        return self.dataManager.getArchivedReports(reportType, start, end)

    def getArchivedReport(self, report_id):
        return self.dataManager.getArchivedReport(report_id)


# DO TESTOWANIA:

#dm = DataManager()
#stat = Statistics(dm)
#
# df = stat.calculateStatistics("101", datetime.fromisoformat('2025-12-01T00:00:00'),
#                               datetime.fromisoformat('2025-12-01T12:00:00'), Measurement.TEMPERATURE)
#
# pd.set_option('display.max_rows', None)
# pd.set_option('display.max_columns', None)
# pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
#
# print(df)
# print()
#
# df = stat.calculateStatistics("101", datetime.fromisoformat('2025-12-01T00:00:00'),
#                               datetime.fromisoformat('2025-12-01T12:00:00'), Measurement.HUMIDITY)
#
# print(df)
