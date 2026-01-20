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
        pdf = canvas.Canvas(buffer, pagesize=(595, 842))
        y = 800
        line_height = 18
        bottom_margin = 50

        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, y, "SZEBI - Analysis Report")
        y -= 30

        if statistics.empty:
            pdf.setFont("Helvetica", 12)
            pdf.drawString(50, y, "No data available.")
            pdf.save()
            buffer.seek(0)
            return buffer.read()

        for _, row in statistics.iterrows():
            pdf.setFont("Helvetica-Bold", 12)
            pdf.drawString(
                50,
                y,
                f"Room: {row['room_id']} | Metric: {row['metric']} | Unit: ({row['unit']})"
            )
            y -= line_height

            pdf.setFont("Helvetica", 11)
            pdf.drawString(
                60,
                y,
                f"Mean: {row['mean']} | Min: {row['min']} | Max: {row['max']}"
            )
            y -= line_height


            data_df = row["data"]
            if hasattr(data_df, "empty") and not data_df.empty:
                if y < bottom_margin:
                    pdf.showPage()
                    y = 800
                pdf.setFont("Helvetica-Bold", 10)
                pdf.drawString(60, y, "Measurements:")
                y -= line_height

                for _, r in data_df.iterrows():
                    if y < bottom_margin:
                        pdf.showPage()
                        y = 800
                    pdf.setFont("Helvetica", 10)
                    pdf.drawString(70, y, f"- {r['timestamp']}: ")
                    timestamp_width = pdf.stringWidth(f"- {r['timestamp']}: ", "Helvetica", 10)
                    pdf.setFont("Helvetica-Bold", 10)
                    pdf.drawString(70 + timestamp_width, y, str(r['value']))
                    y -= 14

            y -= 10

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