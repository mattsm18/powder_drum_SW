#
# Title: main.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Entry point — initialise serial handler and launch GUI

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from comms.serial_handler import SerialHandler
from gui.main_window      import MainWindow
from gui.theme            import DARK_THEME

PORT = 'COM5'
BAUD = 115200

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(DARK_THEME)

    # Single shared serial handler — passed to all tabs
    serial_handler = SerialHandler(port=PORT, baud=BAUD)
    serial_handler.start()

    window = MainWindow(serial_handler)
    window.show()

    sys.exit(app.exec())