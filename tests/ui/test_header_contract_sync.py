from PySide6.QtWidgets import QApplication

from core.test_contract import TestContract
from ui.main_window import MainWindow


def _app():
    return QApplication.instance() or QApplication([])


def test_header_pages_are_loaded_from_test_contract(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _app()
    window = MainWindow()

    header_pages = {
        window.header.page_combo.itemText(index)
        for index in range(window.header.page_combo.count())
    }
    contract_pages = {page.name for page in TestContract.pages}

    assert contract_pages <= header_pages


def test_header_page_selection_syncs_all_test_builders(monkeypatch):
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    _app()
    window = MainWindow()

    target_page = next(page for page in TestContract.pages if page.key == "plt_vehicle_catalog")
    window.header.page_combo.setCurrentText(target_page.name)

    label_builder = window.builder_pages["label"]
    table_builder = window.builder_pages["table"]

    assert label_builder.url_input.text() == target_page.url
    assert target_page.name in label_builder.context_label.text()
    assert label_builder.element_combo.count() > 0
    assert table_builder.url_input.text() == target_page.url
    assert target_page.name in table_builder.context_label.text()
    assert table_builder.element_combo.count() > 0
    assert "Dashboard" not in label_builder.element_combo.itemText(0)
