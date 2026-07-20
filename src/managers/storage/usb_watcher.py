#
# Title: managers/storage/usb_watcher.py
# Author: Matthew Smith 22173112
# Date: 20/07/26
# Purpose: Detect USB drive connect/disconnect and resolve mount paths

import time
import threading
from pathlib import Path
from typing import Callable, Optional

import pyudev
import psutil

class UsbWatcher():

    # CONSTRUCTOR
    #--------------------------------------------------------------------------------------

    def __init__(self, on_connect: Callable[[Path], None], on_disconnect: Callable[[], None], mount_timeout: float = 5.0, poll_interval: float = 0.2):

        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._mount_timeout = mount_timeout
        self._poll_interval = poll_interval

        self._context = pyudev.Context()
        self._monitor = pyudev.Monitor.from_netlink(self._context)
        self._monitor.filter_by(subsystem="block")
        self._observer = None
        self._connected_device_node = None

    # PUBLIC API
    #--------------------------------------------------------------------------------------

    def start(self):
        self._observer = pyudev.MonitorObserver(self._monitor, self._handle_event)
        self._observer.start()

    #--------------------------------------------------------------------------------------

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer = None

    # INTERNAL
    #--------------------------------------------------------------------------------------

    def _handle_event(self, action: str, device):
        
        # Only interested in partitions with a filesystem (skip raw disks, empty devices)
        if device.get("ID_FS_TYPE") is None: return
        if action == "add": self._handle_add(device)
        elif action == "remove": self._handle_remove(device)

    #--------------------------------------------------------------------------------------

    def _handle_add(self, device):
        device_node = device.device_node  # e.g. /dev/sda1
        if device_node is None: return

        mount_path = self._wait_for_mount(device_node)
        if mount_path is None: return  # never mounted within timeout, ignore

        self._connected_device_node = device_node
        self._on_connect(mount_path)

    #--------------------------------------------------------------------------------------

    def _handle_remove(self, device):
        device_node = device.device_node
        if device_node is None or device_node != self._connected_device_node: return

        self._connected_device_node = None
        self._on_disconnect()

    #--------------------------------------------------------------------------------------

    def _wait_for_mount(self, device_node: str) -> Optional[Path]:
        deadline = time.monotonic() + self._mount_timeout

        while time.monotonic() < deadline:
            for part in psutil.disk_partitions(all=False):
                if part.device == device_node:
                    return Path(part.mountpoint)
            time.sleep(self._poll_interval)

        return None