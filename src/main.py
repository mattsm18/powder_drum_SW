#
# Title: main.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Program Entry point

import sys
from PyQt6.QtWidgets import QApplication
from application.app import Application
from gui.theme import DARK_THEME

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    qt_app.setStyle("Fusion")
    qt_app.setStyleSheet(DARK_THEME)

    application = Application()
    application.start()

    sys.exit(qt_app.exec())