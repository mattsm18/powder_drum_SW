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
    def __init__(self, port: str, baud: int = 115200):

        self._callbacks = {}   # parameter_id -> callable
        self._running   = False
        self._thread    = threading.Thread(target=self._run, daemon=True)

        self._serial = serial.Serial(
            port=port,
            baudrate=baud,
            timeout=0.1,
            dsrdtr=False,      # disable DSR/DTR
            rtscts=False       # disable RTS/CTS
        )

        self._serial.dtr = False  # prevent reset on connect

    def start(self):
        self._running = True
        self._thread.start()

    def stop(self):
        self._running = False
        self._serial.close()

    def on_parameter(self, parameter_id: int, callback):
        self._callbacks[parameter_id] = callback

    def get(self, parameter_id: int):
        self._serial.write(build_get(parameter_id))

    def set(self, parameter_id: int, value: float):
        self._serial.write(build_set(parameter_id, value))

    def _run(self):
        buffer = bytes()
        while self._running:
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