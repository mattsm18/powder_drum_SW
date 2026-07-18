#
# Title: application/app.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Central Application, Ties Apps to GUI

# Application Imports
from application.camera.camera_app import CameraApp

# GUI Imports
from gui.main_window import MainWindow

class Application:

    def __init__(self):

        # APPLICATION INSTANTIATION
        self.camera_app = CameraApp()

        # GUI INSTANTIATION
        self.window = MainWindow()
        
        # CAMERA WIRING
        self.camera_app.new_frame.connect(self.window.camera_tab.set_preview)
        self.window.camera_tab.camera_setting_changed.connect(self.camera_app.set_camera_setting)

    def start(self):
        self.camera_app.connect()
        self.window.showFullScreen()

