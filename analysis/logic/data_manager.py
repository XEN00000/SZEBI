from datetime import datetime
from typing import List, Optional
from uuid import UUID

import pandas as pd
from acquisition.models import Measurement as AcqMeasurement

from .aggregate import Aggregate
from .enums import Measurement, MeasurementUnit, ReportType
from analysis.models import StatisticElement


class DataManager:
    def aggregateRoomData(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
    ) -> List[Aggregate]:
        period = self._detectPeriod(periodStart, periodEnd)

        result: List[Aggregate] = []
        for one_metric in metric:
            df, unit = self._loadMeasurements(roomId, periodStart, periodEnd, one_metric)
            result.append(
                Aggregate(
                    roomId=roomId,
                    metric=one_metric,
                    unit=unit,
                    periodStart=periodStart,
                    periodEnd=periodEnd,
                    period=period,
                    mean=None,
                    min=None,
                    max=None,
                    data=df,
                )
            )
        return result

    def getArchivedReportsList(
        self,
        reportType: ReportType,
        from_dt: datetime,
        to_dt: datetime,
        roomId: Optional[str] = None,
        metric: Optional[List[Measurement]] = None,
    ) -> List[StatisticElement]:
        qs = StatisticElement.objects.filter(
            reportType=reportType.value,  # zapisujemy string w DB
            periodStart__gte=from_dt,
            periodEnd__lte=to_dt,
        ).order_by("-createdAt")

        if roomId is not None:
            qs = qs.filter(roomId=roomId)

        if metric:
            qs = qs.filter(metric__in=[m.value for m in metric])

        return list(qs)

    def saveArchivedReport(self, report: StatisticElement) -> StatisticElement:
        report.save()
        return report

    def getArchivedReport(self, report_id: UUID) -> StatisticElement:
        return StatisticElement.objects.get(id=report_id)

    def _loadMeasurements(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: Measurement,
    ) -> tuple[pd.DataFrame, MeasurementUnit]:
        qs = (
            AcqMeasurement.objects.filter(
                sensor__location__room=roomId,
                sensor__type__name__iexact=metric.value,
                timestamp__gte=periodStart,
                timestamp__lte=periodEnd,
            )
            .order_by("timestamp")
            .values("timestamp", "value", "sensor__type__default_unit")
        )

        rows = list(qs)
        if not rows:
            return pd.DataFrame(columns=["timestamp", "value"]), MeasurementUnit.NONE

        df = pd.DataFrame(rows).rename(columns={"sensor__type__default_unit": "unit"})

        unit_raw = str(df["unit"].iloc[0]) if "unit" in df.columns else "none"
        unit = MeasurementUnit(unit_raw) if unit_raw in MeasurementUnit.values else MeasurementUnit.NONE

        df = df[["timestamp", "value"]]
        return df, unit

    def _detectPeriod(self, periodStart: datetime, periodEnd: datetime) -> ReportType:
        delta_days = (periodEnd - periodStart).days
        if delta_days <= 1:
            return ReportType.DAILY
        if delta_days <= 7:
            return ReportType.WEEKLY
        if delta_days <= 31:
            return ReportType.MONTHLY
        if delta_days <= 90:
            return ReportType.SEASONAL
        if delta_days <= 183:
            return ReportType.SEMIANNUAL
        return ReportType.ANNUAL