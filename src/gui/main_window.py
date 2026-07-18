#
# Title: gui/main_window.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Top level window — 800x480 tab shell

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from gui.tabs.camera_tab     import CameraTab
from gui.tabs.control_tab    import ControlTab
from gui.tabs.settings_tab   import SettingsTab

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powder Drum Control")
        self.setFixedSize(800, 480)

        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.setCentralWidget(self._tabs)

        self.camera_tab = CameraTab()
        self.motor_tab = ControlTab()
        self.settings_tab = SettingsTab()

        self._tabs.addTab(self.camera_tab, "Camera")
        self._tabs.addTab(self.motor_tab, "Control")
        self._tabs.addTab(self.settings_tab, "Settings")
