#
# Title: gui/control_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: I/O Control tab — motor speed, live graph, lights
#

from PyQt6.QtWidgets import *

class ControlTab(QWidget):

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        pass