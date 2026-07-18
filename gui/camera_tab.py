#
# Title: gui/camera_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Camera tab — live feed, CV overlay, recording, IP stream

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, QTimer

try: from picamera2 import Picamera2
except ImportError: Picamera2 = None

class CameraTab(QWidget):
    def __init__(self, handler):
        super().__init__()
        self._handler = handler
        self._picam2 = None
        self._build_ui()
        self._start_camera()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self._feed_label = QLabel("Initializing camera…")
        self._feed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._feed_label.setMinimumSize(640, 480)
        self._feed_label.setStyleSheet("background-color: black; color: white;")
        layout.addWidget(self._feed_label)

    def _start_camera(self):
        if Picamera2 is None:
            self._feed_label.setText("picamera2 not installed — cannot start camera feed")
            return

        try:
            self._picam2 = Picamera2()
            config = self._picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
            self._picam2.configure(config)
            self._picam2.start()
        except Exception as exc:
            self._feed_label.setText(f"Camera failed to start: {exc}")
            self._picam2 = None
            return

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_frame)
        self._timer.start(33)  # ~30 fps

    def _update_frame(self):
        if self._picam2 is None:
            return

        frame = self._picam2.capture_array()  # numpy array, RGB888 — ready for OpenCV later
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self._feed_label.setPixmap(
            pixmap.scaled(
                self._feed_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def closeEvent(self, event):
        self.stop_camera()
        super().closeEvent(event)

    # Clean stop function
    def stop_camera(self):
        if hasattr(self, "_timer"): self._timer.stop()
        if self._picam2 is not None:
            self._picam2.stop()
            self._picam2 = None