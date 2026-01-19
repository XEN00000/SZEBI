import io
from datetime import datetime
from typing import List

import matplotlib.pyplot as plt
import pandas as pd
from reportlab.pdfgen import canvas

from .enums import Measurement
from .statistics import Statistics


class Reporting:

    def __init__(self, statistics: Statistics):
        self.statistics = statistics

    def generateOnDemand(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
    ) -> bytes:
        df = self.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.createPdf(df)

    def generateAutomatically(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
    ) -> bytes:
        df = self.statistics.calculateStatistics(roomId, periodStart, periodEnd, metric)
        return self.createPdf(df)

    def buildFileName(
        self,
        roomId: str,
        periodStart: datetime,
        periodEnd: datetime,
        metric: List[Measurement],
    ) -> str:
        metric_name = metric[0].value if metric else "metric"
        return f"report_{roomId}_{metric_name}_{periodStart.date()}_{periodEnd.date()}"

    def createPdf(self, statistics: pd.DataFrame) -> bytes:
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer)
        y = 800

        pdf.drawString(50, y, "SZEBI - Analysis report")
        y -= 30

        if statistics.empty:
            pdf.drawString(50, y, "Brak danych.")
            pdf.save()
            buffer.seek(0)
            return buffer.read()

        for _, row in statistics.iterrows():
            pdf.drawString(
                50,
                y,
                f"Room={row['room_id']} metric={row['metric']} mean={row['mean']} min={row['min']} max={row['max']} ({row['unit']})",
            )
            y -= 18

            data_df = row["data"]
            if hasattr(data_df, "empty") and not data_df.empty:
                for _, r in data_df.tail(5).iterrows():
                    pdf.drawString(70, y, f"- {r['timestamp']}: {r['value']}")
                    y -= 14

            y -= 10
            if y < 120:
                pdf.showPage()
                y = 800

        pdf.save()
        buffer.seek(0)
        return buffer.read()

    def createPng(self, statistics: pd.DataFrame) -> bytes:
        if statistics.empty:
            return b""

        row = statistics.iloc[0]
        data_df = row["data"]
        if data_df is None or data_df.empty:
            return b""

        buffer = io.BytesIO()
        plt.figure()
        plt.plot(data_df["timestamp"], data_df["value"])
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        plt.savefig(buffer, format="png")
        plt.close()
        buffer.seek(0)
        return buffer.read()