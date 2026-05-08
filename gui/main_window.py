#
# Title: gui/main_window.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Top level window — 800x480 tab shell

from PyQt6.QtWidgets import QMainWindow, QTabWidget
from PyQt6.QtCore import Qt

from comms.serial_handler import SerialHandler
from gui.camera_tab   import CameraTab
from gui.control_tab  import ControlTab
from gui.config_tab import ConfigTab

from config import get_parameter

class MainWindow(QMainWindow):
    def __init__(self, handler: SerialHandler):
        super().__init__()
        self._serial_handler = handler
        
        
        self.setWindowTitle("Powder Drum Control")
        self.setFixedSize(800, 480)

        # Tab widget
        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.setCentralWidget(self._tabs)

        # Instantiate tabs — all share the same serial handler
        self._camera_tab   = CameraTab(self._serial_handler)
        self._control_tab  = ControlTab(self._serial_handler)
        self._config_tab = ConfigTab(self._serial_handler)

        # Attach pyqt Signal to function
        self._config_tab.serial_connection_state.connect(self._on_connection_state_changed)

        self._tabs.addTab(self._camera_tab,   "📷  Camera")
        self._tabs.addTab(self._control_tab,  "⚙️  Control")
        self._tabs.addTab(self._config_tab, "🔧  Config")

    # If serial is connected and app closes, shut down motor
    def closeEvent(self, event):
        if self._serial_handler.is_connected():
            self._serial_handler.set(get_parameter("setpoint").id, 0.0)
            self._serial_handler.stop()
        event.accept()

    def _on_connection_state_changed(self, connected: bool):
        if connected: self._control_tab.on_connected()
        else: self._control_tab.on_disconnected()