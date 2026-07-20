#
# Title: gui/control_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Captures tab - lists internal recordings and stills allows user to replay videos, view images and copy to USB drive
#

from PyQt6.QtWidgets import *

class StorageTab(QWidget):

    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        pass