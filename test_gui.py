#
# Title: tests/test_gui.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose:
# - Simple PyQt6 test GUI for motor speed control
# - Slider for speed setpoint (0-30 rad/s)
# - Real-time encoder angular velocity display (parameter_id 0x10)
# - Live plot of setpoint vs encoder angular velocity
# - Graph updates on main thread only to prevent lag

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import collections
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel, QSlider
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from comms.serial_handler import SerialHandler

PORT        = 'COM5'
BAUD        = 115200
MIN_RADS    = 0
MAX_RADS    = 30
HISTORY_LEN = 100

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motor Control")
        self.setMinimumSize(700, 600)

        # Data buffers — written by serial thread, read by main thread
        self._velocity_buf     = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._setpoint_buf     = collections.deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)
        self._current_setpoint = 0.0

        # Serial handler
        self._handler = SerialHandler(port=PORT, baud=BAUD)
        self._handler.on_parameter(0x10, self._on_velocity)
        self._handler.start()

        # Build UI
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Value displays ────────────────────────────────
        display_layout = QHBoxLayout()

        vel_layout = QVBoxLayout()
        vel_layout.addWidget(QLabel("Encoder Angular Velocity (rad/s)"))
        self._velocity_label = QLabel("0.000")
        self._velocity_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._velocity_label.setFont(QFont("Courier New", 36, QFont.Weight.Bold))
        self._velocity_label.setStyleSheet("color: #00FF88;")
        vel_layout.addWidget(self._velocity_label)

        sp_layout = QVBoxLayout()
        sp_layout.addWidget(QLabel("Setpoint (rad/s)"))
        self._setpoint_value_label = QLabel("0.000")
        self._setpoint_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._setpoint_value_label.setFont(QFont("Courier New", 36, QFont.Weight.Bold))
        self._setpoint_value_label.setStyleSheet("color: #00AAFF;")
        sp_layout.addWidget(self._setpoint_value_label)

        display_layout.addLayout(vel_layout)
        display_layout.addLayout(sp_layout)
        layout.addLayout(display_layout)

        # ── Live graph ────────────────────────────────────
        pg.setConfigOption('background', '#1E1E1E')
        pg.setConfigOption('foreground', '#AAAAAA')

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setTitle("Setpoint vs Encoder Angular Velocity")
        self._plot_widget.setLabel('left',   'rad/s')
        self._plot_widget.setLabel('bottom', 'samples')
        self._plot_widget.setYRange(MIN_RADS, MAX_RADS + 2)
        self._plot_widget.addLegend()
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)

        self._velocity_curve = self._plot_widget.plot(
            list(self._velocity_buf),
            pen=pg.mkPen('#00FF88', width=2),
            name='Encoder Velocity'
        )
        self._setpoint_curve = self._plot_widget.plot(
            list(self._setpoint_buf),
            pen=pg.mkPen('#00AAFF', width=2),
            name='Setpoint'
        )
        layout.addWidget(self._plot_widget)

        # ── Setpoint slider ───────────────────────────────
        self._setpoint_label = QLabel("Setpoint: 0.0 rad/s")
        self._setpoint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        slider_layout = QHBoxLayout()
        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setMinimum(MIN_RADS * 10)
        self._slider.setMaximum(MAX_RADS * 10)
        self._slider.setValue(0)
        self._slider.setTickInterval(50)
        self._slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._slider.valueChanged.connect(self._on_slider_changed)

        slider_layout.addWidget(QLabel(f"{MIN_RADS}"))
        slider_layout.addWidget(self._slider)
        slider_layout.addWidget(QLabel(f"{MAX_RADS}"))

        layout.addWidget(self._setpoint_label)
        layout.addLayout(slider_layout)

        # ── Poll + graph timer (main thread only) ─────────
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll)
        self._timer.start(100)

    def _on_slider_changed(self, raw_value: int):
        self._current_setpoint = raw_value / 10.0
        self._setpoint_label.setText(f"Setpoint: {self._current_setpoint:.1f} rad/s")
        self._setpoint_value_label.setText(f"{self._current_setpoint:.3f}")
        self._handler.set(0x01, self._current_setpoint)

    def _on_velocity(self, parameter_id: int, value: float):
        # Serial thread — only append to buffers, never touch Qt widgets
        self._velocity_buf.append(value)
        self._setpoint_buf.append(self._current_setpoint)

    def _poll(self):
        # Main thread — safe to update all Qt widgets here
        self._handler.get(0x10)

        # Snapshot deques once per poll
        vel = list(self._velocity_buf)
        sp  = list(self._setpoint_buf)

        # Update labels
        if vel:
            self._velocity_label.setText(f"{vel[-1]:.3f}")

        # Update graph
        self._velocity_curve.setData(vel)
        self._setpoint_curve.setData(sp)

    def closeEvent(self, event):
        self._timer.stop()
        self._handler.set(0x01, 0.0)
        self._handler.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())