#
# Title: gui/widgets/speed_control.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Speed control widget — slider, ±0.5 RPM buttons, numpad entry
#

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.numpad import NumpadDialog
from gui.theme import COLOUR_BLUE

from config import get_parameter, get_ui_config

STOP_THRESHOLD = 0.05

class SpeedControl(QWidget):
    speed_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self._ui_config = get_ui_config()
        self._setpoint = get_parameter("setpoint")

        self._internal_setpoint = 0.0
        self._motor_stopped = False  # state tracking

        self._build_ui()

    # ---------------- UI BUILD ----------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self._value_btn = QPushButton("0.0 rad/s")
        self._value_btn.setFont(QFont("Courier New", 22, QFont.Weight.Bold))
        self._value_btn.setStyleSheet(f"""
            color: {COLOUR_BLUE};
            background-color: #2A2A2A;
            border: 1px solid #444444;
            border-radius: 6px;
            min-height: 30px;
        """)
        
        self._value_btn.clicked.connect(self._open_numpad)
        layout.addWidget(self._value_btn)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)

        self._minus_btn = QPushButton("−")
        self._minus_btn.setFont(QFont("Segoe UI", 16))
        self._minus_btn.setStyleSheet("min-height: 0px; min-width: 0px;")
        self._minus_btn.clicked.connect(self._step_down)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(int(self._setpoint.max * 100))
        self._slider.setValue(0)
        self._slider.valueChanged.connect(self._on_slider_changed)

        self._plus_btn = QPushButton("+")
        self._plus_btn.setFixedSize(56, 56)
        self._plus_btn.setFont(QFont("Segoe UI", 16))
        self._plus_btn.setStyleSheet("min-height: 0px; min-width: 0px;")
        self._plus_btn.clicked.connect(self._step_up)

        control_layout.addWidget(self._minus_btn)
        control_layout.addWidget(self._slider)
        control_layout.addWidget(self._plus_btn)
        layout.addLayout(control_layout)

        range_layout = QHBoxLayout()
        range_layout.addWidget(QLabel(f"{self._setpoint.min:.0f}"))
        range_layout.addStretch()
        range_layout.addWidget(QLabel(f"{self._setpoint.max:.0f} {self._setpoint.unit}"))
        layout.addLayout(range_layout)

        self._stop_motor_btn = QPushButton("STOP")
        self._stop_motor_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._stop_motor_btn.setStyleSheet("background-color: #b53131; color: #FFFFFF;")
        self._stop_motor_btn.clicked.connect(self._on_stop_motor_pressed)
        layout.addWidget(self._stop_motor_btn)

    # ---------------- CORE CONTROL ----------------

    def _set_speed(self, value: float, from_slider: bool = False):
        value = max(self._setpoint.min, min(self._setpoint.max, value))
        self._internal_setpoint = value
        self.set_display_value(value)

        if not from_slider:
            self._slider.blockSignals(True)
            self._slider.setValue(int(value * 100))
            self._slider.blockSignals(False)

        self.speed_changed.emit(value)

    # ---------------- STOP BUTTON (USER INITIATED) ----------------

    def _on_stop_motor_pressed(self):
        self._set_speed(0.0)
        self._motor_stopped = False  # waiting for real confirmation

        self._stop_motor_btn.setText("STOPPING")
        self._stop_motor_btn.setStyleSheet("background-color: #f51d1d; color: #FFFFFF;")
        self._stop_motor_btn.setEnabled(False)

    def _reset_stop_btn(self):
        self._stop_motor_btn.setText("STOP")
        self._stop_motor_btn.setStyleSheet("background-color: #b53131; color: #FFFFFF;")
        self._stop_motor_btn.setEnabled(True)

    # ---------------- EXTERNAL STATE UPDATES ----------------
    
    def set_display_value(self, value: float):
        self._value_btn.setText(f"{value:.1f} {self._setpoint.unit}")

    def is_motor_stopped(self, velocity: float):
        if abs(velocity) < STOP_THRESHOLD: self._reset_stop_btn()

    # ---------------- INPUT HANDLING ----------------

    def _on_slider_changed(self, raw: int): self._set_speed(raw / 100.0, from_slider=True)
    def _step_up(self): self._set_speed(self._internal_setpoint + self._ui_config.get("plus_minus_step"))
    def _step_down(self): self._set_speed(self._internal_setpoint - self._ui_config.get("plus_minus_step"))
    def _open_numpad(self):

        dlg = NumpadDialog(
            self, 
            "Target Motor Speed", 
            self._internal_setpoint, 
            self._setpoint.min, 
            self._setpoint.max
        )

        if dlg.exec() and dlg.get_value() is not None:
            self._set_speed(dlg.get_value())