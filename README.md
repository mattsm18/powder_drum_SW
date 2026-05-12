# powder_drum_SW

### Software for ENME891 - Industrial Project

## Target
- Raspberry Pi 5 -> 16 GB RAM
- Global Shutter Camera
- 7-inch Touchscreen

## Key Functionality
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

## Custom Serial Comms Protocol
![alt text](https://github.com/mattsm18/powder_drum_SW/blob/master/docs/serial_protocol.png "Custom Serial Protocol")

## Authorship

- Developed by Matthew Smith 22173112 
