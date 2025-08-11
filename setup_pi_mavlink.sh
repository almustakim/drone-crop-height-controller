#!/bin/bash
# Raspberry Pi MAVLink Setup Script
# Run this script to set up the crop quality analyzer with MAVLink support

echo "🌾 Setting up MAVLink Crop Quality Analyzer for Raspberry Pi"
echo "=========================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3-pip python3-venv python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libqtgui4 libqtwebkit4 libqt4-test python3-pyqt5
sudo apt install -y libjasper-dev libqtcore4 libqt4-test

# Install MAVLink dependencies
echo "🚁 Installing MAVLink dependencies..."
sudo apt install -y python3-dev build-essential
sudo apt install -y libxml2-dev libxslt-dev
sudo apt install -y libffi-dev libssl-dev

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv mavlink_venv
source mavlink_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python packages
echo "📚 Installing Python packages..."
pip install -r requirements_pi_mavlink.txt

# Test MAVLink installation
echo "🧪 Testing MAVLink installation..."
python3 -c "from pymavlink import mavutil; print('✅ MAVLink installed successfully')"

# Create configuration file
echo "⚙️  Creating configuration file..."
cat > pi_mavlink_config.json << EOF
{
    "mavlink": {
        "connection_string": "udpin:localhost:14550",
        "timeout": 10,
        "heartbeat_timeout": 5
    },
    "camera": {
        "device": 0,
        "width": 640,
        "height": 480,
        "fps": 30
    },
    "analysis": {
        "crop_type": "wheat",
        "weather_condition": "clear",
        "save_frames": true,
        "log_analysis": true
    },
    "display": {
        "show_overlay": true,
        "show_crop_detection": true,
        "show_drone_commands": true
    }
}
EOF

# Create run script
echo "🚀 Creating run script..."
cat > run_mavlink_analyzer.sh << 'EOF'
#!/bin/bash
# Run the MAVLink crop quality analyzer

echo "Starting MAVLink Crop Quality Analyzer..."
source mavlink_venv/bin/activate

# Check if MAVLink is available
python3 -c "from pymavlink import mavutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ MAVLink available - starting analyzer..."
    python3 mavlink_height_analyzer.py
else
    echo "❌ MAVLink not available - please install dependencies first"
    echo "Run: ./setup_pi_mavlink.sh"
    exit 1
fi
EOF

chmod +x run_mavlink_analyzer.sh

# Create systemd service (optional)
echo "🔧 Creating systemd service (optional)..."
cat > mavlink-analyzer.service << EOF
[Unit]
Description=MAVLink Crop Quality Analyzer
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/run_mavlink_analyzer.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Connect your drone to the Raspberry Pi"
echo "2. Ensure MAVLink is enabled on your drone"
echo "3. Run: ./run_mavlink_analyzer.sh"
echo ""
echo "🔧 Optional: Install as system service:"
echo "   sudo cp mavlink-analyzer.service /etc/systemd/system/"
echo "   sudo systemctl enable mavlink-analyzer.service"
echo "   sudo systemctl start mavlink-analyzer.service"
echo ""
echo "📖 For troubleshooting, check the logs:"
echo "   journalctl -u mavlink-analyzer.service -f" 