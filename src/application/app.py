#
# Title: application/app.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Central Application, Ties Apps to GUI

# General Imports
from pathlib import Path

# Application Imports
from application.camera.camera_app import CameraApp
from application.storage.storage_app import StorageApp

# GUI Imports
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

class Application:

    def __init__(self):

        # APPLICATION INSTANTIATION
        self.storage_app = StorageApp()
        self.camera_app = CameraApp(get_recording_path=self.storage_app.get_recording_path)

        # GUI INSTANTIATION
        self.window = MainWindow()
        self._wire_camera()
        self._wire_storage()

    def start(self):
        self.camera_app.connect()
        self.window.showFullScreen()

    def _wire_camera(self):
        self.camera_app.new_frame.connect(self.window.camera_tab.set_preview)
        self.camera_app.new_frame.connect(self.window.settings_tab.set_preview)
        self.window.camera_tab.camera_setting_changed.connect(self.camera_app.set_camera_setting)
        self.window.settings_tab.camera_setting_changed.connect(self.camera_app.set_camera_setting)
        self.window.camera_tab.record_requested.connect(self.camera_app.start_recording)
        self.window.camera_tab.stop_requested.connect(self.camera_app.stop_recording)
        self.camera_app.recording_started.connect(self.window.camera_tab.set_recording_state)
        self.camera_app.recording_stopped.connect(self.window.camera_tab.set_idle_state)
        self.camera_app.recording_stopped.connect(self.storage_app.refresh_internal)
        #self.camera_app.storage_full.connect(self.window.show_storage_full_warning)

    def _wire_storage(self):
        self.storage_app.internal_updated.connect(self.window.camera_tab.set_internal_files)
        self.storage_app.usb_connected.connect(self.window.camera_tab.set_usb_connected)
        self.storage_app.usb_disconnected.connect(self.window.camera_tab.set_usb_disconnected)
        #self.storage_app.storage_full.connect(self.window.show_storage_full_warning)
        self.window.camera_tab.copy_requested.connect(self.storage_app.copy_to_usb)
        self.window.camera_tab.delete_requested.connect(self.storage_app.delete_file)