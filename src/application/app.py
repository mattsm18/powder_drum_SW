#
# Title: application/app.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Central Application, Ties Apps to GUI
# Functions as an EVENT -> FUNCTION map
#
# e.g Event on_start_recording_event (called by camera_tab UI)
#     Function start_recording       (listened to by camera_app APPLICATION logic)

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
        self.camera_app = CameraApp(storage_path=self.storage_app.get_storage_path)

        # GUI INSTANTIATION
        self.window = MainWindow()
        self._wire_camera()
        self._wire_storage()

    def start(self):
        self.camera_app.connect()
        self.window.showFullScreen()

    def _wire_camera(self):
        
        ### APP ---> UI ###
        self.camera_app.on_new_frame.                       connect(self.window.camera_tab.update_frame)
        self.camera_app.on_new_frame.                       connect(self.window.settings_tab.update_frame)
        self.camera_app.on_recording_stopped.               connect(self.storage_app.refresh_internal_storage)
        self.camera_app.on_photo_taken.                     connect(self.storage_app.refresh_internal_storage)
        
        ### UI ---> APP ###
        self.window.camera_tab.on_setting_change_event.     connect(self.camera_app.set_camera_setting)
        self.window.camera_tab.on_start_recording_event.    connect(self.camera_app.start_recording)
        self.window.camera_tab.on_stop_recording_event.     connect(self.camera_app.stop_recording)
        self.window.camera_tab.on_start_streaming_event.    connect(self.camera_app.start_streaming)
        self.window.camera_tab.on_stop_streaming_event.     connect(self.camera_app.stop_streaming)
        self.window.camera_tab.on_take_photo_event.         connect(self.camera_app.take_photo)

        self.window.settings_tab.on_setting_change_event.   connect(self.camera_app.set_camera_setting)
        

    def _wire_storage(self):
    
        ### APP ---> UI ###
        self.storage_app.on_internal_storage_updated.   connect(self.window.storage_tab.set_internal_files)
        self.storage_app.on_internal_size_updated.      connect(self.window.storage_tab.set_internal_size)
        self.storage_app.on_usb_connected.              connect(self.window.storage_tab.set_usb_files)
        self.storage_app.on_usb_disconnected.           connect(self.window.storage_tab.clear_usb_files)
        self.storage_app.on_usb_size_updated.           connect(self.window.storage_tab.set_usb_size)
        self.storage_app.on_storage_full.               connect(self.window.storage_tab.show_storage_full)

        ### UI ---> APP ###
        self.window.storage_tab.on_copy_to_usb_event.   connect(self.storage_app.copy_to_usb)
        self.window.storage_tab.on_delete_event.        connect(self.storage_app.delete_file)
    
        self.storage_app.refresh_internal_storage()