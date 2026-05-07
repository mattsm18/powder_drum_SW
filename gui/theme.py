#
# Title: gui/theme.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: Centralised dark theme for 800x480 touchscreen

DARK_THEME = """
    QMainWindow, QWidget {
        background-color: #1A1A1A;
        color: #E0E0E0;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }

    /* Tab bar */
    QTabWidget::pane {
        border: none;
        background-color: #1A1A1A;
    }
    QTabBar::tab {
        background-color: #2A2A2A;
        color: #AAAAAA;
        padding: 10px 24px;
        font-size: 14px;
        border: none;
        min-width: 218px;
    }
    QTabBar::tab:selected {
        background-color: #1A1A1A;
        color: #FFFFFF;
        border-bottom: 3px solid #00AAFF;
    }
    QTabBar::tab:hover {
        background-color: #333333;
        color: #FFFFFF;
    }

    /* Buttons */
    QPushButton {
        background-color: #2A2A2A;
        color: #E0E0E0;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 10px 16px;
        font-size: 13px;
        min-height: 48px;
        min-width: 48px;
    }
    QPushButton:pressed {
        background-color: #00AAFF;
        color: #FFFFFF;
    }
    QPushButton:checked {
        background-color: #005588;
        color: #FFFFFF;
        border: 1px solid #00AAFF;
    }

    /* Sliders */
    QSlider::groove:horizontal {
        height: 8px;
        background-color: #333333;
        border-radius: 4px;
    }
    QSlider::handle:horizontal {
        background-color: #00AAFF;
        width: 28px;
        height: 28px;
        margin: -10px 0;
        border-radius: 14px;
    }
    QSlider::sub-page:horizontal {
        background-color: #00AAFF;
        border-radius: 4px;
    }

    /* Labels */
    QLabel {
        color: #E0E0E0;
    }

    /* Line edit */
    QLineEdit {
        background-color: #2A2A2A;
        color: #E0E0E0;
        border: 1px solid #444444;
        border-radius: 6px;
        padding: 8px;
        font-size: 14px;
        min-height: 40px;
    }
    QLineEdit:focus {
        border: 1px solid #00AAFF;
    }

    /* List widget */
    QListWidget {
        background-color: #2A2A2A;
        border: 1px solid #444444;
        border-radius: 6px;
        color: #E0E0E0;
        font-size: 13px;
    }
    QListWidget::item {
        padding: 10px;
        min-height: 44px;
    }
    QListWidget::item:selected {
        background-color: #005588;
        color: #FFFFFF;
    }

    /* Scroll bars */
    QScrollBar:vertical {
        background-color: #2A2A2A;
        width: 12px;
        border-radius: 6px;
    }
    QScrollBar::handle:vertical {
        background-color: #555555;
        border-radius: 6px;
        min-height: 40px;
    }

    /* Separators */
    QFrame[frameShape="4"],
    QFrame[frameShape="5"] {
        color: #333333;
    }
"""

# Colour tokens for use in Python code
COLOUR_GREEN    = "#00FF88"
COLOUR_BLUE     = "#00AAFF"
COLOUR_RED      = "#FF4444"
COLOUR_ORANGE   = "#FF8800"
COLOUR_BG       = "#1A1A1A"
COLOUR_SURFACE  = "#2A2A2A"
COLOUR_BORDER   = "#444444"
COLOUR_TEXT     = "#E0E0E0"
COLOUR_MUTED    = "#AAAAAA"