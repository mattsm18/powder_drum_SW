#
# Title: gui/config_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Settings tab -> modifies config.json to drive all settings

# Qt UI imports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import pyqtSignal

# Styling Imports
from gui.theme import *

class SettingsTab(QWidget):

    serial_connection_state = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self._build_ui()

    # ──────────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self) 
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left Navigation Menu
        self._menu_list = QListWidget()
        self._menu_list.setFixedWidth(180)

        # Content Area (Stacked Widget)
        self._content_stack = QStackedWidget()

        # Define our tabs/pages
        pages = [
            ("Connection", self._build_connection_tab()),
            ("Camera", self._build_camera_tab()),
            ("Vision", self._build_vision_tab()),
            ("Motor", self._build_motor_tab()),
        ]

        for name, widget in pages:
            # Add to menu
            item = QListWidgetItem(name)
            self._menu_list.addItem(item)
            # Add to stack
            self._content_stack.addWidget(widget)

        # Handle switching pages
        self._menu_list.currentRowChanged.connect(self._content_stack.setCurrentIndex)
        self._menu_list.setCurrentRow(0) # Default to first page

        # Add components to the root layout
        root.addWidget(self._menu_list)
        root.addWidget(self._content_stack)

    # ──────────────────────────────────────────────────────
    # Connection Tab
    # ──────────────────────────────────────────────────────

    def _build_connection_tab(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # Camera Controls
    # ──────────────────────────────────────────────────────

    def _build_camera_tab(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # Vision Controls
    # ──────────────────────────────────────────────────────

    def _build_vision_tab(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # Motor Controls
    # ──────────────────────────────────────────────────────

    def _build_motor_tab(self) -> QWidget:
        widget = QWidget()
        return widget
