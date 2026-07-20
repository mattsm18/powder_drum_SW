#
# Title: application/app.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Central Application, Ties Apps to GUI

# General Imports
from pathlib import Path

# Application Imports
from application.camera.camera_app import CameraApp

# GUI Imports
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

class Application:

    def __init__(self):

        # APPLICATION INSTANTIATION
        self.camera_app = CameraApp()

        # GUI INSTANTIATION
        self.window = MainWindow()
        self._wire_camera()

    def start(self):
        self.camera_app.connect()
        self.window.showFullScreen()

    def _wire_camera(self):
        self.camera_app.new_frame.connect(self.window.camera_tab.set_preview)
        self.camera_app.new_frame.connect(self.window.settings_tab.set_preview)
        self.window.camera_tab.camera_setting_changed.connect(self.camera_app.set_camera_setting)
        self.window.settings_tab.camera_setting_changed.connect(self.camera_app.set_camera_setting)
        

