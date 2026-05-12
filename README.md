# powder_drum_SW

### Software for ENME891 - Industrial Project

# About

ENME891 is the capstone paper for the BE(Hons) degree at AUT. It is a year-long industrial project where students develop a real-world engineering solution.

### Project name: 
<b>Quanitfying the flowability of milk powders through the use of computer vision </b>

### Project members / responsibilities:
- Matthew Smith -> Embedded Firmware and Software Development, Electronic Design, on-device computer vision development
- Josh Russell -> Mechanical design and build, MATLAB Computer vision models

# Target
### Raspberry Pi 5 -> 16 GB RAM
- Global Shutter Camera
- 7-inch Touchscreen

# Key Functionality
### High level Spec:
- Provide and intuitve GUI so end users (Researchers) can ensure consistent expirimental results and validate results during data collection
- Connect with Microcontroller and facilitate bi-directional comms over UART to[ powder_drum_FW ](https://github.com/mattsm18/powder_drum_FW)
- Control Global Shutter Camera including recording, streaming and on-device Computer Vision to characterise milk powder flowability

### GUI Tabs:
#### Camera Tab  
- Control of camera settings
- Selection of Computer Vision Methods for characterising milk powder flowability
- Recording and Image Capture Feature to save footage to a USB Drive
- File playback and modification

#### Control Tab
- Control of physical I/O
- Motor target speed control -> Both motor and drum speeds
- Stop button
- LED Backlight control
- Graph of realtime motor angular velocity against setpoint and ramped targets

#### Config Tab
- Connection to Microcontroller over UART (Serial)
- Motor control parameters (Acceleration, PI Controller Gains, Filter settings)
- Vision Configuration
- Video Streaming Configuration

# Custom Serial Comms Protocol
The powder drum implements a custom bi-directional serial comms protocol in 
the firmware and the software

This protocol includes ACKs, NACKs and a XOR CRC checksum to validate data integrity on the wire.

Fully implemented in the firmware, some work still to do for ACK and NACK handling in the software.

![alt text](https://github.com/mattsm18/powder_drum_SW/blob/master/docs/serial_protocol.png "Custom Serial Protocol")
