#
# Title: gui/main_window.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Top level window — 800x480 tab shell

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt

from gui.camera_tab   import CameraTab
from gui.control_tab  import ControlTab
from gui.config_tab import ConfigTab


class MainWindow(QMainWindow):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler

        self.setWindowTitle("Powder Drum Control")
        self.setFixedSize(800, 480)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.setCentralWidget(self._tabs)

        # Instantiate tabs — all share the same handler
        self._camera_tab   = CameraTab(handler)
        self._control_tab  = ControlTab(handler)
        self._config_tab = ConfigTab(handler)

        self._tabs.addTab(self._camera_tab,   "📷  Camera")
        self._tabs.addTab(self._control_tab,  "⚙️  Control")
        self._tabs.addTab(self._config_tab, "🔧  Config")

    def closeEvent(self, event):
        # Zero motor and stop handler cleanly on close
        self._handler.set(0x01, 0.0)
        self._handler.stop()
        event.accept()