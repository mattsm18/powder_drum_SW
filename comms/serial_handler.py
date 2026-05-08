# 
# Title: comms/serial_handler.py
# Author: GenAi + Matthew Smith 22173112
# Date: 6/05/26
# Purpose: 
# - Class that runs on its own thread to handle serial comms with arduino
# - Sits on top of protocol.py which handles the specific implementation

import serial
import threading
from comms.protocol import *

class SerialHandler:
    def __init__(self):
        self._callbacks = {}
        self._running   = False
        self._thread    = None
        self._serial    = None
        self._port      = None
        self._baud      = None

    def connect(self, port: str, baud: int = 115200):
        self._port = port
        self._baud = baud
        self._thread = None
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
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.5)
        self._thread = None
        if self._serial:
            self._serial.close()
            self._serial = None  # ← release the port fully
            
    def on_parameter(self, parameter_id: int, callback):
        self._callbacks[parameter_id] = callback

    def get(self, parameter_id: int):
        if self.is_connected():
            self._serial.write(build_get(parameter_id))

    def set(self, parameter_id: int, value: float):
        if self.is_connected():
            self._serial.write(build_set(parameter_id, value))

    def _run(self):

        buffer = bytes()
        while self._running:
            if not self._serial or not self._serial.is_open:
                break
            data = self._serial.read(self._serial.in_waiting or 1)

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