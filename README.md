# Clean Image Quality Analysis for Crop Monitoring

A simple, efficient image quality analysis system for drone-based crop field monitoring, designed to work on both desktop computers and Raspberry Pi devices.

## ✨ Features

### 🎯 **Crop-Specific Analysis**
- **Multiple crop types**: Wheat, corn, rice, cotton, and general
- **Dynamic thresholds**: Automatically adjusts based on crop characteristics
- **Optimal height recommendations**: Crop-specific altitude suggestions

### 🌤️ **Weather Adaptation**
- **Weather condition detection**: Clear, cloudy, overcast, sunny
- **Dynamic threshold adjustment**: Adapts analysis parameters to lighting conditions
- **Real-time optimization**: Continuously adjusts for changing weather

### 📊 **Comprehensive Quality Metrics**
- **Brightness analysis**: Optimal exposure for crop detail visibility
- **Contrast evaluation**: Ensures sufficient detail differentiation
- **Sharpness detection**: Multiple methods (Laplacian + Sobel) for crop detail
- **Crop coverage analysis**: Green pixel ratio for field focus
- **Texture variance**: Important for disease detection
- **Focus analysis**: Frequency domain analysis for optimal focus
- **Noise assessment**: Image noise level evaluation
- **Crop health analysis**: Color-based health assessment

### 🚁 **Precise Drone Control Recommendations**
- **Priority-based feedback**: 0-3 priority levels for efficient adjustments
- **Specific altitude changes**: Exact meter adjustments needed
- **Action commands**: Ready-to-use drone control instructions
- **JSON output**: Structured data for drone control system integration

### 📈 **Quality Scoring System**
- **Overall quality score**: 0-100 weighted scoring
- **Real-time monitoring**: Live quality assessment
- **Historical tracking**: Quality trend analysis

## 🖥️ **Compatibility**

- **Desktop Computers**: Windows, macOS, Linux
- **Raspberry Pi**: Pi 3, Pi 4, Pi Zero (with camera module)
- **Python**: 3.7 or higher
- **Camera**: USB webcam, Pi Camera, or any OpenCV-compatible camera

## 📋 **Requirements**

- Python 3.7 or higher
- OpenCV 4.5.0+
- NumPy 1.21.0+
- Pillow 8.0.0+

## 🛠️ **Installation**

### Quick Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the analyzer
python imgquality.py
```

### Raspberry Pi Setup
```bash
# On Raspberry Pi
sudo apt-get update
sudo apt-get install python3-opencv python3-pip
pip3 install -r requirements.txt

# Run with Pi Camera
python3 imgquality.py
```

## 🎯 **Usage**

### Basic Usage
```python
from imgquality import CropFieldQualityAnalyzer

# Initialize analyzer
analyzer = CropFieldQualityAnalyzer(
    crop_type="wheat",
    weather_condition="clear"
)

# Analyze frame quality
analysis = analyzer.analyze_frame_quality(frame)

# Get drone positioning feedback
feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)

# Calculate overall quality score
quality_score = analyzer.calculate_overall_quality_score(analysis)
```

### Command Line Usage
```bash
# Run with default settings
python imgquality.py

# Run with specific crop type
python imgquality.py --crop wheat --weather cloudy
```

## 🔧 **Configuration**

### Crop Types
Each crop type has optimized parameters:

- **Wheat**: High detail sensitivity, optimal at 3.0m height
- **Corn**: Medium sensitivity, optimal at 4.0m height  
- **Rice**: High detail sensitivity, optimal at 2.5m height
- **Cotton**: Medium sensitivity, optimal at 3.5m height

### Weather Conditions
- **Clear**: Standard thresholds
- **Cloudy**: Reduced brightness, increased contrast
- **Overcast**: Further reduced brightness, increased contrast
- **Sunny**: Increased brightness, reduced contrast

## 📊 **Output Format**

### Analysis Results
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "frame_count": 150,
  "crop_type": "wheat",
  "weather_condition": "clear",
  "quality_score": 85.5,
  "priority": 1,
  "analysis": {
    "brightness": ["Optimal Brightness", 125.3],
    "contrast": ["Good Contrast", 45.2],
    "sharpness": ["Good Sharpness", 120.8],
    "green_coverage": ["Good Crop Coverage", 0.65],
    "crop_health": ["Excellent Health", 0.85]
  },
  "feedback": [
    "Decrease altitude by 0.5-1.0m for better crop detail detection"
  ]
}
```

### Drone Control Commands
- **Priority 0**: Maintain position (optimal quality)
- **Priority 1**: Fine-tune adjustments (minor issues)
- **Priority 2**: Gradual adjustments (moderate issues)
- **Priority 3**: Immediate adjustments (critical issues)

## 🎮 **Drone Integration**

The system generates structured JSON output that can be easily integrated with your drone control system:

1. **Read analysis logs**: Parse JSON files for quality data
2. **Execute commands**: Use generated drone control commands
3. **Monitor quality**: Track quality scores over time
4. **Optimize flight paths**: Use priority system for efficient navigation

## 📁 **File Structure**

```
ImgQuality/
├── imgquality.py              # Main analyzer
├── requirements.txt           # Dependencies
├── README.md                 # This file
└── venv/                     # Virtual environment (optional)
```

## 🚨 **Troubleshooting**

### Common Issues

1. **Camera not detected**
   ```bash
   # Check camera index
   ls /dev/video*
   # Adjust camera index in code if needed
   ```

2. **Low quality scores**
   - Adjust thresholds in configuration
   - Check lighting conditions
   - Verify camera focus

3. **Performance issues on Pi**
   - Reduce frame resolution
   - Increase frame skip interval
   - Monitor CPU temperature

### Raspberry Pi Optimization

- Use Pi Camera Module for better performance
- Monitor temperature: `vcgencmd measure_temp`
- Consider using a heatsink for extended operation
- Use `sudo raspi-config` to enable camera interface

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- **OpenCV** for computer vision capabilities
- **NumPy** for numerical computing
- **Pillow** for image processing

---

**Note**: This system is designed to be lightweight and efficient, making it suitable for both desktop and embedded applications like Raspberry Pi. 