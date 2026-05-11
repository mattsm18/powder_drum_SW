#
# Title: main.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Entry point — initialise serial handler and launch GUI

import sys
sys.dont_write_bytecode = True
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from comms.serial_handler import SerialHandler
from gui.main_window      import MainWindow
from theme import DARK_THEME


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_THEME)

    # Single shared serial handler — passed to all tabs
    serial_handler = SerialHandler()
    window = MainWindow(serial_handler)

    # Linux Kiosk Target
    window.showFullScreen()
    app.setOverrideCursor(Qt.CursorShape.BlankCursor)
    window.show()

    sys.exit(app.exec())