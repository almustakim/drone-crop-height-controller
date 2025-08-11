# MAVLink Height Integration for Crop Quality Analysis

## 🎯 **Your Target Achieved!**

This system provides exactly what you requested:
- ✅ **Get height from drone** via MAVLink
- ✅ **Check image/footage quality** using computer vision
- ✅ **Detect crops** using color analysis and contour detection
- ✅ **Predict drone positioning** needs (closer/farther) based on quality

## 🚁 **How It Works**

### 1. **MAVLink Height Integration**
```python
# Connects to your drone via MAVLink
height_monitor = MAVLinkHeightMonitor("udpin:localhost:14550")
height_monitor.connect()  # Gets real-time height data
current_height = height_monitor.get_current_height()  # In meters
```

### 2. **Real-Time Quality Analysis**
- **Brightness**: Detects if image is too dark/bright
- **Sharpness**: Identifies blurry images (critical for crop analysis)
- **Contrast**: Ensures proper image contrast
- **Green Coverage**: Measures crop field coverage
- **Texture**: Analyzes crop detail level
- **Noise**: Detects image artifacts

### 3. **Crop Detection**
- **Color-based detection** for wheat, corn, rice, cotton, soybean
- **Contour analysis** to identify crop boundaries
- **Coverage calculation** to measure field density

### 4. **Drone Positioning Recommendations**
```python
# Automatic recommendations based on analysis:
if "Blurry" in analysis["sharpness"]:
    return "DESCEND_1.0m"  # Move closer for sharper images

if "Too Dark" in analysis["brightness"]:
    return "DESCEND_0.75m"  # Move closer for better lighting

if "Too high" in height_feedback:
    return "DESCEND_0.5m"   # Reduce altitude
```

## 🖥️ **Display Features**

The system shows on your live video feed:
- **Current Height**: Real-time drone altitude
- **Optimal Height**: Recommended height for your crop type
- **Height Status**: Too high/low/optimal
- **Quality Score**: Overall image quality (0-100)
- **Crop Detection**: Detected crops with coverage percentages
- **DRONE COMMANDS**: Specific actions like "DESCEND_1.0m"

## 🚀 **Quick Start**

### **On Raspberry Pi:**

1. **Run setup script:**
   ```bash
   chmod +x setup_pi_mavlink.sh
   ./setup_pi_mavlink.sh
   ```

2. **Start the analyzer:**
   ```bash
   ./run_mavlink_analyzer.sh
   ```

### **On PC/Mac (for testing):**

1. **Install dependencies:**
   ```bash
   pip install opencv-python numpy Pillow pymavlink
   ```

2. **Run the analyzer:**
   ```bash
   python3 mavlink_height_analyzer.py
   ```

## 🔧 **MAVLink Connection**

### **Connection String Options:**
```python
# USB connection to flight controller
"serial:/dev/ttyUSB0:115200"

# UDP connection (most common)
"udpin:localhost:14550"

# TCP connection
"tcpin:localhost:5760"

# Serial connection on Pi
"serial:/dev/ttyAMA0:57600"
```

### **Enable MAVLink on Your Drone:**
1. **ArduPilot**: Set `SERIAL1_PROTOCOL = 2` (MAVLink2)
2. **PX4**: Set `MAV_1_CONFIG = 101` (MAVLink)
3. **Mission Planner**: Enable MAVLink forwarding

## 📊 **Quality Analysis Process**

```
Frame Capture → Convert to HSV → Analyze Metrics → Generate Scores → 
Height Integration → Position Recommendations → Display Commands
```

### **Quality Thresholds:**
- **Excellent**: 80-100 (optimal for crop analysis)
- **Good**: 60-79 (acceptable for monitoring)
- **Poor**: <60 (needs immediate adjustment)

## 🎮 **Controls**

- **'q'**: Quit analysis
- **'s'**: Save current frame with analysis data
- **'h'**: Show height information in terminal

## 📁 **Output Files**

### **Saved Frames:**
```
crop_analysis_20241201_143022_h3.5_q85.2.jpg
```
- Includes height, quality score, and crop detection data

### **Analysis Logs:**
```
crop_quality_analysis_20241201_143022.json
```
- Complete analysis data for drone control systems

## 🔍 **Troubleshooting**

### **MAVLink Connection Issues:**
```bash
# Test MAVLink connection
python3 -c "from pymavlink import mavutil; print('MAVLink OK')"

# Check if port is open
netstat -an | grep 14550

# Test with MAVLink tools
mavlink-routerd -e 192.168.1.255:14550 -e 127.0.0.1:14551 /dev/ttyUSB0:115200
```

### **Camera Issues:**
```bash
# List available cameras
ls /dev/video*

# Test camera
v4l2-ctl --list-devices

# Check camera permissions
sudo usermod -a -G video $USER
```

### **Performance Issues:**
```bash
# Monitor CPU usage
htop

# Check memory
free -h

# Monitor temperature
vcgencmd measure_temp
```

## 📈 **Customization**

### **Change Crop Type:**
```python
analyzer = CropFieldQualityAnalyzer(
    crop_type="corn",  # wheat, corn, rice, cotton, soybean
    weather_condition="cloudy"  # clear, cloudy, overcast, sunny
)
```

### **Adjust Height Parameters:**
```python
# In imgquality.py, modify crop parameters:
"corn": {
    "optimal_height": 4.0,      # Optimal height in meters
    "height_tolerance": 0.8,    # Acceptable height range
    "min_resolution": 0.8       # Minimum resolution in cm/pixel
}
```

### **Modify Quality Thresholds:**
```python
# Adjust brightness, contrast, sharpness thresholds
self.thresholds = {
    "brightness": {"min": 50, "max": 200, "optimal": 120},
    "sharpness": {"min": 60, "optimal": 120}
}
```

## 🎯 **Integration with Drone Control**

The system generates commands that can be sent to your drone:

```python
# Example commands generated:
"DESCEND_1.0m"      # Move closer for blurry images
"ASCEND_0.5m"       # Move farther for overexposed images
"MAINTAIN_POSITION"  # Optimal quality achieved
```

### **Send to Drone:**
```python
# Integrate with your drone control system
if "DESCEND" in drone_commands:
    altitude_change = float(drone_commands.split('_')[1].replace('m', ''))
    drone.set_altitude(drone.get_altitude() - altitude_change)
```

## 🔒 **Security Notes**

- **Network Security**: MAVLink runs on UDP - ensure network security
- **Camera Access**: Camera permissions required on Raspberry Pi
- **File Permissions**: Analysis logs may contain sensitive data

## 📞 **Support**

If you encounter issues:
1. Check the terminal output for error messages
2. Verify MAVLink connection with `mavlink-routerd`
3. Test camera with `v4l2-ctl`
4. Check system resources with `htop` and `free -h`

## 🎉 **Ready to Use!**

Your system is now complete with:
- ✅ Real-time MAVLink height monitoring
- ✅ Advanced image quality analysis
- ✅ Automatic crop detection
- ✅ Intelligent drone positioning recommendations
- ✅ Raspberry Pi optimization
- ✅ Professional display interface

**Run it and start getting perfect crop footage!** 🌾📸 