#!/bin/bash
echo "🚀 Installing AI-Enhanced Crop Quality Analysis for Raspberry Pi"
echo "================================================================"

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt-get install -y python3-pip python3-opencv python3-numpy python3-pil

# Install Python packages
echo "🐍 Installing Python packages..."
pip3 install --user tflite-runtime requests pillow

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x imgquality.py
chmod +x download_models.py

echo ""
echo "✅ Installation completed!"
echo ""
echo "🚀 To run the analysis:"
echo "   python3 imgquality.py"
echo ""
echo "📥 To download AI models (optional):"
echo "   python3 download_models.py"
echo ""
echo "💡 Note: If TensorFlow Lite is not available, the system will"
echo "   automatically use traditional OpenCV methods."
