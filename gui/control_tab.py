#
# Title: gui/control_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: I/O Control tab — motor speed, live graph, lights

import collections

# PyQt6 Modules
import pyqtgraph as pg
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

# Internal Modules
from gui.widgets.value_display import ValueDisplay
from gui.widgets.speed_control import SpeedControl
from gui.theme import COLOUR_GREEN, COLOUR_BLUE, COLOUR_ORANGE

# Plot Constants
HISTORY_LEN  = 100
POLL_RATE_MS = 50

# Visual Constants
LEFT_PANEL_FIXED_WIDTH    = 320
RIGHT_PANEL_FIXED_WIDTH   = 420

# Serial Parameter IDs -> POTENTIAL IMPROVEMENT: Grab from config.json...
VELOCITY_PARAMETER_ID = 0x10
SETPOINT_PARAMETER_ID = 0x01
RAMPED_PARAMETER_ID = 0x03
LIGHT_CONTROL_PARAMETER_ID = 0x30

class ControlTab(QWidget):
    def __init__(self, handler):
        super().__init__()
        self._serial_handler = handler

        # Variables to store polled MCU values
        self._latest_velocity       = 0.0
        self._latest_setpoint       = 0.0
        self._latest_ramped         = 0.0

        # Buffer to store previous polled MCU values
        self._velocity_buf          = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._setpoint_buf          = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._ramped_buf            = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)

        self._build_ui()

        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left — value displays + speed control + lights (320px) ───────
        left = QWidget()
        left.setFixedWidth(LEFT_PANEL_FIXED_WIDTH)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(8, 8, 8, 8)
        left_layout.setSpacing(8)

        # Value displays
        self._velocity_display = ValueDisplay("Encoder Velocity", "rad/s", COLOUR_GREEN)
        self._setpoint_display = ValueDisplay("Setpoint",         "rad/s", COLOUR_BLUE)
        self._ramped_display   = ValueDisplay("Ramped Setpoint",  "rad/s", COLOUR_ORANGE)

        left_layout.addWidget(self._velocity_display)
        left_layout.addWidget(self._setpoint_display)
        left_layout.addWidget(self._ramped_display)

        line1 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line1.setStyleSheet("color: #333333;")
        left_layout.addWidget(line1)

        # Speed control
        self._speed_control = SpeedControl()
        self._speed_control.speed_changed.connect(self._on_setpoint_changed)
        left_layout.addWidget(self._speed_control)

        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setStyleSheet("color: #333333;")
        left_layout.addWidget(line2)

        # Lights
        self._lights_btn = QPushButton("Toggle Light")
        self._lights_btn.setCheckable(True)
        self._lights_btn.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self._lights_btn.clicked.connect(self._on_lights_toggled)
        left_layout.addWidget(self._lights_btn)

        root.addWidget(left)

        # ── Vertical Divider ───────────────────────────────────────
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.VLine)
        divider.setStyleSheet("color: #333333;")
        root.addWidget(divider)

        # ── Right — graph + speed control (480px) ─────────
        right = QWidget()
        right.setFixedWidth(RIGHT_PANEL_FIXED_WIDTH)
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 12, 8, 12)
        right_layout.setSpacing(8)

        pg.setConfigOption('background', '#1A1A1A')
        pg.setConfigOption('foreground', '#AAAAAA')

        self._plot = pg.PlotWidget()
        self._plot.setTitle("Realtime Motor Angular Velocity")
        self._plot.setLabel('left', 'Encoder Velocity (rad/s)')
        self._plot.setLabel('bottom', f'samples (at {(1 / (POLL_RATE_MS / 1000))} Hz)')
        self._plot.setYRange(0, 30)
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.setFixedHeight(320)

        self._velocity_curve = self._plot.plot(
            list(self._velocity_buf),
            pen=pg.mkPen(COLOUR_GREEN, width=2),
            name='Encoder Velocity'
        )
        self._setpoint_curve = self._plot.plot(
            list(self._setpoint_buf),
            pen=pg.mkPen(COLOUR_BLUE, width=2),
            name='Setpoint'
        )
        self._ramped_curve = self._plot.plot(
            list(self._ramped_buf),
            pen=pg.mkPen(COLOUR_ORANGE, width=2),
            name='Ramped Setpoint'
        )

        right_layout.addWidget(self._plot)

        root.addWidget(right)

    # ── Serial callbacks (serial thread) ──────────────────

    def _on_velocity_data(self, parameter_id: int, value: float): self._latest_velocity = value
    def _on_setpoint_data(self, parameter_id: int, value: float): self._latest_setpoint = value
    def _on_ramped_data(self, parameter_id: int, value: float): self._latest_ramped = value

    # ── Poll (main thread) ────────────────────────────────

    def _poll(self):

        # Get serial handler
        if not self._serial_handler: return

        # Get Parameters over serial
        self._serial_handler.get(VELOCITY_PARAMETER_ID)
        self._serial_handler.get(SETPOINT_PARAMETER_ID)
        self._serial_handler.get(RAMPED_PARAMETER_ID)

        # Update displays with latest data
        self._velocity_display.set_value(self._latest_velocity)
        self._setpoint_display.set_value(self._latest_setpoint)
        self._ramped_display.set_value(self._latest_ramped)

        # Append new data to buffers
        self._velocity_buf.append(self._latest_velocity)
        self._setpoint_buf.append(self._latest_setpoint)
        self._ramped_buf.append(self._latest_ramped)

        # Update plot curves with latest data
        self._velocity_curve.setData(list(self._velocity_buf))
        self._setpoint_curve.setData(list(self._setpoint_buf))
        self._ramped_curve.setData(list(self._ramped_buf))

        self._speed_control.update_velocity_state(self._latest_velocity)

    # ── UI callbacks ──────────────────────────────────────

    def _on_setpoint_changed(self, value: float):
        if self._serial_handler:
            self._serial_handler.set(SETPOINT_PARAMETER_ID, value)

    def _on_lights_toggled(self, checked: bool):

        if checked: 
            self._lights_btn.setText("Light is ON")
            self._lights_btn.setStyleSheet("background-color: #004e8a; color: #FFFFFF;")
        else: 
            self._lights_btn.setText("Light is OFF")
            self._lights_btn.setStyleSheet("background-color: #2A2A2A; color: #FFFFFF;")

        if self._serial_handler:
            self._serial_handler.set(LIGHT_CONTROL_PARAMETER_ID, 255.0 if checked else 0.0)


    # ── Public API ────────────────────────────────────────

    def on_connected(self):

        # Attach listeners on each parameter
        if self._serial_handler:
            self._serial_handler.on_parameter(VELOCITY_PARAMETER_ID, self._on_velocity_data)
            self._serial_handler.on_parameter(SETPOINT_PARAMETER_ID, self._on_setpoint_data)
            self._serial_handler.on_parameter(RAMPED_PARAMETER_ID,   self._on_ramped_data)

        # Start polling timer
        self._timer.start(POLL_RATE_MS)

    def on_disconnected(self):

        # Stop polling timer
        self._timer.stop()

        # Reset plot
        self._velocity_buf = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._setpoint_buf = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._ramped_buf = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)

        # Reset display to zero
        self._velocity_display.set_value(0.0)
        self._setpoint_display.set_value(0.0)
        self._ramped_display.set_value(0.0)