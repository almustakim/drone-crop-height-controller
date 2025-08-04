# 🚁 Drone Height Controller for Raspberry Pi

**Real-time height adjustment commands for crop field drone monitoring**

## 🎯 What This Does

- **Analyzes crop field footage** in real-time
- **Provides immediate height commands** for your drone
- **No video saving** - focuses only on height optimization
- **Generates JSON commands** for your drone control system

## 🚀 Quick Start (One Command)

```bash
# Make the script executable and run
chmod +x run_on_pi.sh
./run_on_pi.sh
```

That's it! The script will:
1. ✅ Install all dependencies automatically
2. ✅ Test your camera
3. ✅ Start the height controller
4. ✅ Generate commands in `drone_height_commands.json`

## 📋 Manual Setup (if needed)

### 1. Copy Files to Pi
```bash
# Copy these files to your Raspberry Pi:
# - drone_height_controller.py
# - run_on_pi.sh
# - read_drone_commands.py
```

### 2. Run Setup
```bash
chmod +x run_on_pi.sh
./run_on_pi.sh
```

### 3. Configure Camera (if needed)
```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
```

## 🎮 How to Use

### Start the Controller
```bash
python3 drone_height_controller.py
```

Enter:
- **Crop type**: wheat, corn, rice, cotton, or general
- **Weather**: clear, cloudy, overcast, sunny, or rainy
- **Duration**: minutes to run (default 30)

### Monitor Commands
```bash
# View latest command
python3 read_drone_commands.py latest

# Monitor commands in real-time
python3 read_drone_commands.py monitor

# View all commands
python3 read_drone_commands.py all
```

## 📊 Output Format

The controller generates commands like this:

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "frame_count": 150,
  "priority": 2,
  "current_height": 3.0,
  "target_height": 2.25,
  "height_change": -0.75,
  "reason": "Blurry - need sharper crop details",
  "quality_metrics": {
    "brightness": 125.3,
    "sharpness": 45.2,
    "green_coverage": 0.65
  },
  "crop_type": "wheat",
  "weather": "clear"
}
```

## 🎯 Priority Levels

- **Priority 0**: Maintain position (optimal quality)
- **Priority 1**: Fine-tune adjustment (minor issues)
- **Priority 2**: Moderate adjustment (quality issues)
- **Priority 3**: Immediate adjustment (critical issues)

## 🔧 Integration with Your Drone System

Your drone control script can read commands like this:

```python
import json

def get_drone_command():
    with open('drone_height_commands.json', 'r') as f:
        commands = json.load(f)
    return commands[-1] if commands else None

# Get latest command
command = get_drone_command()
if command:
    target_height = command['target_height']
    priority = command['priority']
    reason = command['reason']
    # Send to your drone control system
```

## 📁 Files Created

- `drone_height_commands.json` - Height commands for your drone
- `run_on_pi.sh` - One-command setup and run script
- `drone_height_controller.py` - Main controller script
- `read_drone_commands.py` - Command monitoring script

## 🛠️ Troubleshooting

### Camera Issues
```bash
# Test camera
raspistill -o test.jpg -t 1000

# Check camera status
vcgencmd get_camera
```

### Performance Issues
```bash
# Check system resources
htop

# Check temperature
vcgencmd measure_temp
```

### No Commands Generated
- Check if camera is working
- Verify crop type and weather settings
- Check file permissions

## 🎯 Example Commands

**Optimal Quality:**
```
Height: 3.0m → 3.0m (+0.0m) | Priority: 0 | Optimal quality - maintain position
```

**Need to Move Closer:**
```
Height: 3.0m → 2.25m (-0.75m) | Priority: 2 | Blurry - need sharper crop details
```

**Need to Move Higher:**
```
Height: 3.0m → 3.5m (+0.5m) | Priority: 2 | Too bright - reduce overexposure
```

## 🚀 That's It!

Your drone will now get real-time height commands to optimize crop field footage quality. The system automatically adjusts for different crops and weather conditions. 