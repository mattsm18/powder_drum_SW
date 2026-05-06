# tests/test_protocol.py
from comms.protocol import *

def test_build_get():
    packet = build_get(0x01)
    assert packet[0] == SOF
    assert packet[2] == MsgID.MSG_CMD_GET
    assert packet[5] == 0x01  # parameter_id

def test_build_set():
    packet = build_set(0x01, 30.0)
    _, value = parse_float_payload(packet[5:-1])
    assert abs(value - 30.0) < 0.001

def test_crc():
    packet = build_get(0x00)
    assert compute_crc(packet[:-1]) == packet[-1]

def test_roundtrip():
    raw    = build_set(0x01, 45.5)
    parsed = parse_packet(raw)
    assert parsed is not None
    assert parsed.msg_id == MsgID.MSG_CMD_SET
    _, value = parse_float_payload(parsed.payload)
    assert abs(value - 45.5) < 0.001