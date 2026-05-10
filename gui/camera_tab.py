#
# Title: gui/camera_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Camera tab — live feed, CV overlay, recording, IP stream

from PyQt6.QtWidgets import QWidget, QVBoxLayout

from gui.widgets.stub_placeholder import build_stub_placeholder


class CameraTab(QWidget):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(build_stub_placeholder("📷 Camera Tab — Coming Soon", self))