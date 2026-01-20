from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .data_manager import DataManager
from .enums import Measurement, ReportType
from .reporting import Reporting
from analysis.models import StatisticElement, FileType


class Controller:
    def __init__(self, reporting: Reporting, dataManager: DataManager):
        self.reporting = reporting
        self.dataManager = dataManager

    def createPlot(self, roomId: str, periodStart: datetime, periodEnd: datetime, metric: List[Measurement]) -> bytes:
        df = self.reporting.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.reporting.createPng(df)

    def createReport(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
        createdBy=None,
    ) -> bytes:
        # Zakładamy (jak w Twoim froncie): jedna metryka
        if len(metric) != 1:
            raise ValueError("createReport: na razie obsługuję zapis archiwum tylko dla jednej metryki.")

        df = self.reporting.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        pdf_bytes = self.reporting.createPdf(df)

        report_type = ReportType(df.iloc[0]["period"]) if not df.empty else ReportType.DAILY
        metric_value = metric[0].value  # jedna metryka

        report = StatisticElement(
            periodStart=periodStart,
            periodEnd=periodEnd,
            createdBy=createdBy,
            reportType=report_type.value,   # <-- string do DB
            roomId=roomId,
            metric=metric_value,            # <-- string do DB
            fileType=FileType.PDF,
            fileContent=pdf_bytes,
        )
        self.dataManager.saveArchivedReport(report)

        return pdf_bytes

    def getArchivedReportsList(
        self,
        roomId: Optional[str],
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
        reportType: ReportType,
    ):
        return self.dataManager.getArchivedReportsList(
            reportType=reportType,
            from_dt=periodStart,
            to_dt=periodEnd,
            roomId=roomId,
            metric=metric,
        )

    def getArchivedReport(self, report_id: UUID) -> bytes:
        report = self.dataManager.getArchivedReport(report_id)
        return bytes(report.fileContent)