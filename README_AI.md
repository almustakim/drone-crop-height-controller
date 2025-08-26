# 🤖 AI-Enhanced Crop Quality Analysis

This enhanced version of the crop quality analysis system integrates **OpenCV** with **TensorFlow Lite** to provide intelligent crop detection and quality assessment.

## ✨ New Features

### 🧠 AI-Powered Analysis
- **Crop Detection**: Uses TensorFlow Lite models to identify and classify different crop types
- **Quality Assessment**: AI-based image quality evaluation for more accurate results
- **Smart Fallback**: Automatically falls back to traditional OpenCV methods if AI models aren't available

### 📊 Enhanced Visualization
- **Real-time Bounding Boxes**: Shows detected crops with confidence scores
- **AI Quality Metrics**: Displays AI-generated quality scores alongside traditional metrics
- **Improved UI**: Better visual feedback with emojis and status indicators

### 🚀 Performance Optimizations
- **Intelligent Caching**: AI results are cached to avoid repeated processing
- **Frame Skipping**: AI analysis runs every 5 frames for optimal performance
- **High-Resolution Support**: Optimized for 720p/1080p camera feeds

## 🛠️ Installation

### 1. Install Dependencies
```bash
pip install -r requirements_ai.txt
```

### 2. Setup AI Models (Optional)
```bash
python3 download_models.py
```

**Note**: If models aren't available, the system will automatically use traditional OpenCV methods.

### 3. Run the Analysis
```bash
python3 imgquality.py
```

## 🎯 How It Works

### Traditional Analysis (OpenCV)
- **Brightness Analysis**: Evaluates lighting conditions
- **Contrast Analysis**: Measures image contrast
- **Sharpness Analysis**: Detects blur and focus issues
- **Crop Coverage**: Analyzes green pixel distribution
- **Texture Analysis**: Evaluates crop detail levels
- **Noise Analysis**: Measures image noise

### AI-Enhanced Analysis (TensorFlow Lite)
- **Crop Detection**: Identifies specific crop types and locations
- **Quality Assessment**: AI-powered quality scoring
- **Disease Detection**: Enhanced crop health analysis
- **Smart Recommendations**: Intelligent positioning advice

## 📱 Controls

- **'q'**: Quit the application
- **'i'**: Show current analysis information
- **Mouse**: Interact with the video window

## 🔧 Configuration

### Crop Types
Supported crop types: `wheat`, `corn`, `rice`, `cotton`, `soybean`, `barley`, `oats`, `rye`, `sorghum`, `millet`

### Weather Conditions
Supported weather: `clear`, `cloudy`, `overcast`, `sunny`

### Example Usage
```python
analyzer = CropFieldQualityAnalyzer(
    crop_type="wheat",
    weather_condition="clear"
)
```

## 📊 Output Metrics

### Quality Score (0-100)
- **80-100**: Excellent quality
- **60-79**: Good quality  
- **40-59**: Moderate quality
- **0-39**: Poor quality

### AI Detection Results
- **Crop Type**: Identified crop species
- **Confidence**: Detection confidence (0-1)
- **Bounding Box**: Crop location coordinates
- **AI Quality**: AI-generated quality score

## 🚁 Drone Integration

When quality scores reach 70/100 or higher, the system automatically:
- Sends flight parameters to `flight_maneuvering.py`
- Provides positioning recommendations
- Logs analysis results for drone control

## 🔍 Troubleshooting

### AI Models Not Loading
- Check if TensorFlow is installed: `pip install tensorflow`
- Verify model files exist in the project directory
- The system will automatically use fallback methods

### Camera Issues
- Ensure webcam is connected and accessible
- Check camera permissions
- Try different camera indices (0, 1, 2)

### Performance Issues
- Reduce camera resolution in the code
- Increase frame skipping interval
- Use GPU acceleration if available

## 📁 File Structure

```
ImgQuality/
├── imgquality.py              # Main AI-enhanced analysis script
├── download_models.py         # Model download utility
├── requirements_ai.txt        # AI dependencies
├── README_AI.md              # This file
├── flight_maneuvering.py     # Drone control integration
└── models/                   # TensorFlow Lite models (optional)
```

## 🚀 Future Enhancements

- **Real-time Model Training**: Adapt models to specific crop fields
- **Multi-spectral Analysis**: Support for specialized camera sensors
- **Cloud Integration**: Upload results to cloud platforms
- **Mobile App**: Companion mobile application
- **API Endpoints**: REST API for integration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section
- Review the code comments
- Open an issue on GitHub

---

**Happy Crop Monitoring! 🌾🚁**
