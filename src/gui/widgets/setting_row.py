#
# Title: gui/widgets/setting_rows.py
# Purpose: Reusable settings-row widgets that adapt to a value's type
#          (bool -> checkbox, numeric -> slider or numpad, tuple -> paired numpad)

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QCheckBox, QPushButton, QSlider
from PyQt6.QtCore import pyqtSignal, Qt

from gui.widgets.numpad import NumpadDialog
from models.camera_model import CameraSetting


class _BaseRow(QWidget):
    value_changed = pyqtSignal(object, object)  # (CameraSetting, new_value)

    def __init__(self, setting: CameraSetting, label: str):
        super().__init__()
        self.setting = setting

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)

        self._label = QLabel(label)
        self._label.setFixedWidth(140)
        self._layout.addWidget(self._label)


class BoolSettingRow(_BaseRow):
    def __init__(self, setting: CameraSetting, label: str, current_value: bool):
        super().__init__(setting, label)

        self._checkbox = QCheckBox()
        self._checkbox.setObjectName("settingCheckbox")
        self._checkbox.setChecked(current_value)
        self._checkbox.setFixedHeight(44)  # generous tap target beyond just the indicator
        self._checkbox.stateChanged.connect(self._on_changed)

        self._layout.addWidget(self._checkbox)
        self._layout.addStretch()

    def _on_changed(self, state):
        self.value_changed.emit(self.setting, bool(state))

    def set_value(self, value: bool):
        self._checkbox.blockSignals(True)
        self._checkbox.setChecked(value)
        self._checkbox.blockSignals(False)

    def set_enabled(self, enabled: bool):
        self._checkbox.setEnabled(enabled)


class SliderSettingRow(_BaseRow):

    def __init__(self, setting: CameraSetting, label: str, current_value: float, min_val: float, max_val: float, is_int: bool = False, scale: int = 1):
        super().__init__(setting, label)
        self._is_int = is_int
        self._scale = 1 if is_int else scale

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setObjectName("settingSlider")
        self._slider.setRange(int(min_val * self._scale), int(max_val * self._scale))
        self._slider.setValue(int(current_value * self._scale))
        self._slider.setFixedHeight(44)
        self._slider.valueChanged.connect(self._on_changed)

        self._value_lbl = QLabel(self._format(current_value))
        self._value_lbl.setFixedWidth(70)
        self._value_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._layout.addWidget(self._slider, stretch=1)
        self._layout.addWidget(self._value_lbl)

    def _format(self, value) -> str:
        return str(int(value)) if self._is_int else f"{value:.2f}"

    def _on_changed(self, raw: int):
        value = raw if self._is_int else raw / self._scale
        self._value_lbl.setText(self._format(value))
        self.value_changed.emit(self.setting, value)

    def set_value(self, value):
        self._slider.blockSignals(True)
        self._slider.setValue(int(value * self._scale))
        self._value_lbl.setText(self._format(value))
        self._slider.blockSignals(False)

    def set_enabled(self, enabled: bool):
        self._slider.setEnabled(enabled)


class NumericSettingRow(_BaseRow):
    def __init__(self, setting: CameraSetting, label: str, current_value: float,
                 min_val: float, max_val: float, is_int: bool = False):
        super().__init__(setting, label)
        self._min_val = min_val
        self._max_val = max_val
        self._is_int = is_int
        self._value = current_value

        self._value_btn = QPushButton(self._format(current_value))
        self._value_btn.setObjectName("settingValueButton")
        self._value_btn.setFixedWidth(100)
        self._value_btn.clicked.connect(self._open_numpad)

        self._layout.addWidget(self._value_btn)
        self._layout.addStretch()

    def _format(self, value) -> str:
        return str(int(value)) if self._is_int else f"{value:.2f}"

    def _open_numpad(self):
        dialog = NumpadDialog(self, self._label.text(), self._value,
                               self._min_val, self._max_val)
        if dialog.exec():
            value = dialog.get_value()
            if value is not None:
                value = int(value) if self._is_int else value
                self._value = value
                self._value_btn.setText(self._format(value))
                self.value_changed.emit(self.setting, value)

    def set_value(self, value):
        self._value = value
        self._value_btn.setText(self._format(value))

    def set_enabled(self, enabled: bool):
        self._value_btn.setEnabled(enabled)


class TupleSettingRow(_BaseRow):
    
    def __init__(self, setting: CameraSetting, label: str, current_value: tuple,
                 min_val: float, max_val: float, is_int: bool = False):
        super().__init__(setting, label)
        self._min_val = min_val
        self._max_val = max_val
        self._is_int = is_int
        self._value = list(current_value)

        self._btn_a = QPushButton(self._format(self._value[0]))
        self._btn_b = QPushButton(self._format(self._value[1]))
        for btn in (self._btn_a, self._btn_b):
            btn.setObjectName("settingValueButton")
            btn.setFixedWidth(70)

        self._btn_a.clicked.connect(lambda: self._open_numpad(0))
        self._btn_b.clicked.connect(lambda: self._open_numpad(1))

        self._layout.addWidget(self._btn_a)
        self._layout.addWidget(self._btn_b)
        self._layout.addStretch()

    def _format(self, value) -> str:
        return str(int(value)) if self._is_int else f"{value:.2f}"

    def _open_numpad(self, index: int):
        dialog = NumpadDialog(self, self._label.text(), self._value[index],
                               self._min_val, self._max_val)
        if dialog.exec():
            value = dialog.get_value()
            if value is not None:
                value = int(value) if self._is_int else value
                self._value[index] = value
                (self._btn_a if index == 0 else self._btn_b).setText(self._format(value))
                self.value_changed.emit(self.setting, tuple(self._value))

    def set_enabled(self, enabled: bool):
        self._btn_a.setEnabled(enabled)
        self._btn_b.setEnabled(enabled)