#!/bin/bash

echo "🚁 Drone Height Controller for Raspberry Pi (USB Webcam)"
echo "======================================================"

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
    
    # Install system packages for webcam support
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
        python3-wheel \
        v4l-utils \
        fswebcam
    
    # Install Python packages
    pip3 install --upgrade pip
    pip3 install numpy opencv-python-headless Pillow
    
    echo "✅ Dependencies installed"
}

# Function to test webcam
test_webcam() {
    echo "📷 Testing webcam..."
    
    # Check if webcam is detected
    if ls /dev/video* 2>/dev/null; then
        echo "✅ Webcam devices found:"
        ls /dev/video*
        
        # Test webcam with fswebcam
        if command -v fswebcam &> /dev/null; then
            echo "Testing webcam capture..."
            fswebcam --no-banner test_webcam.jpg
            if [ -f "test_webcam.jpg" ]; then
                echo "✅ Webcam test successful"
                rm test_webcam.jpg
                return 0
            else
                echo "❌ Webcam test failed"
                return 1
            fi
        else
            echo "⚠️  fswebcam not available, skipping webcam test"
            return 0
        fi
    else
        echo "❌ No webcam devices found"
        echo "Please check webcam connection and try again"
        return 1
    fi
}

# Function to test Python installation
test_python() {
    echo "🐍 Testing Python installation..."
    
    python3 -c "import cv2; print('✅ OpenCV version:', cv2.__version__)" || return 1
    python3 -c "import numpy; print('✅ NumPy version:', numpy.__version__)" || return 1
    
    # Test webcam with OpenCV
    echo "Testing OpenCV webcam access..."
    python3 -c "
import cv2
cap = cv2.VideoCapture(0)
if cap.isOpened():
    print('✅ OpenCV can access webcam')
    ret, frame = cap.read()
    if ret:
        print(f'✅ Webcam resolution: {frame.shape[1]}x{frame.shape[0]}')
    else:
        print('⚠️  Webcam found but cannot capture frame')
    cap.release()
else:
    print('❌ OpenCV cannot access webcam')
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

# Function to show webcam info
show_webcam_info() {
    echo "📷 Webcam Information:"
    echo "====================="
    
    # List video devices
    if ls /dev/video* 2>/dev/null; then
        echo ""
        echo "Available video devices:"
        ls -la /dev/video*
        
        # Show webcam capabilities
        if command -v v4l2-ctl &> /dev/null; then
            echo ""
            echo "Webcam capabilities:"
            v4l2-ctl --list-devices 2>/dev/null || echo "v4l2-ctl not available"
        fi
    else
        echo "No webcam devices found"
    fi
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
    
    # Show webcam info
    show_webcam_info
    
    # Test webcam
    if ! test_webcam; then
        echo "⚠️  Webcam test failed, but continuing..."
        echo "You can still try running the controller manually"
    fi
    
    # Test Python
    if ! test_python; then
        echo "❌ Python test failed"
        exit 1
    fi
    
    echo ""
    echo "🎯 Ready to run!"
    echo "The controller will use your USB webcam to provide real-time height commands for your drone."
    echo "Commands are saved to 'drone_height_commands.json'"
    echo ""
    echo "📝 Notes:"
    echo "  - Make sure your USB webcam is connected and working"
    echo "  - Point the webcam at your crop field"
    echo "  - The system will analyze footage and provide height commands"
    echo "  - Visual UI shows real-time analysis overlay"
    echo ""
    
    # Run the controller
    run_controller
}

# Run main function
main 