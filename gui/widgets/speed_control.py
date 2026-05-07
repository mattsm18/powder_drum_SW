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

MIN_RADS  = 0.0
MAX_RADS  = 30.0
STEP_RADS = 0.5
STOP_THRESHOLD = 0.05

class SpeedControl(QWidget):
    speed_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self._motor_rads = 0.0
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
        self._slider.setMaximum(int(MAX_RADS * 100))
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
        range_layout.addWidget(QLabel(f"{MIN_RADS:.0f}"))
        range_layout.addStretch()
        range_layout.addWidget(QLabel(f"{MAX_RADS:.0f} rad/s"))
        layout.addLayout(range_layout)

        self._stop_motor_btn = QPushButton("STOP")
        self._stop_motor_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._stop_motor_btn.setStyleSheet(
            "background-color: #b53131; color: #FFFFFF;"
        )
        self._stop_motor_btn.clicked.connect(self._on_stop_motor_pressed)
        layout.addWidget(self._stop_motor_btn)

    # ---------------- CORE CONTROL ----------------

    def _set_rads(self, rads: float, from_slider: bool = False):
        rads = max(MIN_RADS, min(MAX_RADS, rads))
        self._motor_rads = rads

        self._value_btn.setText(f"{rads:.1f} rad/s")

        if not from_slider:
            self._slider.blockSignals(True)
            self._slider.setValue(int(rads * 100))
            self._slider.blockSignals(False)

        self.speed_changed.emit(rads)

    # ---------------- STOP BUTTON (USER INITIATED) ----------------

    def _on_stop_motor_pressed(self):
        self._set_rads(0.0)
        self._motor_stopped = False  # waiting for real confirmation

        self._stop_motor_btn.setText("STOPPING")
        self._stop_motor_btn.setStyleSheet(
            "background-color: #f51d1d; color: #FFFFFF;"
        )
        self._stop_motor_btn.setEnabled(False)

    # ---------------- EXTERNAL STATE UPDATE (FROM ENCODER) ----------------

    def update_velocity_state(self, velocity: float):

        if abs(velocity) < STOP_THRESHOLD:
            self._reset_stop_btn()

    def _reset_stop_btn(self):
        self._stop_motor_btn.setText("STOP")
        self._stop_motor_btn.setStyleSheet("background-color: #b53131; color: #FFFFFF;")
        self._stop_motor_btn.setEnabled(True)

    # ---------------- INPUT HANDLING ----------------

    def _on_slider_changed(self, raw: int):
        self._set_rads(raw / 100.0, from_slider=True)

    def _step_up(self):
        self._set_rads(self._motor_rads + STEP_RADS)

    def _step_down(self):
        self._set_rads(self._motor_rads - STEP_RADS)

    def _open_numpad(self):
        dlg = NumpadDialog(
            self,
            "Target Motor Speed",
            self._motor_rads,
            MIN_RADS,
            MAX_RADS
        )
        if dlg.exec() and dlg.get_value() is not None:
            self._set_rads(dlg.get_value())

    # ---------------- PUBLIC API ----------------

    def get_rads(self) -> float:
        return self._motor_rads