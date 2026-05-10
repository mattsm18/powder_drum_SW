#
# Title: gui/widgets/value_display.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Large numeric value display with label and unit

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from theme import COLOUR_MUTED


class ValueDisplay(QWidget):
    def __init__(
        self,
        label: str,
        unit: str,
        colour: str,
        decimals: int = 2,
        *,
        compact: bool = False,
    ):
        super().__init__()
        self._decimals = decimals
        self._compact = compact
        self._build_ui(label, unit, colour)

    def _build_ui(self, label: str, unit: str, colour: str):
        layout = QHBoxLayout(self)
        if self._compact:
            layout.setContentsMargins(4, 0, 4, 0)
            layout.setSpacing(6)
            lbl_pt, val_pt, unit_pt = 9, 15, 11
            self.setMaximumHeight(36)
        else:
            layout.setContentsMargins(8, 4, 0, 4)
            layout.setSpacing(4)
            lbl_pt, val_pt, unit_pt = 12, 20, 18

        self._label = QLabel(label)
        self._label.setStyleSheet(f"color: {COLOUR_MUTED}; font-size: {lbl_pt}px;")
        layout.addWidget(self._label)

        layout.addStretch()

        self._value_label = QLabel(f"0.{'0' * self._decimals}")
        self._value_label.setFont(QFont("Courier New", val_pt, QFont.Weight.Bold))
        self._value_label.setStyleSheet(f"color: {colour};")
        layout.addWidget(self._value_label)

        self._unit_label = QLabel(unit)
        self._unit_label.setStyleSheet(f"color: {COLOUR_MUTED}; font-size: {unit_pt}px;")
        layout.addWidget(self._unit_label)

    def set_value(self, value: float):
        self._value_label.setText(f"{value:.{self._decimals}f}")

    def set_unit(self, unit: str):
        self._unit_label.setText(unit)