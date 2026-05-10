#
# QObject bridge: serial worker thread signals link loss; Qt delivers on GUI thread.

from PyQt6.QtCore import QObject, pyqtSignal


class SerialLinkNotifier(QObject):
    link_lost = pyqtSignal()
