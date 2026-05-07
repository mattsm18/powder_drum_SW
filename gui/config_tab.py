#
# Title: gui/config_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Settings tab — Kp, Ki, accel rate, CV params, stream config, serial port connect etc.

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class ConfigTab(QWidget):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("🔧 Config Tab — Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)