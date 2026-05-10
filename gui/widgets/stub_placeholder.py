#
# Shared “coming soon” placeholder — same structure everywhere for consistent spacing/styling.

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from theme import STYLE_STUB_LABEL


def build_stub_placeholder(message: str, parent: QWidget | None = None) -> QWidget:
    widget = QWidget(parent)
    layout = QVBoxLayout(widget)
    label = QLabel(message)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet(STYLE_STUB_LABEL)
    layout.addWidget(label)
    return widget
