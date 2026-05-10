#
# Title: gui/widgets/param_row.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Single parameter row widget — bound directly to Parameter dataclass
#

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.numpad import NumpadDialog
from theme import COLOUR_DIM, COLOUR_MUTED, COLOUR_ORANGE, COLOUR_TEXT, stylesheet_compact_icon_button


BTN_STYLE = stylesheet_compact_icon_button()


class ParamRow(QWidget):

    changed = pyqtSignal()

    def __init__(self, parameter):
        super().__init__()

        self._param = parameter

        self._label = parameter.label
        self._default = parameter.default
        self._min_val = parameter.min
        self._max_val = parameter.max
        self._unit = parameter.unit

        self._saved = self._default
        self._pending = None

        self._build_ui()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _build_ui(self):

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # Name
        name_lbl = QLabel(self._label)
        name_lbl.setFixedWidth(140)
        name_lbl.setStyleSheet(f"color: {COLOUR_TEXT}; font-size: 13px;")
        layout.addWidget(name_lbl)

        # Saved value
        self._saved_lbl = QLabel(self._fmt(self._saved))
        self._saved_lbl.setFixedWidth(64)
        self._saved_lbl.setFont(QFont("Courier New", 12))
        self._saved_lbl.setStyleSheet(f"color: {COLOUR_MUTED};")
        layout.addWidget(self._saved_lbl)

        # Unit
        unit_lbl = QLabel(self._unit)
        unit_lbl.setFixedWidth(48)
        unit_lbl.setStyleSheet(f"color: {COLOUR_DIM}; font-size: 11px;")
        layout.addWidget(unit_lbl)

        # Edit
        edit_btn = QPushButton("Edit")
        edit_btn.setFixedSize(52, 36)
        edit_btn.setStyleSheet(BTN_STYLE)
        edit_btn.clicked.connect(self._on_edit)
        layout.addWidget(edit_btn)

        # Pending indicator
        self._arrow_lbl = QLabel("→")
        self._arrow_lbl.setFixedWidth(16)
        self._arrow_lbl.setStyleSheet(f"color: {COLOUR_DIM};")
        self._arrow_lbl.setVisible(False)
        layout.addWidget(self._arrow_lbl)

        self._pending_lbl = QLabel("")
        self._pending_lbl.setFixedWidth(64)
        self._pending_lbl.setFont(QFont("Courier New", 12, QFont.Weight.Bold))
        self._pending_lbl.setStyleSheet(f"color: {COLOUR_ORANGE};")
        self._pending_lbl.setVisible(False)
        layout.addWidget(self._pending_lbl)

        layout.addStretch()

        # Reset
        reset_btn = QPushButton("↺")
        reset_btn.setFont(QFont("Courier New", 16, QFont.Weight.Bold))
        reset_btn.setFixedSize(48, 48)
        reset_btn.setStyleSheet(BTN_STYLE)
        reset_btn.setToolTip(f"Reset to default ({self._fmt(self._default)})")
        reset_btn.clicked.connect(self._on_reset)
        layout.addWidget(reset_btn)


    # Helper
    def _fmt(self, value: float) -> str: return f"{value:.2f}"

    # ──────────────────────────────────────────────
    # Edit
    # ──────────────────────────────────────────────

    def _on_edit(self):

        current = self._pending if self._pending is not None else self._saved

        dlg = NumpadDialog(
            self,
            self._label,
            current,
            self._min_val,
            self._max_val
        )

        if dlg.exec() and dlg.get_value() is not None:

            value = dlg.get_value()

            if value == self._saved:

                self._pending = None
                self._arrow_lbl.setVisible(False)
                self._pending_lbl.setVisible(False)

            else:

                self._pending = value
                self._arrow_lbl.setVisible(True)
                self._pending_lbl.setText(self._fmt(value))
                self._pending_lbl.setVisible(True)

            self.changed.emit()

    # ──────────────────────────────────────────────
    # Reset
    # ──────────────────────────────────────────────

    def _on_reset(self):

        self._pending = self._default
        self._arrow_lbl.setVisible(True)
        self._pending_lbl.setText(self._fmt(self._default))
        self._pending_lbl.setVisible(True)

        self.changed.emit()

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def has_pending(self) -> bool: return self._pending is not None
    def get_pending(self): return self._pending
    def get_saved(self): return self._saved

    def confirm_save(self):

        if self._pending is not None:

            self._saved = self._pending

            self._saved_lbl.setText(self._fmt(self._saved))

            self._pending = None

            self._arrow_lbl.setVisible(False)
            self._pending_lbl.setVisible(False)

    def discard(self):

        self._pending = None
        self._arrow_lbl.setVisible(False)
        self._pending_lbl.setVisible(False)

    def reset_to_default(self):

        self._pending = self._default

        self._arrow_lbl.setVisible(True)
        self._pending_lbl.setText(self._fmt(self._default))
        self._pending_lbl.setVisible(True)

        self.changed.emit()