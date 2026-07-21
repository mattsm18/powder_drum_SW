#
# Title: gui/storage_tab.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Captures tab - lists internal recordings and stills allows user to replay videos, view images and copy to USB drive
#

from pathlib import Path

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QProgressBar, QPushButton, QGroupBox, QMessageBox, QAbstractItemView,
    QStackedWidget, QApplication, QDialog
)

from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget

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

    on_copy_to_usb_event = pyqtSignal(FileEntry)
    on_delete_event = pyqtSignal(FileEntry)

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
        QMessageBox.warning(self, "Storage Full", f"Not enough free space on {location}.")

    # UI CONSTRUCTION
    #--------------------------------------------------------------------------------------

    def _build_ui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self._build_internal_panel(), stretch=1)
        layout.addWidget(self._build_usb_panel(), stretch=1)

    #--------------------------------------------------------------------------------------

    def _build_internal_panel(self) -> QWidget:
        group = QGroupBox("Internal Recordings")
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

        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon("assets/icons/delete_icon.svg"))
        delete_btn.setIconSize(QSize(64, 48))
        
        self._copy_btn.setEnabled(False)

        view_btn.clicked.connect(lambda: self._open_selected(self._internal_list))
        self._copy_btn.clicked.connect(lambda: self._request_copy(self._internal_list))
        delete_btn.clicked.connect(lambda: self._request_delete(self._internal_list))

        button_row = QHBoxLayout()
        button_row.addWidget(view_btn)
        button_row.addWidget(self._copy_btn)
        button_row.addWidget(delete_btn)
        layout.addLayout(button_row)

        return group

    #--------------------------------------------------------------------------------------

    def _build_usb_panel(self) -> QWidget:
        group = QGroupBox("USB Drive")
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
        for entry in files:
            match entry.media_type:
                case MediaType.VIDEO: icon = "\U0001F3AC"  # clapper board
                case MediaType.STILL: icon = "\U0001F4F7"  # camera
                case _: icon = ""

            label = f"{icon}  {entry.path.name}   ({_format_bytes(entry.size_bytes)})"
            item = QListWidgetItem(label)
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

    def _show_image_preview(self, path: Path):
        pixmap = QPixmap(str(path))
        if pixmap.isNull(): return

        width, height = self._preview_size()

        dialog = QDialog(self)
        dialog.setWindowTitle(path.name)
        dialog.setModal(True)
        dialog.resize(width, height)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(dialog)

        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(pixmap.scaled(width, height,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
        layout.addWidget(image_label)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    #--------------------------------------------------------------------------------------

    def _show_video_preview(self, path: Path):
        width, height = self._preview_size()

        dialog = QDialog(self)
        dialog.setWindowTitle(path.name)
        dialog.setModal(True)
        dialog.resize(width, height)
        dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout(dialog)

        video_widget = QVideoWidget()
        layout.addWidget(video_widget)

        player = QMediaPlayer(dialog)
        audio_output = QAudioOutput(dialog)
        player.setAudioOutput(audio_output)
        player.setVideoOutput(video_widget)
        player.setSource(QUrl.fromLocalFile(str(path)))

        play_btn = QPushButton("Pause")
        close_btn = QPushButton("Close")

        def toggle_play():
            if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                player.pause()
                play_btn.setText("Play")
            else:
                player.play()
                play_btn.setText("Pause")

        def close_preview():
            player.stop()
            dialog.accept()

        play_btn.clicked.connect(toggle_play)
        close_btn.clicked.connect(close_preview)

        button_row = QHBoxLayout()
        button_row.addWidget(play_btn)
        button_row.addWidget(close_btn)
        layout.addLayout(button_row)

        player.play()
        dialog.exec()
        player.stop()

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

        confirm = QMessageBox.question(
            self, "Delete File", f"Delete {entry.path.name}? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            self.on_delete_event.emit(entry)

    #--------------------------------------------------------------------------------------