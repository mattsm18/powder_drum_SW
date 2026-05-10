#
# Title: gui/widgets/numpad.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Touchscreen numpad overlay dialog for numeric input

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from theme import (
    COLOUR_BLUE,
    COLOUR_HINT,
    COLOUR_RED,
    COLOUR_SURFACE,
    stylesheet_compact_icon_button,
    stylesheet_numpad_display,
    stylesheet_primary_action_button,
)

# Layout constants
DIALOG_WIDTH  = 280
BTN_HEIGHT    = 48
BTN_STYLE     = f"{stylesheet_compact_icon_button()} border-radius: 4px;"


class NumpadDialog(QDialog):
    def __init__(self, parent, title: str, current_value: float, min_val: float, max_val: float):
        super().__init__(parent)
        self._min_val = min_val
        self._max_val = max_val
        self._input   = str(round(current_value, 2))
        self._value   = None

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setFixedWidth(DIALOG_WIDTH)
        self.setStyleSheet(f"background-color: {COLOUR_SURFACE};")

        self._build_ui(title)

        # Centre over parent after layout is computed
        self.adjustSize()
        if parent:
            geo = parent.window().geometry()
            x   = geo.x() + (geo.width()  - self.width())  // 2
            y   = geo.y() + (geo.height() - self.height()) // 2
            self.move(x, y)

    def _build_ui(self, title: str):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 4, 12, 12)
        layout.setSpacing(8)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_lbl.setFixedHeight(20)
        layout.addWidget(title_lbl)

        # Input display
        self._display = QLabel(self._input)
        self._display.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._display.setFont(QFont("Courier New", 22, QFont.Weight.Bold))
        self._display.setFixedHeight(48)
        self._display.setStyleSheet(stylesheet_numpad_display())
        layout.addWidget(self._display)

        # Range hint
        hint = QLabel(f"{self._min_val:.2f} – {self._max_val:.2f}")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setFixedHeight(18)
        hint.setStyleSheet(f"color: {COLOUR_HINT}; font-size: 11px;")
        layout.addWidget(hint)

        # Numpad grid
        grid = QGridLayout()
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 0, 0)

        keys = [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['.', '0', '⌫'],
        ]

        for row, key_row in enumerate(keys):
            for col, key in enumerate(key_row):
                btn = QPushButton(key)
                btn.setFixedHeight(BTN_HEIGHT)
                btn.setFont(QFont("Segoe UI", 13))
                btn.setStyleSheet(BTN_STYLE)
                btn.clicked.connect(lambda _, k=key: self._on_key(k))
                grid.addWidget(btn, row, col)

        layout.addLayout(grid)

        # Cancel / Set
        action = QHBoxLayout()
        action.setSpacing(6)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(BTN_HEIGHT)
        cancel_btn.setStyleSheet(
            f"{BTN_STYLE} color: {COLOUR_RED}; border: 1px solid {COLOUR_RED};"
        )
        cancel_btn.clicked.connect(self.reject)

        set_btn = QPushButton("Set")
        set_btn.setFixedHeight(BTN_HEIGHT)
        set_btn.setStyleSheet(f"{BTN_STYLE} {stylesheet_primary_action_button()}")
        set_btn.clicked.connect(self._on_set)

        action.addWidget(cancel_btn)
        action.addWidget(set_btn)
        layout.addLayout(action)

    def _on_key(self, key: str):
        if key == '⌫':
            self._input = self._input[:-1] or '0'
        elif key == '.':
            if '.' not in self._input:
                self._input += '.'
        else:
            self._input = key if self._input == '0' else self._input + key

        if len(self._input) > 7:
            self._input = self._input[:7]

        self._display.setStyleSheet(stylesheet_numpad_display())
        self._display.setText(self._input)

    def _on_set(self):
        try:
            value = float(self._input)
            if self._min_val <= value <= self._max_val:
                self._value = value
                self.accept()
                return
        except ValueError:
            pass

        # Invalid — flash red
        self._display.setText("Out of range" if self._input else "?")
        self._display.setStyleSheet(stylesheet_numpad_display(invalid=True))
        self._input = '0'

    def get_value(self) -> float | None:
        return self._value