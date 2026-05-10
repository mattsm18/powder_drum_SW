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
    """Top-level shell: fixed 800×480 tab strip + shared serial handler across tabs."""

    _TAB_SPECS: tuple[tuple[str, type], ...] = (
        ("📷  Camera", CameraTab),
        ("⚙️  Control", ControlTab),
        ("🔧  Config", ConfigTab),
    )

    def __init__(self, handler: SerialHandler):
        super().__init__()
        self._serial_handler = handler

        self.setWindowTitle("Powder Drum Control")
        self.setFixedSize(800, 480)

        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.setCentralWidget(self._tabs)

        for title, tab_cls in self._TAB_SPECS:
            self._tabs.addTab(tab_cls(self._serial_handler), title)

        self._camera_tab = self._tabs.widget(0)
        self._control_tab = self._tabs.widget(1)
        self._config_tab = self._tabs.widget(2)

        self._config_tab.serial_connection_state.connect(self._on_connection_state_changed)

    # If serial is connected and app closes, shut down motor
    def closeEvent(self, event):
        if self._serial_handler.is_connected():
            self._serial_handler.set(get_parameter("setpoint").id, 0.0)
            self._serial_handler.stop()
        event.accept()

    def _on_connection_state_changed(self, connected: bool):
        if connected: self._control_tab.on_connected()
        else: self._control_tab.on_disconnected()