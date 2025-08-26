# Drone Height & Footage Quality Monitor

Simple script that monitors drone altitude and camera footage quality, providing recommendations for drone movement.

## Features
- Reads altitude from Pixhawk via MAVLink
- Analyzes camera footage quality (brightness + sharpness)
- Provides simple up/down recommendations

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Connect camera to Raspberry Pi
3. Connect Pixhawk to `/dev/ttyAMA0` (hardware UART)

## Usage
```bash
python3 pi_mavlink_quality.py
```

## Output
The script continuously outputs:
- Current height in meters
- Footage quality score (0-100)
- Movement recommendation (up/down)

## Requirements
- Raspberry Pi with camera
- Pixhawk flight controller
- MAVLink connection
