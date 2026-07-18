#
# Title: gui/main_window.py
# Author: Matthew Smith 22173112
# Date: 18/07/26
# Purpose: Top level window — 800x480 tab shell

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from src.gui.tabs.camera_tab     import CameraTab
from src.gui.tabs.motor_tab      import MotorTab
from src.gui.tabs.settings_tab   import SettingsTab

class MainWindow(QMainWindow):

    _TAB_SPECS: tuple[tuple[str, type], ...] = (
        ("Camera", CameraTab),
        ("Motor", MotorTab),
        ("Settings", SettingsTab),
    )

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Powder Drum Control")
        self.setFixedSize(800, 480)

        self._tabs = QTabWidget()
        self._tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.setCentralWidget(self._tabs)

        for title, tab_cls in self._TAB_SPECS:
            self._tabs.addTab(tab_cls(), title)

        self._camera_tab = self._tabs.widget(0)
        self._motor_tab = self._tabs.widget(1)
        self._settings_tab = self._tabs.widget(2)