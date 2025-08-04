#!/bin/bash

echo "🚁 Drone Height Controller for Raspberry Pi"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "⚠️  Warning: This script is optimized for Raspberry Pi"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Update system
    sudo apt update -y
    
    # Install system packages
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
    
    # Install Python packages
    pip3 install --upgrade pip
    pip3 install numpy opencv-python-headless Pillow
    
    # Try to install PiCamera2
    pip3 install picamera2
    
    echo "✅ Dependencies installed"
}

# Function to test camera
test_camera() {
    echo "📷 Testing camera..."
    
    if command -v raspistill &> /dev/null; then
        echo "Testing Pi Camera..."
        raspistill -o test_camera.jpg -t 1000
        if [ -f "test_camera.jpg" ]; then
            echo "✅ Camera test successful"
            rm test_camera.jpg
            return 0
        else
            echo "❌ Camera test failed"
            return 1
        fi
    else
        echo "⚠️  raspistill not found, skipping camera test"
        return 0
    fi
}

# Function to test Python installation
test_python() {
    echo "🐍 Testing Python installation..."
    
    python3 -c "import cv2; print('✅ OpenCV version:', cv2.__version__)" || return 1
    python3 -c "import numpy; print('✅ NumPy version:', numpy.__version__)" || return 1
    
    python3 -c "
try:
    from picamera2 import Picamera2
    print('✅ PiCamera2 installed successfully')
except ImportError:
    print('⚠️  PiCamera2 not available, will use OpenCV camera')
"
    
    return 0
}

# Function to run the controller
run_controller() {
    echo "🚁 Starting Drone Height Controller..."
    echo ""
    
    # Check if script exists
    if [ ! -f "drone_height_controller.py" ]; then
        echo "❌ Error: drone_height_controller.py not found"
        echo "Please make sure the script is in the current directory"
        exit 1
    fi
    
    # Make script executable
    chmod +x drone_height_controller.py
    
    # Run the controller
    python3 drone_height_controller.py
}

# Main execution
main() {
    # Check if dependencies are already installed
    if ! python3 -c "import cv2" 2>/dev/null; then
        echo "🔧 First time setup detected..."
        install_dependencies
    else
        echo "✅ Dependencies already installed"
    fi
    
    # Test camera
    if ! test_camera; then
        echo "⚠️  Camera test failed, but continuing..."
    fi
    
    # Test Python
    if ! test_python; then
        echo "❌ Python test failed"
        exit 1
    fi
    
    echo ""
    echo "🎯 Ready to run!"
    echo "The controller will provide real-time height commands for your drone."
    echo "Commands are saved to 'drone_height_commands.json'"
    echo ""
    
    # Run the controller
    run_controller
}

# Run main function
main 