#
# Title: gui/widgets/scaled_preview.py
# Purpose: QLabel that scales incoming frames to fit while preserving aspect ratio

from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class ScaledPreviewLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumHeight(180)
        self._frame: QImage | None = None

    def set_frame(self, frame):
        h, w, channels = frame.shape
        self._frame = QImage(frame.data, w, h, w * channels, QImage.Format.Format_BGR888)
        self._update_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_pixmap()

    def _update_pixmap(self):
        if self._frame is None: return
        pixmap = QPixmap.fromImage(self._frame).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pixmap)