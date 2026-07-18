# gui/tabs/camera_tab.py

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSlider, QCheckBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

class CameraTab(QWidget):

    # Outbound Signals
    exposure_changed = pyqtSignal(int)
    auto_exposure_changed = pyqtSignal(bool)

    def __init__(self):

        super().__init__()
        self.build_ui()
        
    def build_ui(self):
        # Camera feed preview
        self.preview = QLabel()

        # Exposure Slider
        self.exposure_slider = QSlider(Qt.Orientation.Horizontal)
        self.exposure_slider.setRange(100, 100000)
        self.exposure_slider.setValue(2000)
        self.exposure_slider.valueChanged.connect(self._on_exposure_changed)
        self.exposure_slider.setFixedHeight(60)

        # Auto Exposure checkbox
        self.auto_exposure_checkbox = QCheckBox("Auto Exposure")
        self.auto_exposure_checkbox.setChecked(True)
        self.auto_exposure_checkbox.stateChanged.connect(self._on_auto_exposure_changed)

        layout = QVBoxLayout(self)
        layout.addWidget(self.preview)
        layout.addWidget(self.exposure_slider)
        layout.addWidget(self.auto_exposure_checkbox)


    # GUI Updates
    def set_preview(self, frame):

        h, w, channels = frame.shape
        image = QImage(frame.data,w, h, w * channels, QImage.Format.Format_BGR888)
        self.preview.setPixmap(QPixmap.fromImage(image))

    def set_connected(self, state): pass

    def _on_exposure_changed(self, value): self.exposure_changed.emit(value)
    def _on_auto_exposure_changed(self, value): self.auto_exposure_changed.emit(value)
    