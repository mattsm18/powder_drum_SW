#
# Title: gui/widgets/preview_widget.py
# Purpose: Camera preview widget with overlay animations

#    Camera preview widget.
#
#    Responsibilities
#    ----------------
#    • Display latest camera frame
#    • Preserve aspect ratio
#    • Draw recording indicator
#    • Draw camera flash
#    • Draw streaming animation
#
#    Future overlays:
#        - Crosshair
#        - CV bounding boxes
#        - Object labels
#        - FPS
#        - Histogram
#        - Grid

import math

from PyQt6.QtCore import (Qt,QRectF,QPointF,QTimer,)
from PyQt6.QtGui import (QColor,QImage,QPainter,QPen,)
from PyQt6.QtWidgets import QWidget


class PreviewWidget(QWidget):

    # ------------------------------------------------------------------
    # Constructor
    # ------------------------------------------------------------------

    def __init__(self):
        super().__init__()

        self.setMinimumSize(640, 480)

        # Black background
        self.setAutoFillBackground(False)

        # Current camera frame
        self._frame: QImage | None = None

        # Rectangle occupied by displayed image
        self._image_rect = QRectF()

        # ==============================================================
        # Recording state
        # ==============================================================

        self._recording = False
        self._record_visible = True

        self._record_timer = QTimer(self)
        self._record_timer.setInterval(500)
        self._record_timer.timeout.connect(self._record_timeout)

        # ==============================================================
        # Camera flash
        # ==============================================================

        self._flash_alpha = 0

        self._flash_timer = QTimer(self)
        self._flash_timer.setInterval(16)
        self._flash_timer.timeout.connect(self._flash_timeout)

        # ==============================================================
        # Streaming animation
        # ==============================================================

        self._streaming = False
        self._stream_phase = 0.0

        self._stream_timer = QTimer(self)
        self._stream_timer.setInterval(16)
        self._stream_timer.timeout.connect(self._stream_timeout)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_frame(self, frame):

        h, w, channels = frame.shape
        self._frame = QImage(frame.data, w, h, w * channels, QImage.Format.Format_BGR888).copy()
        self.update()

    # ------------------------------------------------------------------

    def set_recording(self, recording: bool):

        if self._recording == recording: return
        self._recording = recording

        if recording:
            self._record_visible = True
            self._record_timer.start()
        else:
            self._record_timer.stop()
            self._record_visible = False

        self.update()

    # ------------------------------------------------------------------

    def trigger_flash(self):

        self._flash_alpha = 255

        if not self._flash_timer.isActive(): self._flash_timer.start()

        self.update()

    # ------------------------------------------------------------------

    def set_streaming(self, streaming: bool):

        if self._streaming == streaming: return
        self._streaming = streaming

        if streaming:
            self._stream_phase = 0
            self._stream_timer.start()
        else:
            self._stream_timer.stop()

        self.update()

    # ------------------------------------------------------------------
    # Animation timers
    # ------------------------------------------------------------------

    def _record_timeout(self):

        self._record_visible = not self._record_visible
        self.update()

    # ------------------------------------------------------------------

    def _flash_timeout(self):

        self._flash_alpha -= 25

        if self._flash_alpha <= 0:
            self._flash_alpha = 0
            self._flash_timer.stop()

        self.update()

    # ------------------------------------------------------------------

    def _stream_timeout(self):

        self._stream_phase += 0.10
        if self._stream_phase > math.tau: self._stream_phase = 0
        self.update()

    # ------------------------------------------------------------------
    # QWidget events
    # ------------------------------------------------------------------

    def resizeEvent(self, event):

        super().resizeEvent(event)
        self.update()

    # ------------------------------------------------------------------
    # Painting
    # ------------------------------------------------------------------

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Draw background
        painter.fillRect(self.rect(), Qt.GlobalColor.black)

        if self._frame is not None: self._draw_frame(painter)

        self._draw_recording(painter)
        self._draw_streaming(painter)
        self._draw_flash(painter)

    def _draw_frame(self, painter: QPainter):

        image_w = self._frame.width()
        image_h = self._frame.height()

        widget_w = self.width()
        widget_h = self.height()

        image_ratio = image_w / image_h
        widget_ratio = widget_w / widget_h

        if image_ratio > widget_ratio:

            draw_w = widget_w
            draw_h = draw_w / image_ratio

        else:

            draw_h = widget_h
            draw_w = draw_h * image_ratio

        x = (widget_w - draw_w) / 2
        y = (widget_h - draw_h) / 2

        self._image_rect = QRectF(x, y, draw_w, draw_h)

        painter.drawImage(
            self._image_rect,
            self._frame,
        )

    def _draw_recording(self, painter: QPainter):

        if not self._recording: return
        if not self._record_visible: return

        margin = 18
        radius = 10

        x = self._image_rect.right() - margin - radius
        y = self._image_rect.top() + margin + radius

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(230, 0, 0))

        painter.drawEllipse(QPointF(x, y), radius, radius)
        painter.setPen(Qt.GlobalColor.white)

        font = painter.font()
        font.setBold(True)
        font.setPointSize(11)
        painter.setFont(font)

    def _draw_flash(self, painter: QPainter):

        if self._flash_alpha == 0: return
        colour = QColor(255, 255, 255, self._flash_alpha)
        painter.fillRect(self._image_rect, colour)

    def _draw_streaming(self, painter: QPainter):

        if not self._streaming: return

        cx = self._image_rect.right() - 35
        cy = self._image_rect.bottom() - 35

        painter.setBrush(Qt.BrushStyle.NoBrush)

        for i in range(3):

            radius = 10 + i * 16
            alpha = 170 + 70 * math.sin(self._stream_phase + i)
            pen = QPen(QColor(0, 170, 255, int(alpha)))
            pen.setWidth(3)

            painter.setPen(pen)
            painter.drawArc(
                int(cx - radius),
                int(cy - radius),
                radius * 2,
                radius * 2,
                -45 * 16,
                90 * 16,
            )

        painter.setBrush(QColor(0, 170, 255))
        painter.setPen(Qt.PenStyle.NoPen)

        painter.drawEllipse(QPointF(cx, cy), 4, 4)