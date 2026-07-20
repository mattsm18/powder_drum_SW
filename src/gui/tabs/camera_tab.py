# gui/tabs/camera_tab.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSlider, QCheckBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

from models.camera_model import CameraSetting

class CameraTab(QWidget):

    # Outbound Signals
    camera_setting_changed = pyqtSignal(CameraSetting, object)

    def __init__(self):

        super().__init__()
        self.build_ui()
        
    def build_ui(self):
        # Camera feed preview
        self.preview = QLabel()

        layout = QVBoxLayout(self)
        layout.addWidget(self.preview)


    # GUI Updates
    def set_preview(self, frame):

        h, w, channels = frame.shape
        image = QImage(frame.data,w, h, w * channels, QImage.Format.Format_BGR888)
        self.preview.setPixmap(QPixmap.fromImage(image))

    def set_connected(self, state): pass

    