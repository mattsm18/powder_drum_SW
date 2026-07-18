#
# Title: main.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Entry point — initialise serial handler and launch GUI

import os
import sys
sys.dont_write_bytecode = True

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.gui.main_window import MainWindow
from src.gui.theme import DARK_THEME


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_THEME)

    window = MainWindow()

    # Linux Kiosk Target
    window.showFullScreen()
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)
    window.show()

    sys.exit(app.exec())