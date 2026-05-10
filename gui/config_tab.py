#
# Title: gui/config_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Configuration tab — connection, motor params, vision (stub), stream (stub)

import serial.tools.list_ports

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QFrame,
    QScrollArea,
    QListWidget,
    QStackedWidget,
    QListWidgetItem,
    QMessageBox
)

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont

from gui.widgets.param_row import ParamRow
from gui.widgets.stub_placeholder import build_stub_placeholder
from gui.serial_link_notifier import SerialLinkNotifier
from theme import (
    COLOUR_GREEN,
    COLOUR_RED,
    COLOUR_BLUE,
    STYLE_SECTION_TITLE,
    STYLE_SEPARATOR_LINE,
    stylesheet_compact_icon_button,
    stylesheet_danger_outline_button,
    stylesheet_primary_action_button,
)

from config import get_parameters

import time

class ConfigTab(QWidget):

    serial_connection_state = pyqtSignal(bool)

    def __init__(self, handler):
        super().__init__()

        self._serial_handler = handler

        self._link_notifier = SerialLinkNotifier()
        self._link_notifier.link_lost.connect(self._on_serial_link_lost)

        # Internal memory
        self._connected = False
        self._param_rows: dict[str, ParamRow] = {}
        
        self._build_ui()

    # ──────────────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self) 
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left Navigation Menu
        self._menu_list = QListWidget()
        self._menu_list.setFixedWidth(180)

        # Content Area (Stacked Widget)
        self._content_stack = QStackedWidget()

        # Define our tabs/pages
        pages = [
            ("🔌   Connection", self._build_connection_tab()),
            ("⚙️   Motor", self._build_motor_tab()),
            ("👁️   Vision", build_stub_placeholder("👁️  Vision — Coming Soon")),
            ("📡   Stream", build_stub_placeholder("📡  Stream — Coming Soon")),
        ]

        for name, widget in pages:
            # Add to menu
            item = QListWidgetItem(name)
            self._menu_list.addItem(item)
            # Add to stack
            self._content_stack.addWidget(widget)

        # Handle switching pages
        self._menu_list.currentRowChanged.connect(self._content_stack.setCurrentIndex)
        self._menu_list.setCurrentRow(0) # Default to first page

        # Add components to the root layout
        root.addWidget(self._menu_list)
        root.addWidget(self._content_stack)

    # ──────────────────────────────────────────────────────
    # Connection Tab
    # ──────────────────────────────────────────────────────

    def _build_connection_tab(self) -> QWidget:

        widget = QWidget()

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        layout.addWidget(self._section_label("Serial Connection"))

        self._port_combo = QComboBox()
        self._port_combo.setMinimumHeight(44)

        self._refresh_serial_ports()

        self._baud_combo = QComboBox()
        self._baud_combo.setMinimumHeight(44)

        baud_options = [9600, 57600, 115200, 230400]

        for baud in baud_options:
            self._baud_combo.addItem(str(baud))

        self._baud_combo.setCurrentText("115200")

        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(44, 44)
        refresh_btn.setStyleSheet(stylesheet_compact_icon_button())
        refresh_btn.clicked.connect(self._refresh_serial_ports)

        self._connect_btn = QPushButton("Connect")
        self._connect_btn.setMinimumHeight(44)
        self._connect_btn.setCheckable(True)
        self._connect_btn.clicked.connect(self._on_connect_clicked)

        # Row 1: port, baud, refresh
        selectors_layout = QHBoxLayout()
        selectors_layout.addWidget(QLabel("Port:"))
        selectors_layout.addWidget(self._port_combo, stretch=2)
        selectors_layout.addWidget(QLabel("Baud:"))
        selectors_layout.addWidget(self._baud_combo, stretch=1)
        selectors_layout.addWidget(refresh_btn)

        # Row 2: connect button full width
        connect_layout = QHBoxLayout()
        connect_layout.addWidget(self._connect_btn)

        layout.addLayout(selectors_layout)
        layout.addLayout(connect_layout)

        self._status_label = QLabel("⬤  Disconnected")
        self._status_label.setStyleSheet(f"color: {COLOUR_RED}; font-size: 13px;")

        layout.addWidget(self._status_label)

        layout.addStretch()

        return widget

    # ──────────────────────────────────────────────────────
    # Motor Tab
    # ──────────────────────────────────────────────────────

    def _build_motor_tab(self) -> QWidget:

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)
        layout.addWidget(self._section_label("Motor & Controller Parameters"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.setSpacing(4)
        params_layout.setContentsMargins(0, 0, 0, 0)

        self._param_rows = {}

        # Iterate through writable motor parameters
        for param in get_parameters(group="motor", access="w"):

            row = ParamRow(param)
            row.changed.connect(self._on_param_changed)

            self._param_rows[param.name] = row

            params_layout.addWidget(row)

            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet(STYLE_SEPARATOR_LINE)
            params_layout.addWidget(line)

        params_layout.addStretch()

        scroll.setWidget(params_widget)
        layout.addWidget(scroll)

        # Buttons unchanged
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # Discard Button
        self._discard_btn = QPushButton("Discard")
        self._discard_btn.setFixedHeight(44)
        self._discard_btn.setStyleSheet(stylesheet_danger_outline_button())
        self._discard_btn.setEnabled(False)
        self._discard_btn.clicked.connect(self._on_discard)

        # Save Button
        self._save_btn = QPushButton("Save")
        self._save_btn.setFixedHeight(44)
        self._save_btn.setStyleSheet(stylesheet_primary_action_button())
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self._on_save)

        # Reset Button
        reset_all_btn = QPushButton("Reset All to Defaults")
        reset_all_btn.setFixedHeight(44)
        reset_all_btn.clicked.connect(self._on_reset_all)

        # Add all to Layout
        btn_layout.addWidget(reset_all_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(self._discard_btn)
        btn_layout.addWidget(self._save_btn)
        layout.addLayout(btn_layout)

        return widget

    # ──────────────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────────────

    def _section_label(self, text: str) -> QLabel:

        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        label.setStyleSheet(STYLE_SECTION_TITLE)
        return label

    def _refresh_serial_ports(self):

        self._port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self._port_combo.addItem(
                f"{port.device} — {port.description}",
                port.device
            )
        if not ports: self._port_combo.addItem("No ports found", None)

    # ──────────────────────────────────────────────────────
    # Connection Callbacks
    # ──────────────────────────────────────────────────────

    def _on_connect_clicked(self):

        if not self._connected: self._connect()
        else: self._disconnect()

    def _connect(self):

        port = self._port_combo.currentData()
        baud = int(self._baud_combo.currentText())

        if not port:

            self._status_label.setText("⬤  No port selected")
            self._status_label.setStyleSheet(f"color: {COLOUR_RED};")
            self._connect_btn.setChecked(False)
            return

        try:
            # Call serial connection
            self._serial_handler.connect(port, baud)
            self._serial_handler.set_link_lost_callback(self._link_notifier.link_lost.emit)
            self._serial_handler.start()
            self._connected = True

            # Update UI
            self._connect_btn.setText("Disconnect")
            self._status_label.setText(f"⬤  Connected — {port} @ {baud}")
            self._status_label.setStyleSheet(f"color: {COLOUR_GREEN};")

            # Emit pyqt Signal
            self.serial_connection_state.emit(True)

        except Exception as e:
            import traceback
            traceback.print_exc() 
            self._connected = False
            self._connect_btn.setChecked(False)
            self._status_label.setText(f"⬤  Failed: {e}")
            self._status_label.setStyleSheet(f"color: {COLOUR_RED};")

    def _on_serial_link_lost(self):
        if not self._connected:
            return
        self._disconnect(status_text="⬤  Connection lost — cable unplugged or device removed")

    def _disconnect(self, status_text: str | None = None):
        self._serial_handler.clear_link_lost_callback()
        # Call serial disconnection
        self._serial_handler.stop()
        self._connected = False
        time.sleep(0.5)  # ← give Windows time to release the port

        # Update UI
        self._connect_btn.setText("Connect")
        self._connect_btn.setChecked(False)
        self._status_label.setText(status_text or "⬤  Disconnected")
        self._status_label.setStyleSheet(f"color: {COLOUR_RED};")

        # Emit pyqt Signal
        self.serial_connection_state.emit(False)

    # ──────────────────────────────────────────────────────
    # Parameter Callbacks
    # ──────────────────────────────────────────────────────

    def _on_param_changed(self):

        has_any = any(
            row.has_pending()
            for row in self._param_rows.values()
        )

        self._save_btn.setEnabled(has_any)
        self._discard_btn.setEnabled(has_any)

    def _on_save(self):


        # Iterate through writable motor parameters
        for param in get_parameters(group="motor", access="w"):

            row = self._param_rows[param.name]

            if row.has_pending():
                if self._serial_handler: 
                    self._serial_handler.set(param.id, row.get_pending())
                row.confirm_save()

        self._save_btn.setEnabled(False)
        self._discard_btn.setEnabled(False)

    def _on_discard(self):

        for row in self._param_rows.values(): row.discard()

        self._save_btn.setEnabled(False)
        self._discard_btn.setEnabled(False)

    def _on_reset_all(self):

        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Reset all motor parameters to their default values?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for row in self._param_rows.values(): row.reset_to_default()