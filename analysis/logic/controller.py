from datetime import datetime
from typing import List, Optional
from uuid import UUID

from .data_manager import DataManager
from .enums import Measurement, ReportType
from .reporting import Reporting
from analysis.models import StatisticElement, FileType


class Controller:
    """
    Łączy logikę obliczeń (Statistics/Reporting) z dostępem do danych i archiwum (DataManager).
    """
    def __init__(self, reporting: Reporting, dataManager: DataManager):
        self.reporting = reporting
        self.dataManager = dataManager

    def createPlot(self, roomId: str, periodStart: datetime, periodEnd: datetime, metric: List[Measurement]) -> bytes:
        """
        Tworzy wykres PNG dla podanego pokoju, zakresu czasu i metryki.
        Najpierw liczy statystyki, potem generuje obraz PNG.
        """
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
        #Tworzy raport PDF i zapisuje go w archiwum (tabela StatisticElement)
        if len(metric) != 1:
            raise ValueError("createReport: na razie obsługuję zapis archiwum tylko dla jednej metryki.")

        df = self.reporting.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        pdf_bytes = self.reporting.createPdf(df)

        report_type = ReportType(df.iloc[0]["period"]) if not df.empty else ReportType.DAILY
        metric_value = metric[0].value

        report = StatisticElement(
            periodStart=periodStart,
            periodEnd=periodEnd,
            createdBy=createdBy,
            reportType=report_type.value,
            roomId=roomId,
            metric=metric_value,
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
        #Zwraca listę zapisanych raportów archiwum
        return self.dataManager.getArchivedReportsList(
            reportType=reportType,
            from_dt=periodStart,
            to_dt=periodEnd,
            roomId=roomId,
            metric=metric,
        )

    def getArchivedReport(self, report_id: UUID) -> bytes:
        #Pobiera pojedynczy zapisany plik z archiwum po id
        report = self.dataManager.getArchivedReport(report_id)
        return bytes(report.fileContent)