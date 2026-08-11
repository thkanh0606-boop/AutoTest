import csv
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class Card(QFrame):
    def __init__(self, title=None, subtitle=None, parent=None):
        super().__init__(parent)
        self.setObjectName("LinhCard")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(16, 14, 16, 14)
        self.layout.setSpacing(9)

        if title:
            label = QLabel(title)
            label.setObjectName("SectionTitle")
            self.layout.addWidget(label)
        if subtitle:
            sub = QLabel(subtitle)
            sub.setObjectName("Muted")
            sub.setWordWrap(True)
            self.layout.addWidget(sub)


class ResultTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(0, 4, parent)
        self.setHorizontalHeaderLabels(["STT", "Expected", "Actual", "Kết quả"])
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)

    def set_results(self, rows):
        self.setRowCount(0)
        for index, row in enumerate(rows, 1):
            self.insertRow(self.rowCount())
            values = [index, row.get("expected", ""), row.get("actual", ""), row.get("result", "")]
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                if col == 3:
                    item.setForeground(QColor("#047857" if value == "PASS" else "#b91c1c"))
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)
                self.setItem(self.rowCount() - 1, col, item)

    def export_csv(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["STT", "Expected", "Actual", "Kết quả"])
            for row in range(self.rowCount()):
                writer.writerow([
                    self.item(row, col).text() if self.item(row, col) else ""
                    for col in range(4)
                ])


class Toast(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(13, 9, 13, 9)
        self.label = QLabel()
        self.layout.addWidget(self.label)
        self.hide()

    def show_message(self, text, status="PASS", duration=2800):
        palette = {
            "PASS": ("#ecfdf5", "#047857", "#a7f3d0"),
            "FAIL": ("#fff1f2", "#be123c", "#fecdd3"),
            "ERROR": ("#fffbeb", "#b45309", "#fde68a"),
            "INFO": ("#eff6ff", "#1d4ed8", "#bfdbfe"),
        }
        bg, fg, border = palette.get(status, palette["INFO"])
        self.setStyleSheet(f"""
            QFrame {{ background: {bg}; border: 1px solid {border}; border-radius: 9px; }}
            QLabel {{ color: {fg}; font-weight: 700; }}
        """)
        self.label.setText(text)
        self.adjustSize()
        if self.parentWidget():
            parent = self.parentWidget()
            self.move(max(12, parent.width() - self.width() - 24), max(12, parent.height() - self.height() - 24))
        self.show()
        self.raise_()
        QTimer.singleShot(duration, self.hide)
