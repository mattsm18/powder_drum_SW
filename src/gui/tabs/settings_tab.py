#
# Title: gui/tabs/settings_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Settings tab -> modifies config.json to drive all settings

# Qt UI imports
from PyQt6.QtWidgets import (
    QScrollArea, QFrame, QSizePolicy, QWidget, 
    QHBoxLayout, QListWidgetItem, QListWidget, 
    QStackedWidget, QVBoxLayout, QGroupBox
)

from PyQt6.QtCore import Qt, pyqtSignal

# Styling Imports
from gui.theme import *
from gui.widgets.preview_widget import PreviewWidget
from gui.widgets.setting_row import BoolSettingRow, SliderSettingRow, NumericSettingRow, TupleSettingRow
from models.camera_model import CameraSetting, CameraSettings

class SettingsTab(QWidget):

    serial_connection_state = pyqtSignal(bool)
    camera_setting_changed  = pyqtSignal(CameraSetting, object)
    
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
            ("Connection", self._build_connection_page()),
            ("Camera", self._build_camera_page()),
            ("Vision", self._build_vision_page()),
            ("Motor", self._build_motor_page()),
            ("System Info", self._build_system_page()),
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
    # Connection Setting
    # ──────────────────────────────────────────────────────

    def _build_connection_page(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # Camera Settings
    # ──────────────────────────────────────────────────────
    def _build_camera_page(self) -> QWidget:
        # Outer scroll area the page page itself, added to the QStackedWidget
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Inner content widget this is what scrolls
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        defaults = CameraSettings()  # source of initial display values

        # ── Preview ──

        self._camera_preview = PreviewWidget()
        self._camera_preview.setMinimumHeight(240)
        self._camera_preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self._camera_preview)

        # ── Exposure ──
        exposure_group = QGroupBox("Exposure")
        exposure_layout = QVBoxLayout(exposure_group)

        auto_exposure_row = BoolSettingRow(CameraSetting.AUTO_EXPOSURE, "Auto Exposure", defaults.auto_exposure)
        exposure_time_row = SliderSettingRow(CameraSetting.EXPOSURE_TIME, "Exposure Time (µs)", defaults.exposure_time_us, min_val=100, max_val=100000, is_int=True)
        analogue_gain_row = SliderSettingRow(CameraSetting.ANALOGUE_GAIN, "Analogue Gain", defaults.analogue_gain, min_val=1.0, max_val=16.0, scale=100)

        for row in (auto_exposure_row, exposure_time_row, analogue_gain_row):
            exposure_layout.addWidget(row)
            row.value_changed.connect(self.camera_setting_changed)

        layout.addWidget(exposure_group)

        # ── White Balance ──
        wb_group = QGroupBox("White Balance")
        wb_layout = QVBoxLayout(wb_group)

        auto_wb_row = BoolSettingRow(CameraSetting.AUTO_WHITE_BALANCE, "Auto White Balance", defaults.auto_white_balance)
        wb_layout.addWidget(auto_wb_row)
        auto_wb_row.value_changed.connect(self.camera_setting_changed)

        layout.addWidget(wb_group)

        # ── Resolution / FPS ──
        capture_group = QGroupBox("Resolution / FPS")
        capture_layout = QVBoxLayout(capture_group)

        resolution_row = TupleSettingRow(CameraSetting.RESOLUTION, "Resolution (W/H)", defaults.resolution, min_val=64, max_val=4096, is_int=True)
        fps_row = NumericSettingRow(CameraSetting.FPS, "FPS", defaults.fps, min_val=1, max_val=120, is_int=True)

        for row in (resolution_row, fps_row):
            capture_layout.addWidget(row)
            row.value_changed.connect(self.camera_setting_changed)

        layout.addWidget(capture_group)

        layout.addStretch()

        scroll.setWidget(content)
        return scroll

    def set_preview(self, frame):
        self._camera_preview.set_frame(frame)

    # ──────────────────────────────────────────────────────
    # Vision Controls
    # ──────────────────────────────────────────────────────

    def _build_vision_page(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # Motor Controls
    # ──────────────────────────────────────────────────────

    def _build_motor_page(self) -> QWidget:
        widget = QWidget()
        return widget

    # ──────────────────────────────────────────────────────
    # System Info 
    # ──────────────────────────────────────────────────────

    def _build_system_page(self) -> QWidget:
        widget = QWidget()
        return widget
