# 🚁 Height Integration Guide for Image Quality Analyzer

This guide shows you how to get current height/distance data and integrate it with the image quality analysis system.

## 📏 **How to Get Current Height**

### **1. DJI Drone SDK (Recommended for DJI drones)**

```python
from djitellopy import Tello
from imgquality import CropFieldQualityAnalyzer

# Initialize drone
drone = Tello()
drone.connect()

# Initialize analyzer
analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")

# Get height in real-time
while True:
    try:
        # Get height from drone (in cm, convert to meters)
        height_cm = drone.get_height()
        height_m = height_cm / 100
        
        # Update analyzer with current height
        analyzer.update_drone_height(height_m)
        
        # Get height feedback
        feedback = analyzer.get_height_feedback()
        print(f"Height: {height_m:.1f}m - {feedback}")
        
        time.sleep(1)  # Update every second
        
    except Exception as e:
        print(f"Height reading error: {e}")
        break

drone.land()
```

### **2. ArduPilot/MAVLink (For custom drones)**

```python
from pymavlink import mavutil
from imgquality import CropFieldQualityAnalyzer

# Connect to ArduPilot
connection = mavutil.mavlink_connection('udpin:0.0.0.0:14550')

# Initialize analyzer
analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")

# Get height in real-time
while True:
    try:
        # Get altitude message
        msg = connection.recv_match(type='GLOBAL_POSITION_INT')
        if msg:
            # Altitude in mm, convert to meters
            height_mm = msg.alt
            height_m = height_mm / 1000
            
            # Update analyzer
            analyzer.update_drone_height(height_m)
            
            # Get height feedback
            feedback = analyzer.get_height_feedback()
            print(f"Height: {height_m:.1f}m - {feedback}")
        
        time.sleep(0.1)  # Update every 100ms
        
    except Exception as e:
        print(f"Height reading error: {e}")
        break
```

### **3. Custom Height Sensor (For DIY drones)**

```python
import serial
from imgquality import CropFieldQualityAnalyzer

# Initialize serial connection to height sensor
ser = serial.Serial('/dev/ttyUSB0', 9600)  # Adjust port and baud rate

# Initialize analyzer
analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")

# Read height from sensor
while True:
    try:
        # Read from sensor (example: ultrasonic, lidar, barometer)
        if ser.in_waiting:
            height_data = ser.readline().decode().strip()
            height_m = float(height_data)
            
            # Update analyzer
            analyzer.update_drone_height(height_m)
            
            # Get height feedback
            feedback = analyzer.get_height_feedback()
            print(f"Height: {height_m:.1f}m - {feedback}")
        
        time.sleep(0.1)
        
    except Exception as e:
        print(f"Height reading error: {e}")
        break

ser.close()
```

### **4. Raspberry Pi with Ultrasonic Sensor**

```python
import RPi.GPIO as GPIO
import time
from imgquality import CropFieldQualityAnalyzer

# GPIO setup for ultrasonic sensor
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    """Get distance from ultrasonic sensor"""
    GPIO.output(TRIG, False)
    time.sleep(0.1)
    
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150  # Speed of sound
    distance = round(distance, 2)
    
    return distance / 100  # Convert cm to meters

# Initialize analyzer
analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")

# Continuous height monitoring
try:
    while True:
        height_m = get_distance()
        
        # Update analyzer
        analyzer.update_drone_height(height_m)
        
        # Get height feedback
        feedback = analyzer.get_height_feedback()
        print(f"Height: {height_m:.1f}m - {feedback}")
        
        time.sleep(1)
        
except KeyboardInterrupt:
    GPIO.cleanup()
```

## 🔧 **Integration with Main System**

### **Real-time Height Monitoring**

```python
from imgquality import CropFieldQualityAnalyzer
import cv2

# Initialize analyzer with height monitoring
analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")

# Initialize camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Update height from your drone/sensor (example)
    current_height = get_height_from_drone()  # Your height function
    analyzer.update_drone_height(current_height)
    
    # Analyze frame quality
    analysis = analyzer.analyze_frame_quality(frame)
    
    # Get drone positioning feedback (now includes height)
    feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
    
    # Calculate quality score
    quality_score = analyzer.calculate_overall_quality_score(analysis)
    
    # Display results with height information
    display_results(frame, analysis, feedback, priority, quality_score, analyzer)
    
    cv2.imshow("Crop Analysis with Height", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 📊 **Height-Based Features**

### **1. Automatic Height Recommendations**
- **Too Low**: Increase altitude for better coverage
- **Too High**: Decrease altitude for better detail
- **Optimal**: Maintain current height

### **2. Height-Aware Quality Scoring**
- Height deviations affect overall quality score
- Priority adjustments based on height issues
- Crop-specific optimal height enforcement

### **3. Smart Drone Control**
- Height-specific adjustment commands
- Priority-based height corrections
- Real-time height monitoring display

## 🎯 **Crop-Specific Optimal Heights**

| Crop Type | Optimal Height | Tolerance | Reason |
|-----------|----------------|-----------|---------|
| **Wheat** | 3.0m | ±0.5m | High detail sensitivity |
| **Corn** | 4.0m | ±0.8m | Larger plants, medium detail |
| **Rice** | 2.5m | ±0.4m | Dense planting, high detail |
| **Cotton** | 3.5m | ±0.6m | Medium detail, fiber focus |
| **General** | 3.0m | ±0.5m | Balanced approach |

## 🚨 **Troubleshooting Height Issues**

### **Common Problems:**

1. **Height Not Updating**
   ```python
   # Check if height is being received
   print(f"Raw height data: {height_data}")
   print(f"Converted height: {height_m}")
   ```

2. **Incorrect Height Values**
   ```python
   # Validate height range
   if 0 < height_m < 100:  # Reasonable range
       analyzer.update_drone_height(height_m)
   else:
       print(f"Invalid height: {height_m}m")
   ```

3. **Height Sensor Errors**
   ```python
   # Add error handling
   try:
       height_m = get_height_from_sensor()
       analyzer.update_drone_height(height_m)
   except Exception as e:
       print(f"Height sensor error: {e}")
       # Use last known height or default
   ```

## 📱 **Mobile/Web Integration**

### **Height Data API**
```python
from flask import Flask, jsonify
from imgquality import CropFieldQualityAnalyzer

app = Flask(__name__)
analyzer = CropFieldQualityAnalyzer(crop_type="wheat")

@app.route('/height/update/<float:height>')
def update_height(height):
    analyzer.update_drone_height(height)
    feedback = analyzer.get_height_feedback()
    return jsonify({
        'height': height,
        'feedback': feedback,
        'optimal_height': analyzer.crop_params['optimal_height']
    })

@app.route('/height/status')
def height_status():
    return jsonify({
        'current_height': analyzer.drone_height,
        'optimal_height': analyzer.crop_params['optimal_height'],
        'feedback': analyzer.get_height_feedback(),
        'recommendation': analyzer.get_height_recommendation()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 🎉 **Summary**

The system now provides:

✅ **Real-time height monitoring** from any drone/sensor  
✅ **Height-based quality optimization**  
✅ **Precise altitude recommendations**  
✅ **Height-aware drone control commands**  
✅ **Crop-specific optimal height enforcement**  
✅ **Priority-based height corrections**  

**To get started:**
1. Choose your height data source (DJI SDK, MAVLink, custom sensor)
2. Use the integration examples above
3. Run the height demo: `python3 height_demo.py`
4. Integrate with your main system

The height integration makes your crop monitoring much more precise and automated! 🚁🌾 