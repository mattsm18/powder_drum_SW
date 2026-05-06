#
# Title: comms/protocol.py
# Author: Matthew Smith 22173112
# Date: 6/05/26
# Purpose: 
# - Handle low level protocol implementation for Serial comms with Arduino Nano

import struct
from enum import IntEnum
from dataclasses import dataclass

### Data Representation
#######################
class MsgID(IntEnum):
    MSG_CMD_SET     = 0x01
    MSG_CMD_GET     = 0x02
    MSG_STATUS      = 0x10
    MSG_ACK         = 0xEE
    MSG_NACK        = 0xEF
    MSG_HEARTBEAT   = 0xFF

class NackError(IntEnum):
    ERR_VERSION_MISMATCH    = 0x01
    ERR_BAD_CRC             = 0x02
    ERR_UNKNOWN_MSG         = 0x03
    ERR_BAD_LEN             = 0x04

@dataclass
class Packet:
    msg_id:     int
    dir:        int
    payload:    bytes

### Constants
#################
PROTOCOL_VERSION    = 0x01
SOF                 = 0xAA
DIR_PC_TO_MCU       = 0x01
DIR_MCU_TO_PC       = 0x02

### Helpers / Calculation
#########################
def compute_crc(data: bytes) -> int:
    crc = 0x00
    for b in data: crc ^= b
    return crc

### Builders 
################

def build_packet(msg_id: int, direction: int, payload: bytes) -> bytes:
    header = bytes([SOF, PROTOCOL_VERSION, msg_id, direction, len(payload)])
    crc    = compute_crc(header + payload)
    return header + payload + bytes([crc])

def build_get(parameter_id: int) -> bytes:
    return build_packet(MsgID.MSG_CMD_GET, DIR_PC_TO_MCU, bytes([parameter_id]))

def build_set(parameter_id: int, value: float) -> bytes:

    # Build payload with value as IEEE 754 Float (Little-Endian <f)
    payload = bytes([parameter_id]) + struct.pack('<f', value)
    return build_packet(MsgID.MSG_CMD_SET, DIR_PC_TO_MCU, payload)

### Parsing
###########

def parse_packet(data: bytes) -> Packet | None:

    # Throw on edge case
    if len(data) < 6:               return None
    if data[0] != SOF:              return None
    if data[1] != PROTOCOL_VERSION: return None

    # Get each component in data frame
    msg_id      = data[2]
    dir         = data[3]
    length      = data[4]
    payload     = data[5:5 + length]
    crc         = data[5 + length]

    # Check CRC while parsing packet
    if compute_crc(data[:5 + length]) != crc: return None

    return Packet(msg_id=msg_id, dir=dir, payload=payload)

def parse_float_payload(payload: bytes) -> tuple[int, float]:
    parameter_id = payload[0]
    value        = struct.unpack('<f', payload[1:5])[0]
    return parameter_id, value