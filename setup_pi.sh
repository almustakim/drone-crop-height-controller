#!/bin/bash

echo "Raspberry Pi Crop Quality Analysis Setup"
echo "========================================"

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "Warning: This script is designed for Raspberry Pi"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
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
    gfortran \
    python3-setuptools \
    python3-wheel

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install numpy opencv-python-headless Pillow

# Try to install PiCamera2
echo "Installing PiCamera2..."
pip3 install picamera2

# Create directories
echo "Creating directories..."
mkdir -p quality_frames
mkdir -p output

# Set permissions
echo "Setting permissions..."
chmod +x imgquality_pi.py
chmod +x drone_integration_example.py

# Test camera
echo "Testing camera..."
if command -v raspistill &> /dev/null; then
    echo "Testing Pi Camera..."
    raspistill -o test_camera.jpg -t 1000
    if [ -f "test_camera.jpg" ]; then
        echo "✓ Camera test successful"
        rm test_camera.jpg
    else
        echo "✗ Camera test failed"
    fi
else
    echo "raspistill not found, skipping camera test"
fi

# Test Python installation
echo "Testing Python installation..."
python3 -c "import cv2; print('✓ OpenCV version:', cv2.__version__)"
python3 -c "import numpy; print('✓ NumPy version:', numpy.__version__)"

# Try to import PiCamera2
python3 -c "
try:
    from picamera2 import Picamera2
    print('✓ PiCamera2 installed successfully')
except ImportError:
    print('✗ PiCamera2 not available, will use OpenCV camera')
"

echo ""
echo "Setup completed!"
echo "================"
echo "To run the analysis:"
echo "  python3 imgquality_pi.py"
echo ""
echo "To run the drone integration example:"
echo "  python3 drone_integration_example.py"
echo ""
echo "Files created:"
echo "  - imgquality_pi.py (Pi Camera optimized version)"
echo "  - quality_frames/ (directory for saved frames)"
echo "  - output/ (directory for analysis logs)"
echo ""
echo "Configuration:"
echo "  - Edit config.json to customize settings"
echo "  - Edit pi_config.json for Pi-specific settings" 