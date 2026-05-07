#
# Title: gui/control_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: I/O Control tab — motor speed, live graph, lights

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt


class ControlTab(QWidget):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("⚙️ Control Tab — Coming Soon")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)