# 
# Title: comms/serial_handler.py
# Author: GenAi + Matthew Smith 22173112
# Date: 6/05/26
# Purpose: 
# - Class that runs on its own thread to handle serial comms with arduino
# - Sits on top of protocol.py which handles the specific implementation

import serial
import threading
from typing import Callable, Optional

from comms.protocol import *

class SerialHandler:
    def __init__(self):
        self._callbacks = {}
        self._running   = False
        self._thread    = None
        self._serial    = None
        self._port      = None
        self._baud      = None
        self._link_lost_cb: Optional[Callable[[], None]] = None
        self._user_stop = False
        self._failure_lock = threading.Lock()
        self._failure_reported = False

    def connect(self, port: str, baud: int = 115200):
        self._port = port
        self._baud = baud
        self._thread = None
        self._user_stop = False
        with self._failure_lock:
            self._failure_reported = False
        self._serial = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=0.1,
            dsrdtr=False,
            rtscts=False
        )
        self._serial.dtr = False

    def start(self):
        if not self._serial or not self._serial.is_open:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def stop(self):
        self._user_stop = True
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        self._thread = None
        if self._serial:
            try:
                self._serial.close()
            except (serial.SerialException, OSError):
                pass
            self._serial = None
        self._user_stop = False

    def set_link_lost_callback(self, callback: Optional[Callable[[], None]]):
        self._link_lost_cb = callback

    def clear_link_lost_callback(self):
        self._link_lost_cb = None

    def on_parameter(self, parameter_id: int, callback):
        self._callbacks[parameter_id] = callback

    def get(self, parameter_id: int):
        if not self.is_connected():
            return
        try:
            self._serial.write(build_get(parameter_id))
        except (serial.SerialException, OSError, ValueError):
            self._on_transport_failed()

    def set(self, parameter_id: int, value: float):
        if not self.is_connected():
            return
        try:
            self._serial.write(build_set(parameter_id, value))
        except (serial.SerialException, OSError, ValueError):
            self._on_transport_failed()

    def _on_transport_failed(self):
        if self._user_stop:
            return
        with self._failure_lock:
            if self._failure_reported:
                return
            self._failure_reported = True

        self._running = False
        if self._serial:
            try:
                self._serial.close()
            except (serial.SerialException, OSError):
                pass
            self._serial = None

        t = self._thread
        if t is not None and threading.current_thread() is not t and t.is_alive():
            t.join(timeout=1.0)

        cb = self._link_lost_cb
        if cb:
            cb()

    def _run(self):

        buffer = bytes()
        while self._running:
            if not self._serial or not self._serial.is_open:
                break
            try:
                data = self._serial.read(self._serial.in_waiting or 1)
            except (serial.SerialException, OSError):
                self._on_transport_failed()
                break

            ## debug
            #if data: print(f"RAW: {data.hex(' ').upper()}")

            buffer += data
            packet, buffer = self._try_parse(buffer)
            if packet:
                self._dispatch(packet)

    def _try_parse(self, buffer: bytes):
        # Hunt for SOF
        sof = buffer.find(SOF)
        if sof == -1:
            return None, bytes()
        buffer = buffer[sof:]

        if len(buffer) < 6: return None, buffer
        length = buffer[4]
        if len(buffer) < 6 + length: return None, buffer

        packet = parse_packet(buffer[:6 + length])
        return packet, buffer[6 + length:]

    def _dispatch(self, packet: Packet):
        if packet.msg_id == MsgID.MSG_CMD_GET:
            parameter_id, value = parse_float_payload(packet.payload)
            if parameter_id in self._callbacks:
                self._callbacks[parameter_id](parameter_id, value)