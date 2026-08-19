"""Export grouped Test Suite reports to Excel, HTML and PDF."""

from __future__ import annotations

from html import escape
from pathlib import Path


def _duration(value: int) -> str:
    return f"{max(0, int(value or 0)) / 1000:.1f}s"


def build_report_html(run: dict, results: list[dict], module_summary: list[dict]) -> str:
    summary_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row.get('module', '')))}</td>"
        f"<td>{row.get('total', 0)}</td><td class='pass'>{row.get('passed', 0)}</td>"
        f"<td class='fail'>{row.get('failed', 0)}</td><td class='error'>{row.get('error', 0)}</td>"
        f"<td class='skip'>{row.get('skipped', 0)}</td><td>{_duration(row.get('duration_ms', 0))}</td>"
        "</tr>"
        for row in module_summary
    )
    result_rows = "".join(
        "<tr>"
        f"<td>{escape(str(row.get('case_id', '')))}</td>"
        f"<td>{escape(str(row.get('module', '')))}</td>"
        f"<td>{escape(str(row.get('title', '')))}</td>"
        f"<td class='{str(row.get('status', '')).lower()}'>{escape(str(row.get('status', '')))}</td>"
        f"<td>{escape(str(row.get('expected', '')))}</td>"
        f"<td>{escape(str(row.get('actual', '')))}</td>"
        f"<td>{escape(str(row.get('message', '')))}</td>"
        f"<td>{_duration(row.get('duration_ms', 0))}</td>"
        "</tr>"
        for row in results
    )
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Test Suite Report</title>
<style>
body{{font-family:'Segoe UI',Arial,sans-serif;color:#102033;margin:32px}}
h1{{color:#0f3d8a}} .meta{{background:#f1f5f9;padding:14px;border-radius:8px}}
.cards{{display:flex;gap:10px;margin:18px 0}} .card{{padding:10px 16px;border-radius:8px;background:#eef2ff}}
table{{width:100%;border-collapse:collapse;margin:12px 0 28px;font-size:12px}}
th,td{{border:1px solid #dbe3ec;padding:7px;text-align:left;vertical-align:top}}
th{{background:#eaf0f8}} .pass,.passed{{color:#087f5b;font-weight:700}}
.fail,.failed,.error{{color:#c92a2a;font-weight:700}} .skip,.skipped{{color:#b26a00;font-weight:700}}
</style></head><body>
<h1>TEST SUITE REPORT</h1>
<div class="meta"><b>Suite:</b> {escape(str(run.get('suite_name', '')))} &nbsp; | &nbsp;
<b>Run ID:</b> {escape(str(run.get('run_id', '')))} &nbsp; | &nbsp;
<b>Chế độ:</b> {escape(str(run.get('run_mode', '')))}<br>
<b>Bắt đầu:</b> {escape(str(run.get('started_at', '')))} &nbsp; | &nbsp;
<b>Kết thúc:</b> {escape(str(run.get('finished_at', '')))} &nbsp; | &nbsp;
<b>Trạng thái:</b> {escape(str(run.get('status', '')))}</div>
<div class="cards"><div class="card">Total: <b>{run.get('total', 0)}</b></div>
<div class="card pass">PASS: {run.get('passed', 0)}</div>
<div class="card fail">FAIL: {run.get('failed', 0)}</div>
<div class="card error">ERROR: {run.get('error', 0)}</div>
<div class="card skip">SKIP: {run.get('skipped', 0)}</div></div>
<h2>Kết quả theo module</h2>
<table><thead><tr><th>Module</th><th>Total</th><th>Pass</th><th>Fail</th><th>Error</th><th>Skip</th><th>Thời gian</th></tr></thead>
<tbody>{summary_rows}</tbody></table>
<h2>Chi tiết Test Case</h2>
<table><thead><tr><th>TC ID</th><th>Module</th><th>Tên case</th><th>Status</th><th>Expected</th><th>Actual</th><th>Message</th><th>Thời gian</th></tr></thead>
<tbody>{result_rows}</tbody></table></body></html>"""


def export_excel(path: str, run: dict, results: list[dict], module_summary: list[dict]):
    import pandas as pd

    summary = [
        {"Thuộc tính": key, "Giá trị": run.get(key, "")}
        for key in (
            "run_id", "suite_name", "run_mode", "status", "total", "passed",
            "failed", "error", "skipped", "started_at", "finished_at", "duration_ms",
        )
    ]
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        pd.DataFrame(summary).to_excel(writer, sheet_name="Test Summary", index=False)
        pd.DataFrame(module_summary).to_excel(writer, sheet_name="Module Summary", index=False)
        columns = [
            "case_id", "module", "title", "status", "expected", "actual", "message",
            "error_message", "screenshot_path", "log_text", "started_at", "finished_at", "duration_ms",
        ]
        pd.DataFrame(results, columns=columns).to_excel(writer, sheet_name="Results", index=False)


def export_html(path: str, run: dict, results: list[dict], module_summary: list[dict]):
    Path(path).write_text(build_report_html(run, results, module_summary), encoding="utf-8")


def export_pdf(path: str, run: dict, results: list[dict], module_summary: list[dict]):
    from PySide6.QtGui import QTextDocument
    from PySide6.QtPrintSupport import QPrinter

    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
    printer.setOutputFileName(path)
    document = QTextDocument()
    document.setHtml(build_report_html(run, results, module_summary))
    document.print_(printer)


def export_report(path: str, run: dict, results: list[dict], module_summary: list[dict]):
    extension = Path(path).suffix.lower()
    if extension == ".xlsx":
        export_excel(path, run, results, module_summary)
    elif extension in {".html", ".htm"}:
        export_html(path, run, results, module_summary)
    elif extension == ".pdf":
        export_pdf(path, run, results, module_summary)
    else:
        raise ValueError("Định dạng báo cáo phải là .xlsx, .html hoặc .pdf")
