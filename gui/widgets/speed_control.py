#
# Title: gui/widgets/speed_control.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Speed control — 2×2 grid (motor/drum × rad/s/RPM); ω_drum = ω_motor / drum_to_motor_ratio
#

import math

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QSlider,
    QPushButton,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.numpad import NumpadDialog
from theme import (
    COLOUR_BLUE,
    COLOUR_HINT,
    COLOUR_ORANGE,
    stylesheet_compact_icon_button,
    stylesheet_stop_idle_button,
    stylesheet_stop_pending_button,
    stylesheet_value_readout_pad,
)

from config import get_parameter, get_ui_config, get_motor_config


def _rad_s_to_rpm(rad_s: float) -> float:
    return rad_s * 60.0 / (2.0 * math.pi)


def _rpm_to_rad_s(rpm: float) -> float:
    return rpm * (2.0 * math.pi) / 60.0


class SpeedControl(QWidget):
    speed_changed = pyqtSignal(float)

    def __init__(self):
        super().__init__()

        self._motor_config = get_motor_config()
        self._ui_config = get_ui_config()
        self._setpoint = get_parameter("setpoint")

        self._internal_setpoint = 0.0
        self._motor_stopped = False

        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(6)

        hint = QLabel("Tap a cell to type · Slider = motor shaft (rad/s)")
        hint.setStyleSheet(f"color: {COLOUR_HINT}; font-size: 10px;")
        hint.setWordWrap(False)
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(6)
        grid.setVerticalSpacing(4)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)

        corner = QWidget()
        corner.setFixedWidth(36)
        grid.addWidget(corner, 0, 0)

        hdr_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        motor_hdr = QLabel("Motor target")
        motor_hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motor_hdr.setFont(hdr_font)
        grid.addWidget(motor_hdr, 0, 1)

        drum_hdr = QLabel("Drum target")
        drum_hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drum_hdr.setFont(hdr_font)
        grid.addWidget(drum_hdr, 0, 2)

        rad_lbl = QLabel("rad/s")
        rad_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        rad_lbl.setStyleSheet(f"color: {COLOUR_HINT}; font-size: 10px;")
        grid.addWidget(rad_lbl, 1, 0)

        rpm_lbl = QLabel("RPM")
        rpm_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        rpm_lbl.setStyleSheet(f"color: {COLOUR_HINT}; font-size: 10px;")
        grid.addWidget(rpm_lbl, 2, 0)

        cell_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        cell_h = 40

        self._motor_rad_btn = QPushButton()
        self._motor_rad_btn.setFont(cell_font)
        self._motor_rad_btn.setMinimumHeight(cell_h)
        self._motor_rad_btn.setMaximumHeight(cell_h)
        self._motor_rad_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._motor_rad_btn.setStyleSheet(stylesheet_value_readout_pad(COLOUR_BLUE))
        self._motor_rad_btn.clicked.connect(self._open_numpad_motor_rad)
        grid.addWidget(self._motor_rad_btn, 1, 1)

        self._drum_rad_btn = QPushButton()
        self._drum_rad_btn.setFont(cell_font)
        self._drum_rad_btn.setMinimumHeight(cell_h)
        self._drum_rad_btn.setMaximumHeight(cell_h)
        self._drum_rad_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._drum_rad_btn.setStyleSheet(stylesheet_value_readout_pad(COLOUR_ORANGE))
        self._drum_rad_btn.clicked.connect(self._open_numpad_drum_rad)
        grid.addWidget(self._drum_rad_btn, 1, 2)

        self._motor_rpm_btn = QPushButton()
        self._motor_rpm_btn.setFont(cell_font)
        self._motor_rpm_btn.setMinimumHeight(cell_h)
        self._motor_rpm_btn.setMaximumHeight(cell_h)
        self._motor_rpm_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._motor_rpm_btn.setStyleSheet(stylesheet_value_readout_pad(COLOUR_BLUE))
        self._motor_rpm_btn.clicked.connect(self._open_numpad_motor_rpm)
        grid.addWidget(self._motor_rpm_btn, 2, 1)

        self._drum_rpm_btn = QPushButton()
        self._drum_rpm_btn.setFont(cell_font)
        self._drum_rpm_btn.setMinimumHeight(cell_h)
        self._drum_rpm_btn.setMaximumHeight(cell_h)
        self._drum_rpm_btn.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self._drum_rpm_btn.setStyleSheet(stylesheet_value_readout_pad(COLOUR_ORANGE))
        self._drum_rpm_btn.clicked.connect(self._open_numpad_drum_rpm)
        grid.addWidget(self._drum_rpm_btn, 2, 2)

        layout.addLayout(grid)

        layout.addSpacing(4)

        control_layout = QHBoxLayout()
        control_layout.setSpacing(8)
        control_layout.setContentsMargins(0, 2, 0, 0)

        self._minus_btn = QPushButton("−")
        self._minus_btn.setFont(QFont("Segoe UI", 16))
        self._minus_btn.setStyleSheet(stylesheet_compact_icon_button())
        self._minus_btn.clicked.connect(self._step_down)

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(0)
        self._slider.setMaximum(int(self._setpoint.max * 100))
        self._slider.setValue(0)
        self._slider.valueChanged.connect(self._on_slider_changed)

        self._plus_btn = QPushButton("+")
        self._plus_btn.setFixedSize(56, 56)
        self._plus_btn.setFont(QFont("Segoe UI", 16))
        self._plus_btn.setStyleSheet(stylesheet_compact_icon_button())
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
        self._stop_motor_btn.setStyleSheet(stylesheet_stop_idle_button())
        self._stop_motor_btn.clicked.connect(self._on_stop_motor_pressed)
        layout.addWidget(self._stop_motor_btn)

        self.set_display_value(0.0)

    # ---------------- Ratio: ω_drum = ω_motor / ratio ----------------

    def _ratio(self) -> float:
        r = float(self._motor_config["drum_to_motor_ratio"])
        return r if r > 0 else 1.0

    def _drum_from_motor(self, motor_rad_s: float) -> float:
        return motor_rad_s / self._ratio()

    def _motor_from_drum(self, drum_rad_s: float) -> float:
        return drum_rad_s * self._ratio()

    @staticmethod
    def _text_cell_rad(rad_s: float) -> str:
        return f"{rad_s:.2f} rad/s"

    @staticmethod
    def _text_cell_rpm(rpm: float) -> str:
        return f"{rpm:.1f} RPM"

    # ---------------- CORE ----------------

    def _set_speed(self, value: float, from_slider: bool = False):
        value = max(self._setpoint.min, min(self._setpoint.max, value))
        self._internal_setpoint = value
        self.set_display_value(value)

        if not from_slider:
            self._slider.blockSignals(True)
            self._slider.setValue(int(value * 100))
            self._slider.blockSignals(False)

        self.speed_changed.emit(value)

    # ---------------- STOP ----------------

    def _on_stop_motor_pressed(self):
        self._set_speed(0.0)
        self._motor_stopped = False

        self._stop_motor_btn.setText("STOPPING")
        self._stop_motor_btn.setStyleSheet(stylesheet_stop_pending_button())
        self._stop_motor_btn.setEnabled(False)

    def _reset_stop_btn(self):
        self._stop_motor_btn.setText("STOP")
        self._stop_motor_btn.setStyleSheet(stylesheet_stop_idle_button())
        self._stop_motor_btn.setEnabled(True)

    # ---------------- DISPLAY ----------------

    def set_display_value(self, motor_rad_s: float):
        drum_rad_s = self._drum_from_motor(motor_rad_s)
        m_rpm = _rad_s_to_rpm(motor_rad_s)
        d_rpm = _rad_s_to_rpm(drum_rad_s)

        self._motor_rad_btn.setText(self._text_cell_rad(motor_rad_s))
        self._motor_rpm_btn.setText(self._text_cell_rpm(m_rpm))
        self._drum_rad_btn.setText(self._text_cell_rad(drum_rad_s))
        self._drum_rpm_btn.setText(self._text_cell_rpm(d_rpm))

    def is_motor_stopped(self, velocity: float):
        if abs(velocity) < self._motor_config["motor_stop_threshold"]:
            self._reset_stop_btn()

    # ---------------- Slider / steps ----------------

    def _on_slider_changed(self, raw: int):
        self._set_speed(raw / 100.0, from_slider=True)

    def _step_up(self):
        self._set_speed(self._internal_setpoint + self._ui_config.get("plus_minus_step"))

    def _step_down(self):
        self._set_speed(self._internal_setpoint - self._ui_config.get("plus_minus_step"))

    # ---------------- Numpads ----------------

    def _open_numpad_motor_rad(self):
        dlg = NumpadDialog(
            self,
            "Motor (rad/s)",
            self._internal_setpoint,
            self._setpoint.min,
            self._setpoint.max,
        )
        if dlg.exec() and dlg.get_value() is not None:
            self._set_speed(dlg.get_value())

    def _open_numpad_motor_rpm(self):
        lo = _rad_s_to_rpm(self._setpoint.min)
        hi = _rad_s_to_rpm(self._setpoint.max)
        cur = _rad_s_to_rpm(self._internal_setpoint)
        dlg = NumpadDialog(self, "Motor (RPM)", cur, lo, hi)
        if dlg.exec() and dlg.get_value() is not None:
            self._set_speed(_rpm_to_rad_s(dlg.get_value()))

    def _open_numpad_drum_rad(self):
        r = self._ratio()
        d_lo = self._setpoint.min / r
        d_hi = self._setpoint.max / r
        drum_now = self._internal_setpoint / r
        dlg = NumpadDialog(self, "Drum (rad/s)", drum_now, d_lo, d_hi)
        if dlg.exec() and dlg.get_value() is not None:
            self._set_speed(self._motor_from_drum(dlg.get_value()))

    def _open_numpad_drum_rpm(self):
        r = self._ratio()
        d_lo = self._setpoint.min / r
        d_hi = self._setpoint.max / r
        lo = _rad_s_to_rpm(d_lo)
        hi = _rad_s_to_rpm(d_hi)
        cur = _rad_s_to_rpm(self._internal_setpoint / r)
        dlg = NumpadDialog(self, "Drum (RPM)", cur, lo, hi)
        if dlg.exec() and dlg.get_value() is not None:
            drum_rad = _rpm_to_rad_s(dlg.get_value())
            self._set_speed(self._motor_from_drum(drum_rad))
