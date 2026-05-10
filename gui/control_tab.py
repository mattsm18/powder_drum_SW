#
# Title: gui/control_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: I/O Control tab — motor speed, live graph, lights
#

import collections
import pyqtgraph as pg

from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QFrame
)

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont

from gui.widgets.value_display import ValueDisplay
from gui.widgets.speed_control import SpeedControl
from theme import COLOUR_BG, COLOUR_GREEN, COLOUR_BLUE, COLOUR_ORANGE, COLOUR_LIGHT_ON, COLOUR_MUTED, COLOUR_SURFACE, COLOUR_WHITE

from config import get_parameter, get_ui_config

class ControlTab(QWidget):

    def __init__(self, handler):
        super().__init__()

        self._serial_handler = handler

        # ──────────────────────────────────────────────
        # Config-driven parameters
        # ──────────────────────────────────────────────
        self._ui_config = get_ui_config()
        self._hist_len = self._ui_config.get("history_length")

        self._velocity = get_parameter("encoderAngularVelocity")
        self._setpoint = get_parameter("setpoint")
        self._ramped   = get_parameter("rampedSetpoint")
        self._lights   = get_parameter("lights")

        # ──────────────────────────────────────────────
        # Runtime state
        # ──────────────────────────────────────────────
        self._latest_velocity = 0.0
        self._latest_setpoint = 0.0
        self._latest_ramped = 0.0

        self._velocity_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)
        self._setpoint_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)
        self._ramped_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)

        self._build_ui()

        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _build_ui(self):

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT PANEL ─────────────────────────────
        left = QWidget()
        left.setFixedWidth(320)

        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 6, 8, 8)
        left_layout.setSpacing(8)
        
        #### MOTOR CONTROL ####
        self._speed_control = SpeedControl()
        self._speed_control.speed_changed.connect(self._on_setpoint_changed)
        left_layout.addWidget(self._speed_control)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        left_layout.addWidget(line2)

        #### LIGHT CONTROL ####
        self._lights_btn = QPushButton("Toggle Light")
        self._lights_btn.setCheckable(True)
        self._lights_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._lights_btn.clicked.connect(self._on_lights_toggled)
        left_layout.addWidget(self._lights_btn)

        root.addWidget(left)

        # ── DIVIDER ────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        root.addWidget(divider)

        # ── RIGHT PANEL ────────────────────────────
        right = QWidget()
        right.setFixedWidth(420)

        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 12, 8, 12)
        right_layout.setSpacing(6)

        pg.setConfigOption('background', COLOUR_BG)
        pg.setConfigOption('foreground', COLOUR_MUTED)

        #### PLOT ####
        self._plot = pg.PlotWidget()
        self._plot.setFixedHeight(292)
        self._plot.setYRange(self._setpoint.min - 10, self._setpoint.max + 10)

        self._plot.setTitle("Setpoint vs Measured Angular Velocity")
        self._plot.setLabel('left', f"{self._velocity.label} ({self._velocity.unit})")
        self._plot.setMouseEnabled(x=False, y=False)

        hz = 1000 / self._ui_config.get("poll_rate_ms")
        self._plot.setLabel('bottom', f"samples ({hz:.1f} Hz)")
        
        self._velocity_curve = self._plot.plot(pen=pg.mkPen(COLOUR_GREEN, width=2))
        self._setpoint_curve = self._plot.plot(pen=pg.mkPen(COLOUR_BLUE, width=2))
        self._ramped_curve = self._plot.plot(pen=pg.mkPen(COLOUR_ORANGE, width=2))

        right_layout.addWidget(self._plot)

        plot_readout_line = QFrame()
        plot_readout_line.setFrameShape(QFrame.Shape.HLine)
        right_layout.addWidget(plot_readout_line)

        #### READINGS ####
        self._velocity_display = ValueDisplay(self._velocity.label, self._velocity.unit, COLOUR_GREEN, compact=True)
        self._setpoint_display = ValueDisplay( self._setpoint.label, self._setpoint.unit, COLOUR_BLUE, compact=True)
        self._ramped_display = ValueDisplay(self._ramped.label, self._ramped.unit, COLOUR_ORANGE, compact=True)

        readouts_wrap = QWidget()
        readouts_layout = QVBoxLayout(readouts_wrap)
        readouts_layout.setContentsMargins(0, 0, 0, 0)
        readouts_layout.setSpacing(2)
        readouts_layout.addWidget(self._velocity_display)
        readouts_layout.addWidget(self._setpoint_display)
        readouts_layout.addWidget(self._ramped_display)
        right_layout.addWidget(readouts_wrap)

        root.addWidget(right)

    # ──────────────────────────────────────────────
    # Poll loop
    # ──────────────────────────────────────────────

    def _poll(self):

        # Get latest values
        self._serial_handler.get(self._velocity.id)
        self._serial_handler.get(self._setpoint.id)
        self._serial_handler.get(self._ramped.id)

        # Update display and internal graph buffer with latest values
        self._velocity_display.set_value(self._latest_velocity)
        self._setpoint_display.set_value(self._latest_setpoint)
        self._ramped_display.set_value(self._latest_ramped)

        # Append latest values to plot buffer
        self._velocity_buf.append(self._latest_velocity)
        self._setpoint_buf.append(self._latest_setpoint)
        self._ramped_buf.append(self._latest_ramped)
        
        # Update plot with buffer
        self._velocity_curve.setData(list(self._velocity_buf))
        self._setpoint_curve.setData(list(self._setpoint_buf))
        self._ramped_curve.setData(list(self._ramped_buf))

        # Update speed control widget with latest velocity
        self._speed_control.is_motor_stopped(self._latest_velocity)

    # ──────────────────────────────────────────────
    # UI events
    # ──────────────────────────────────────────────

    def _on_setpoint_changed(self, value: float):

        if self._serial_handler.is_connected():
            self._serial_handler.set(self._setpoint.id, value)

    def _on_lights_toggled(self, checked: bool):

        if checked:
            self._lights_btn.setText("Light is ON")
            self._lights_btn.setStyleSheet(f"background-color: {COLOUR_LIGHT_ON}; color: {COLOUR_WHITE};")
        else:
            self._lights_btn.setText("Light is OFF")
            self._lights_btn.setStyleSheet(f"background-color: {COLOUR_SURFACE}; color: {COLOUR_WHITE};")

        if self._serial_handler.is_connected(): 
            self._serial_handler.set(self._lights.id, 1.0 if checked else 0.0)

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def on_connected(self):

        if self._serial_handler:
            
            # On incoming parameter, update latest value
            self._serial_handler.on_parameter(self._velocity.id, lambda pid, val: setattr(self, '_latest_velocity', val))
            self._serial_handler.on_parameter(self._setpoint.id, lambda pid, val: setattr(self, '_latest_setpoint', val))
            self._serial_handler.on_parameter(self._ramped.id,   lambda pid, val: setattr(self, '_latest_ramped', val))

        self._timer.start(self._ui_config["poll_rate_ms"])

    def on_disconnected(self):

        self._timer.stop()

        self._velocity_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)
        self._setpoint_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)
        self._ramped_buf = collections.deque([0.0] * self._hist_len, maxlen=self._hist_len)

        self._velocity_display.set_value(0.0)
        self._setpoint_display.set_value(0.0)
        self._ramped_display.set_value(0.0)