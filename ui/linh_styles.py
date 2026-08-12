LINH_PAGE_STYLE = """
QWidget#LinhPage {
    background-color: #f8fafc;
    color: #0f172a;
}
QWidget#LinhPage QLabel {
    background: transparent;
}
QLabel#LinhTitle {
    color: #0f172a;
    font-size: 27px;
    font-weight: 750;
}
QLabel#LinhSubtitle, QLabel#Muted {
    color: #64748b;
    font-size: 13px;
}
QLabel#SectionTitle {
    color: #0f172a;
    font-size: 16px;
    font-weight: 700;
}
QLabel#SmallLabel {
    color: #475569;
    font-size: 11px;
    font-weight: 650;
}
QLabel#StatusPass {
    color: #047857;
    font-weight: 700;
}
QLabel#StatusFail {
    color: #b91c1c;
    font-weight: 700;
}
QLabel#StatusError {
    color: #b45309;
    font-weight: 700;
}
QFrame#LinhCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 11px;
}
QFrame#StepCard {
    background: #ffffff;
    border: 1px solid #dfe7f0;
    border-radius: 10px;
}
QLineEdit, QComboBox, QPlainTextEdit, QSpinBox {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 7px 10px;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}
QLineEdit, QComboBox, QSpinBox {
    min-height: 22px;
}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {
    border: 1px solid #3b82f6;
}
QLineEdit[readOnly="true"] {
    color: #475569;
    background: #f8fafc;
}
QComboBox {
    padding-right: 30px;
}
QComboBox::drop-down {
    width: 28px;
    border-left: 1px solid #e2e8f0;
}
QComboBox QAbstractItemView {
    background: #ffffff;
    color: #0f172a;
    border: 1px solid #cbd5e1;
    selection-background-color: #dbeafe;
    selection-color: #0f172a;
    outline: 0;
}
QComboBox QAbstractItemView::item {
    min-height: 30px;
    padding: 4px 8px;
}
QPushButton#PrimaryButton {
    background: #2563eb;
    color: #ffffff;
    border: 1px solid #2563eb;
    border-radius: 7px;
    padding: 8px 14px;
    font-weight: 700;
}
QPushButton#PrimaryButton:hover { background: #1d4ed8; }
QPushButton#PrimaryButton:disabled { background: #94a3b8; border-color: #94a3b8; }
QPushButton#SecondaryButton {
    background: #ffffff;
    color: #334155;
    border: 1px solid #cbd5e1;
    border-radius: 7px;
    padding: 8px 13px;
    font-weight: 650;
}
QPushButton#SecondaryButton:hover { background: #f1f5f9; }
QPushButton#DangerButton {
    background: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
    border-radius: 7px;
    padding: 7px 11px;
    font-weight: 650;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    color: #0f172a;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    gridline-color: #e2e8f0;
    selection-background-color: #dbeafe;
    selection-color: #0f172a;
}
QHeaderView::section {
    background: #f1f5f9;
    color: #334155;
    border: 0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px;
    font-weight: 700;
}
QProgressBar {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    text-align: center;
    min-height: 10px;
}
QProgressBar::chunk { background: #3b82f6; border-radius: 5px; }
QScrollArea#LinhScroll {
    border: none;
    background: transparent;
}
QScrollArea#LinhScroll > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: #f1f5f9;
    width: 10px;
}
QScrollBar::handle:vertical {
    background: #cbd5e1;
    min-height: 28px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QCheckBox { color: #475569; spacing: 7px; }
QToolTip {
    background: #0f172a;
    color: white;
    border: 0;
    padding: 6px;
}
"""
