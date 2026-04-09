"""
Serialize analytics dashboard payloads for CSV and Excel download.
"""

from __future__ import annotations

import csv
from io import BytesIO, StringIO

from openpyxl import Workbook


def render_dashboard_export_csv(dashboard_payload: dict) -> str:
    """Same layout as the legacy single-sheet CSV export."""
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(["Metric", "Value"])
    for key, value in dashboard_payload["metrics"].items():
        writer.writerow([key, value])

    writer.writerow([])
    writer.writerow(["Application Status", "Count"])
    for key, value in dashboard_payload["application_status"].items():
        writer.writerow([key, value])

    writer.writerow([])
    writer.writerow(
        ["Program", "Applications", "Approval Rate", "Avg Processing Time", "Popularity Score"]
    )
    for program in dashboard_payload["program_performance"]:
        writer.writerow(
            [
                program["name"],
                program["applications"],
                program["approval_rate"],
                program["avg_processing_time"],
                program["popularity_score"],
            ]
        )

    return output.getvalue()


def render_dashboard_export_xlsx(dashboard_payload: dict) -> bytes:
    """Multi-sheet workbook mirroring the CSV sections."""
    wb = Workbook()

    ws_m = wb.active
    ws_m.title = "Metrics"
    ws_m.append(["Metric", "Value"])
    for key, value in dashboard_payload["metrics"].items():
        ws_m.append([key, value])

    ws_s = wb.create_sheet("Application status")
    ws_s.append(["Application Status", "Count"])
    for key, value in dashboard_payload["application_status"].items():
        ws_s.append([key, value])

    ws_p = wb.create_sheet("Program performance")
    ws_p.append(
        ["Program", "Applications", "Approval Rate", "Avg Processing Time", "Popularity Score"]
    )
    for program in dashboard_payload["program_performance"]:
        ws_p.append(
            [
                program["name"],
                program["applications"],
                program["approval_rate"],
                program["avg_processing_time"],
                program["popularity_score"],
            ]
        )

    bio = BytesIO()
    wb.save(bio)
    return bio.getvalue()
