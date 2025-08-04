# Crop Field Quality Analysis for Drone Monitoring

This script provides advanced image quality analysis for drone-based crop field monitoring, specifically designed to optimize footage quality for disease detection and crop health assessment.

## Features

### 🎯 **Crop-Specific Analysis**
- **Multiple crop types**: Wheat, corn, rice, cotton, soybeans, and general
- **Dynamic thresholds**: Automatically adjusts based on crop characteristics
- **Optimal height recommendations**: Crop-specific altitude suggestions

### 🌤️ **Weather Adaptation**
- **Weather condition detection**: Clear, cloudy, overcast, sunny, rainy
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

### 🚁 **Precise Drone Control Recommendations**
- **Priority-based feedback**: 0-3 priority levels for efficient adjustments
- **Specific altitude changes**: Exact meter adjustments needed
- **Action commands**: Ready-to-use drone control instructions
- **JSON output**: Structured data for drone control system integration

### 📈 **Quality Scoring System**
- **Overall quality score**: 0-100 weighted scoring
- **Real-time monitoring**: Live quality assessment
- **Historical tracking**: Quality trend analysis

## Installation

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **For Raspberry Pi with Pi Camera**:
```bash
sudo apt-get update
sudo apt-get install python3-opencv
sudo apt-get install libatlas-base-dev
```

## Usage

### Basic Usage
```bash
python imgquality.py
```

### Advanced Usage with Configuration
```python
from imgquality import CropFieldQualityAnalyzer

# Initialize with specific crop and weather
analyzer = CropFieldQualityAnalyzer(
    crop_type="wheat", 
    weather_condition="cloudy"
)

# Analyze a frame
analysis = analyzer.analyze_frame_quality(frame)
feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
quality_score = analyzer.calculate_overall_quality_score(analysis)
```

### Configuration File
Edit `config.json` to customize:
- Camera settings
- Crop type parameters
- Weather conditions
- Drone control preferences
- Output settings

## Key Improvements

### 1. **Enhanced Sharpness Analysis**
- **Combined methods**: Laplacian variance + Sobel edge detection
- **Crop-specific sensitivity**: Different thresholds for different crops
- **Frequency domain analysis**: FFT-based focus assessment

### 2. **Intelligent Drone Positioning**
- **Precise altitude recommendations**: Exact meter adjustments
- **Priority-based system**: Efficient flight path optimization
- **Weather-aware adjustments**: Dynamic recommendations based on conditions

### 3. **Crop-Specific Optimization**
- **Green range adaptation**: Different color ranges for different crops
- **Texture sensitivity**: Crop-specific detail detection
- **Optimal height mapping**: Crop-specific altitude recommendations

### 4. **Weather Condition Adaptation**
- **Dynamic thresholds**: Automatic adjustment for lighting conditions
- **Multiple weather types**: Clear, cloudy, overcast, sunny, rainy
- **Real-time optimization**: Continuous parameter adjustment

### 5. **Integration-Ready Output**
- **JSON logging**: Structured data for drone control systems
- **Command generation**: Ready-to-use drone instructions
- **Priority system**: Efficient decision making

## Output Format

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
    "brightness": ("Optimal Brightness", 125.3),
    "contrast": ("Good Contrast", 45.2),
    "sharpness": ("Good Sharpness", 120.8),
    "green_coverage": ("Good Crop Coverage", 0.65),
    "texture_variance": ("Good Texture Detail", 85.4),
    "focus": ("Good Focus", 12.3),
    "noise": ("Low Noise", 3.2)
  },
  "feedback": [
    "Decrease altitude by 0.5-1.0m for better crop detail detection"
  ],
  "recommendations": {
    "priority": 1,
    "actions": [
      {
        "command": "gradual_adjustment",
        "reason": "Moderate quality issues"
      }
    ]
  }
}
```

### Drone Control Commands
- **Priority 0**: Maintain position (optimal quality)
- **Priority 1**: Fine-tune adjustments (minor issues)
- **Priority 2**: Gradual adjustments (moderate issues)
- **Priority 3**: Immediate adjustments (critical issues)

## Integration with Drone Control System

The script generates structured JSON output that can be easily integrated with your drone control system:

1. **Read analysis logs**: Parse JSON files for quality data
2. **Execute commands**: Use generated drone control commands
3. **Monitor quality**: Track quality scores over time
4. **Optimize flight paths**: Use priority system for efficient navigation

## Customization

### Adding New Crop Types
Edit `config.json` to add new crop types:
```json
"new_crop": {
  "green_range": [35, 50, 50, 85, 255, 255],
  "texture_sensitivity": 1.0,
  "detail_importance": "medium",
  "optimal_height": 3.0,
  "min_resolution": 0.5
}
```

### Adjusting Quality Thresholds
Modify thresholds in the configuration file based on your specific requirements and field conditions.

## Performance Optimization

- **Frame skipping**: Adjust `analysis_interval` in config
- **Resolution reduction**: Lower frame resolution for faster processing
- **Selective analysis**: Focus on specific quality metrics

## Troubleshooting

### Common Issues
1. **Camera not detected**: Check camera index in config
2. **Low quality scores**: Adjust thresholds for your specific conditions
3. **High noise levels**: Check camera settings and lighting

### Raspberry Pi Optimization
- Use `picamera` library for better Pi Camera integration
- Adjust frame resolution for performance
- Monitor CPU usage during operation

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements and bug fixes. 