#
# Title: gui/storage_tab.py
# Author: Matthew Smith 22173112
# Date: 21/07/26
# Purpose: Captures tab - lists internal recordings and stills allows user to replay videos, view images and copy to USB drive
#

from pathlib import Path
import cv2

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QPushButton, QGroupBox, QMessageBox, QAbstractItemView,
    QStackedWidget, QApplication, QDialog, QSlider, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QImage, QColor

from models.storage_model import FileEntry, MediaType


def _format_bytes(size: int) -> str:
    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1000 or unit == "TB":
            return f"{int(value)} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1000
    return f"{value:.1f} TB"


class StorageTab(QWidget):

    # EVENTS (UI ---> APP)
    #--------------------------------------------------------------------------------------

    on_copy_to_usb_event    = pyqtSignal(FileEntry)
    on_delete_event         = pyqtSignal(FileEntry)
    on_preview_opened_event = pyqtSignal()
    on_preview_closed_event = pyqtSignal()

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self):
        super().__init__()
        self._internal_files: list[FileEntry] = []
        self._usb_files: list[FileEntry] = []
        self._usb_is_connected = False
        self._build_ui()

    # PUBLIC API (slots, APP ---> UI)
    #--------------------------------------------------------------------------------------

    def set_internal_files(self, files: list[FileEntry]):
        self._internal_files = files
        self._populate_list(self._internal_list, files)

    #--------------------------------------------------------------------------------------

    def set_internal_size(self, used_bytes: int, quota_bytes: int):
        self._set_usage_bar(self._internal_usage_bar, self._internal_usage_label, used_bytes, quota_bytes)

    #--------------------------------------------------------------------------------------

    def set_usb_files(self, mount_path: Path, files: list[FileEntry]):
        self._usb_is_connected = True
        self._usb_files = files
        self._usb_stack.setCurrentWidget(self._usb_connected_widget)
        self._usb_mount_label.setText(f"USB Drive: {mount_path}")
        self._copy_btn.setEnabled(True)
        self._populate_list(self._usb_list, files)

    #--------------------------------------------------------------------------------------

    def set_usb_size(self, used_bytes: int, quota_bytes: int):
        self._set_usage_bar(self._usb_usage_bar, self._usb_usage_label, used_bytes, quota_bytes)

    #--------------------------------------------------------------------------------------

    def clear_usb_files(self):
        self._usb_is_connected = False
        self._usb_files = []
        self._usb_list.clear()
        self._copy_btn.setEnabled(False)
        self._usb_stack.setCurrentWidget(self._usb_disconnected_widget)

    #--------------------------------------------------------------------------------------

    def show_storage_full(self, which: str):
        location = "internal storage" if which == "internal" else "the USB drive"

        box = QMessageBox(self)
        box.setWindowTitle("Storage Full")
        box.setText(f"Not enough free space on {location}.")
        box.setIcon(QMessageBox.Icon.Warning)
        box.setStyleSheet("QMessageBox { border: 1px solid lightgray; }")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        box.exec()

    # UI CONSTRUCTION
    #--------------------------------------------------------------------------------------

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self._build_internal_panel(), stretch=1)
        layout.addWidget(self._build_usb_panel(), stretch=1)

    #--------------------------------------------------------------------------------------

    def _build_internal_panel(self) -> QWidget:
        group = QGroupBox("Internal Recordings")
        group.setStyleSheet("QGroupBox { font-size: 18px;font-weight: bold; }")
        layout = QVBoxLayout(group)

        self._internal_usage_label = QLabel("0 B / 0 B used")
        self._internal_usage_bar = QProgressBar()
        layout.addWidget(self._internal_usage_label)
        layout.addWidget(self._internal_usage_bar)

        self._internal_list = QListWidget()
        self._internal_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self._internal_list)

        view_btn = QPushButton()
        view_btn.setIcon(QIcon("assets/icons/view_icon.svg"))
        view_btn.setIconSize(QSize(64, 48))

        self._copy_btn = QPushButton()
        self._copy_btn.setIcon(QIcon("assets/icons/copy_icon.svg"))
        self._copy_btn.setIconSize(QSize(64, 48))
        self._copy_btn.setEnabled(False)

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("assets/icons/delete_icon.svg"))
        delete_btn.setIconSize(QSize(64, 48))

        view_btn.clicked.connect(lambda: self._open_selected(self._internal_list))
        self._copy_btn.clicked.connect(lambda: self._request_copy(self._internal_list))
        delete_btn.clicked.connect(lambda: self._request_delete(self._internal_list))

        button_row = QHBoxLayout()
        button_row.addWidget(view_btn)
        button_row.addWidget(delete_btn)
        button_row.addWidget(self._copy_btn)
        layout.addLayout(button_row)

        return group

    #--------------------------------------------------------------------------------------

    def _build_usb_panel(self) -> QWidget:
        group = QGroupBox("USB Drive")
        group.setStyleSheet("QGroupBox { font-size: 18px;font-weight: bold; }")
        outer_layout = QVBoxLayout(group)

        self._usb_stack = QStackedWidget()
        self._usb_disconnected_widget = self._build_usb_disconnected_widget()
        self._usb_connected_widget = self._build_usb_connected_widget()
        self._usb_stack.addWidget(self._usb_disconnected_widget)
        self._usb_stack.addWidget(self._usb_connected_widget)
        self._usb_stack.setCurrentWidget(self._usb_disconnected_widget)

        outer_layout.addWidget(self._usb_stack)
        return group

    #--------------------------------------------------------------------------------------

    def _build_usb_disconnected_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("No USB drive connected")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        layout.addWidget(label)
        layout.addStretch()
        return widget

    #--------------------------------------------------------------------------------------

    def _build_usb_connected_widget(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self._usb_mount_label = QLabel("USB Drive")
        layout.addWidget(self._usb_mount_label)

        self._usb_usage_label = QLabel("0 B / 0 B used")
        self._usb_usage_bar = QProgressBar()
        layout.addWidget(self._usb_usage_label)
        layout.addWidget(self._usb_usage_bar)

        self._usb_list = QListWidget()
        self._usb_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        layout.addWidget(self._usb_list)

        view_btn = QPushButton()
        view_btn.setIcon(QIcon("assets/icons/view_icon.svg"))
        view_btn.setIconSize(QSize(64, 48))

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("assets/icons/delete_icon.svg"))
        delete_btn.setIconSize(QSize(64, 48))

        view_btn.clicked.connect(lambda: self._open_selected(self._usb_list))
        delete_btn.clicked.connect(lambda: self._request_delete(self._usb_list))

        button_row = QHBoxLayout()
        button_row.addWidget(view_btn)
        button_row.addWidget(delete_btn)
        layout.addLayout(button_row)

        return widget

    # INTERNAL HELPERS
    #--------------------------------------------------------------------------------------

    def _populate_list(self, list_widget: QListWidget, files: list[FileEntry]):
        list_widget.clear()
        list_widget.setIconSize(QSize(32, 32))

        for entry in files:
            match entry.media_type:
                case MediaType.VIDEO: icon = QIcon("assets/icons/video_icon.svg")
                case MediaType.STILL: icon = QIcon("assets/icons/photo_icon.svg")
                case _: icon = QIcon()

            label = f"{entry.path.name}   ({_format_bytes(entry.size_bytes)})"
            item = QListWidgetItem(icon, label)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            list_widget.addItem(item)

    #--------------------------------------------------------------------------------------

    def _set_usage_bar(self, bar: QProgressBar, label: QLabel, used_bytes: int, quota_bytes: int):
        percent = int((used_bytes / quota_bytes) * 100) if quota_bytes else 0
        bar.setValue(min(percent, 100))
        label.setText(f"{_format_bytes(used_bytes)} / {_format_bytes(quota_bytes)} used")

    #--------------------------------------------------------------------------------------

    def _selected_entry(self, list_widget: QListWidget) -> FileEntry | None:
        item = list_widget.currentItem()
        if item is None: return None
        return item.data(Qt.ItemDataRole.UserRole)

    #--------------------------------------------------------------------------------------

    def _open_selected(self, list_widget: QListWidget):
        entry = self._selected_entry(list_widget)
        if entry is None: return

        match entry.media_type:
            case MediaType.STILL: self._show_image_preview(entry.path)
            case MediaType.VIDEO: self._show_video_preview(entry.path)

    #--------------------------------------------------------------------------------------

    def _preview_size(self) -> tuple[int, int]:
        parent_size = self.window().size()
        return int(parent_size.width() * 0.8), int(parent_size.height() * 0.8)

    #--------------------------------------------------------------------------------------

    def _apply_dialog_shadow(self, dialog: QDialog, margin: int = 24) -> QVBoxLayout:
        dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        outer_layout = QVBoxLayout(dialog)
        outer_layout.setContentsMargins(margin, margin, margin, margin)

        container = QWidget()
        container.setObjectName("previewContainer")
        container.setStyleSheet(
            """
            #previewContainer {
                background: #2f2f2f;
                border: 3px solid #555;
                border-radius: 16px;
            }
            QLabel, QPushButton {
                background: transparent;
                border: none;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect(container)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 160))
        container.setGraphicsEffect(shadow)

        outer_layout.addWidget(container)

        inner_layout = QVBoxLayout(container)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(0)

        return inner_layout

    #--------------------------------------------------------------------------------------

    def _build_preview_top_bar(self, dialog: QDialog, on_close) -> QHBoxLayout:

        title = QLabel(dialog.windowTitle())
        title.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 15px;
            font-weight: 600;
            padding-left: 14px;
        }
        """)

        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(8, 8, 8, 8)

        top_bar.addWidget(title)
        top_bar.addStretch()

        close_btn = QPushButton("\u2715")
        close_btn.setFixedSize(44, 44)
        close_btn.setStyleSheet(
            "QPushButton { border: none; font-size: 18px; }"
            "QPushButton:pressed { background: rgba(0, 0, 80, 80); }"
        )
        close_btn.clicked.connect(on_close)
        top_bar.addWidget(close_btn)

        return top_bar

    #--------------------------------------------------------------------------------------

    def _show_image_preview(self, path: Path):
        pixmap = QPixmap(str(path))
        if pixmap.isNull(): return

        width, height = self._preview_size()
        shadow_margin = 24
        top_bar_height = 44
        content_width = width - shadow_margin * 2
        content_height = height - top_bar_height - shadow_margin * 2

        dialog = QDialog(self)
        dialog.setWindowTitle(path.name)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        dialog.resize(width, height)

        layout = self._apply_dialog_shadow(dialog, shadow_margin)
        layout.addLayout(self._build_preview_top_bar(dialog, dialog.accept))

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(pixmap.scaled(
            content_width, content_height,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        image_label.setContentsMargins(12,20,12,20)
        layout.addWidget(image_label)

        dialog.exec()

    #--------------------------------------------------------------------------------------

    def _show_video_preview(self, path: Path):
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened(): return

        width, height = self._preview_size()

        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        interval = max(int(1000 / fps), 1)
        frame_count = max(int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), 1)

        dialog = QDialog(self)
        dialog.setWindowTitle(path.name)
        dialog.setModal(True)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        dialog.setFixedSize(width, height + 60)

        layout = self._apply_dialog_shadow(dialog, 24)
        layout.setSpacing(8)

        timer = QTimer(dialog)
        playing = True

        def close_preview():
            timer.stop()
            cap.release()
            dialog.accept()

        layout.addLayout(self._build_preview_top_bar(dialog, close_preview))

        video_width = width - 80
        video_height = height - 120

        video = QLabel()
        video.setFixedSize(video_width, video_height)
        video.setAlignment(Qt.AlignmentFlag.AlignCenter)
        video.setStyleSheet("""
            QLabel {
                background-color: #111;
                border-radius: 12px;
            }
        """)

        video_container = QHBoxLayout()
        video_container.addStretch()
        video_container.addWidget(video)
        video_container.addStretch()

        layout.addLayout(video_container)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, frame_count - 1)
        slider.setFixedWidth(width - 100)
        slider.setFixedHeight(40)
        slider.setContentsMargins(12,12,12,12)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #555;
                border-radius: 3px;
            }

            QSlider::sub-page:horizontal {
                background: #4A90E2;
                border-radius: 3px;
            }

            QSlider::handle:horizontal {
                width: 30px;
                height: 20px;
                margin: -10px 10;
                border-radius: 8px;
                background: white;
            }
        """)

        slider_container = QHBoxLayout()
        slider_container.setContentsMargins(0, 0, 20, 0)

        slider_container.addStretch()
        slider_container.addWidget(slider)
        slider_container.addStretch()

        layout.addLayout(slider_container)

        def display_frame(frame):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            h, w, _ = rgb.shape

            image = QImage(
                rgb.data,
                w,
                h,
                w * 3,
                QImage.Format.Format_RGB888
            ).copy()

            video.setPixmap(
                QPixmap.fromImage(image).scaled(
                    video.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        def next_frame():
            ok, frame = cap.read()

            if not ok:
                timer.stop()
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                slider.setValue(0)
                return

            display_frame(frame)

            slider.blockSignals(True)
            slider.setValue(int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1)
            slider.blockSignals(False)

        def toggle_play():
            nonlocal playing

            playing = not playing

            if playing:
                timer.start(interval)
            else:
                timer.stop()

        def seek(frame):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame)

            ok, img = cap.read()

            if ok:
                display_frame(img)

        timer.timeout.connect(next_frame)
        slider.sliderMoved.connect(seek)

        video.mousePressEvent = lambda _: toggle_play()

        timer.start(interval)

        self.on_preview_opened_event.emit()

        dialog.exec()

        timer.stop()
        cap.release()

        self.on_preview_closed_event.emit()

    #--------------------------------------------------------------------------------------

    def _request_copy(self, list_widget: QListWidget):
        if not self._usb_is_connected: return

        entry = self._selected_entry(list_widget)
        if entry is None: return

        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        try:
            self.on_copy_to_usb_event.emit(entry)
        finally:
            QApplication.restoreOverrideCursor()

    #--------------------------------------------------------------------------------------

    def _request_delete(self, list_widget: QListWidget):
        entry = self._selected_entry(list_widget)
        if entry is None: return

        box = QMessageBox(self)
        box.setWindowTitle("Delete File")
        box.setText(f"Delete {entry.path.name}? This cannot be undone.")
        box.setStyleSheet("QMessageBox { border: 3px solid lightgray; }")
        box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        box.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        if box.exec() == QMessageBox.StandardButton.Yes:
            self.on_delete_event.emit(entry)

    #--------------------------------------------------------------------------------------