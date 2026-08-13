import sys

from PySide6.QtWidgets import QApplication

from database.database import init_database
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

# Khởi tạo SQLite database
init_database()

window = MainWindow()
window.show()

