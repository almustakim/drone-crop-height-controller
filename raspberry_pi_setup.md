# Raspberry Pi Setup Guide for Crop Quality Analysis

## Prerequisites
- Raspberry Pi (3B+, 4B, or newer recommended)
- Pi Camera Module (v1, v2, or HQ)
- MicroSD card with Raspberry Pi OS (Bullseye or newer)
- Internet connection for installation

## Step 1: System Setup

### 1.1 Update Raspberry Pi OS
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 1.2 Enable Camera Interface
```bash
sudo raspi-config
```
Navigate to: **Interface Options** → **Camera** → **Enable** → **Finish**

### 1.3 Test Camera
```bash
# Test camera capture
raspistill -o test.jpg

# Test camera video
raspistill -t 5000 -o test_video.jpg
```

## Step 2: Install Dependencies

### 2.1 Install System Dependencies
```bash
# Install required system packages
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libatlas-base-dev \
    libjasper-dev \
    libqtcore4 \
    libqtgui4 \
    libqt4-test \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    python3-setuptools \
    python3-wheel
```

### 2.2 Install Python Dependencies
```bash
# Install Python packages
pip3 install --upgrade pip
pip3 install numpy opencv-python-headless Pillow

# Alternative: Install from requirements.txt
pip3 install -r requirements.txt
```

### 2.3 Verify Installation
```bash
# Test OpenCV installation
python3 -c "import cv2; print('OpenCV version:', cv2.__version__)"
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"
```

## Step 3: Pi Camera Integration

### 3.1 Install PiCamera Library
```bash
pip3 install picamera2
```

### 3.2 Create Pi Camera Version
Create a new file `imgquality_pi.py` with Pi Camera integration:

```python
#!/usr/bin/env python3
"""
Raspberry Pi Camera version of Crop Field Quality Analysis
Optimized for Pi Camera with better performance
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os
from picamera2 import Picamera2
from picamera2.encoders import JpegEncoder
from picamera2.outputs import FileOutput

# Import the main analyzer class
from imgquality import CropFieldQualityAnalyzer

class PiCameraQualityAnalyzer:
    def __init__(self, crop_type="general", weather_condition="clear"):
        self.analyzer = CropFieldQualityAnalyzer(crop_type, weather_condition)
        self.picam2 = None
        self.setup_camera()
        
    def setup_camera(self):
        """Setup Pi Camera with optimal settings for crop analysis"""
        self.picam2 = Picamera2()
        
        # Configure camera for crop analysis
        config = self.picam2.create_preview_configuration(
            main={"size": (1920, 1080), "format": "RGB888"},
            controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
        )
        
        self.picam2.configure(config)
        self.picam2.start()
        
        # Wait for camera to start
        time.sleep(2)
        
    def capture_frame(self):
        """Capture a frame from Pi Camera"""
        try:
            frame = self.picam2.capture_array()
            return frame
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def run_analysis(self, duration_minutes=30):
        """Run continuous analysis for specified duration"""
        print(f"Starting crop quality analysis for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    continue
                
                # Analyze frame quality
                analysis = self.analyzer.analyze_frame_quality(frame)
                feedback, priority, adjustments = self.analyzer.get_drone_position_feedback(analysis)
                quality_score = self.analyzer.calculate_overall_quality_score(analysis)
                
                # Log analysis
                log_entry = self.analyzer.log_analysis(analysis, feedback, priority, quality_score)
                
                # Display results
                self.display_results(frame, analysis, feedback, priority, quality_score)
                
                # Print console output
                print(f"Quality: {quality_score:.1f}/100 | Priority: {priority} | {feedback[0] if feedback else 'Optimal'}")
                
                # Save frame if quality is good
                if quality_score > 80:
                    self.save_quality_frame(frame, quality_score)
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nAnalysis stopped by user")
        finally:
            self.cleanup()
    
    def display_results(self, frame, analysis, feedback, priority, quality_score):
        """Display analysis results on frame"""
        # Create overlay for better visibility
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (400, 280), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display quality score prominently
        color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
        cv2.putText(frame, f"Quality: {quality_score:.1f}/100", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Display priority
        priority_color = (0, 255, 0) if priority == 0 else (0, 255, 255) if priority <= 2 else (0, 0, 255)
        cv2.putText(frame, f"Priority: {priority}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
        
        # Display key metrics
        y_pos = 90
        for metric, (status, value) in analysis.items():
            if metric in ["brightness", "contrast", "sharpness", "green_coverage"]:
                color = (0, 255, 0) if "Good" in status or "Optimal" in status else (0, 0, 255)
                cv2.putText(frame, f"{metric.title()}: {status} ({value:.1f})", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_pos += 25
        
        # Display feedback
        y_pos += 10
        for i, msg in enumerate(feedback[:2]):  # Show first 2 feedback messages
            cv2.putText(frame, msg, (10, y_pos + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show the frame
        cv2.imshow("Crop Quality Analysis - Pi Camera", frame)
        cv2.waitKey(1)
    
    def save_quality_frame(self, frame, quality_score):
        """Save high-quality frames"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quality_frame_{timestamp}_score_{quality_score:.1f}.jpg"
        
        # Create output directory if it doesn't exist
        os.makedirs("quality_frames", exist_ok=True)
        filepath = os.path.join("quality_frames", filename)
        
        cv2.imwrite(filepath, frame)
        print(f"Saved quality frame: {filepath}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.picam2:
            self.picam2.stop()
        cv2.destroyAllWindows()

def main():
    """Main function for Pi Camera analysis"""
    print("Raspberry Pi Crop Quality Analysis")
    print("=" * 40)
    
    # Get user input
    crop_type = input("Enter crop type (wheat/corn/rice/cotton/general): ").lower() or "general"
    weather = input("Enter weather condition (clear/cloudy/overcast/sunny/rainy): ").lower() or "clear"
    duration = input("Enter analysis duration in minutes (default 30): ") or "30"
    
    try:
        duration = int(duration)
    except ValueError:
        duration = 30
    
    # Initialize analyzer
    analyzer = PiCameraQualityAnalyzer(crop_type, weather)
    
    # Run analysis
    analyzer.run_analysis(duration)

if __name__ == "__main__":
    main()
```

## Step 4: Performance Optimization

### 4.1 Create Performance Configuration
Create `pi_config.json`:

```json
{
  "camera_settings": {
    "resolution": [1280, 720],
    "fps": 15,
    "quality": 85
  },
  "analysis_settings": {
    "analysis_interval": 2,
    "save_interval": 5,
    "quality_threshold": 70
  },
  "system_settings": {
    "enable_gpu": false,
    "cpu_cores": 2,
    "memory_limit": "512MB"
  }
}
```

### 4.2 Optimize System Performance
```bash
# Increase GPU memory split (if using GPU)
sudo raspi-config
# Navigate to: Performance Options → GPU Memory → 128

# Disable unnecessary services
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon

# Optimize CPU governor
echo 'GOVERNOR="performance"' | sudo tee -a /etc/default/cpufrequtils
```

## Step 5: Running the Script

### 5.1 Basic Run
```bash
# Navigate to your project directory
cd /path/to/your/project

# Run the Pi Camera version
python3 imgquality_pi.py
```

### 5.2 Run as Service (Optional)
Create service file `/etc/systemd/system/crop-analysis.service`:

```ini
[Unit]
Description=Crop Quality Analysis Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/crop-analysis
ExecStart=/usr/bin/python3 /home/pi/crop-analysis/imgquality_pi.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl enable crop-analysis.service
sudo systemctl start crop-analysis.service
sudo systemctl status crop-analysis.service
```

## Step 6: Monitoring and Logs

### 6.1 View Logs
```bash
# View service logs
sudo journalctl -u crop-analysis.service -f

# View analysis logs
tail -f crop_quality_analysis_*.json
```

### 6.2 Monitor System Resources
```bash
# Monitor CPU and memory
htop

# Monitor disk space
df -h

# Monitor temperature
vcgencmd measure_temp
```

## Step 7: Troubleshooting

### 7.1 Common Issues

**Camera not detected:**
```bash
# Check camera status
vcgencmd get_camera

# Test camera
raspistill -o test.jpg
```

**Low performance:**
```bash
# Check CPU usage
top

# Reduce resolution in pi_config.json
# Increase analysis_interval
```

**Memory issues:**
```bash
# Check memory usage
free -h

# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 7.2 Performance Tips

1. **Reduce resolution** if performance is slow
2. **Increase analysis interval** to reduce CPU load
3. **Use SSD** instead of SD card for better I/O
4. **Add cooling** to prevent thermal throttling
5. **Overclock carefully** if needed

## Step 8: Integration with Drone Control

### 8.1 Create Drone Control Interface
The script generates JSON logs that can be read by your drone control system:

```python
# Example: Read analysis results
import json
import glob

def get_latest_analysis():
    files = glob.glob("crop_quality_analysis_*.json")
    if files:
        latest = max(files, key=os.path.getctime)
        with open(latest, 'r') as f:
            return json.load(f)
    return None
```

### 8.2 Network Integration
For remote monitoring, you can add network capabilities:

```bash
# Install web server for remote monitoring
sudo apt-get install nginx
sudo apt-get install python3-flask

# Create web interface for monitoring
# (See additional files for web interface)
```

## Step 9: Automation

### 9.1 Create Startup Script
Create `start_analysis.sh`:

```bash
#!/bin/bash
cd /home/pi/crop-analysis
python3 imgquality_pi.py >> analysis.log 2>&1
```

Make executable:
```bash
chmod +x start_analysis.sh
```

### 9.2 Add to Startup
```bash
# Add to crontab for auto-start
crontab -e
# Add line: @reboot /home/pi/crop-analysis/start_analysis.sh
```

## Summary

1. **Install dependencies** and enable camera
2. **Test camera** functionality
3. **Run the script** with your crop type and weather conditions
4. **Monitor performance** and adjust settings as needed
5. **Integrate with drone control** system using JSON outputs
6. **Automate** for continuous operation

The script will now run efficiently on your Raspberry Pi and provide real-time crop quality analysis for your drone monitoring system! 