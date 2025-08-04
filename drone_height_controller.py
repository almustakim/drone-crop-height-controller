#!/usr/bin/env python3
"""
Real-time Drone Height Controller for Crop Quality Analysis
Provides immediate height adjustment commands for drone control system
Optimized for Raspberry Pi with Pi Camera
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os
import sys

# Try to import PiCamera2, fallback to regular OpenCV
try:
    from picamera2 import Picamera2
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Warning: PiCamera2 not available, using regular OpenCV camera")

class DroneHeightController:
    def __init__(self, crop_type="general", weather_condition="clear"):
        self.crop_type = crop_type
        self.weather_condition = weather_condition
        self.current_height = 3.0  # meters
        self.frame_count = 0
        self.last_command_time = 0
        self.command_interval = 2.0  # seconds between commands
        self.setup_camera()
        self.setup_analysis_parameters()
        
    def setup_camera(self):
        """Setup camera for real-time analysis"""
        if PICAMERA_AVAILABLE:
            self.setup_picamera()
        else:
            self.setup_opencv_camera()
    
    def setup_picamera(self):
        """Setup Pi Camera for optimal performance"""
        try:
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (1280, 720), "format": "RGB888"},
                controls={"FrameDurationLimits": (33333, 33333)}
            )
            self.picam2.configure(config)
            self.picam2.start()
            time.sleep(1)
            print("✓ Pi Camera initialized")
        except Exception as e:
            print(f"Pi Camera error: {e}")
            self.setup_opencv_camera()
    
    def setup_opencv_camera(self):
        """Setup OpenCV camera as fallback"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        print("✓ OpenCV camera initialized")
    
    def setup_analysis_parameters(self):
        """Setup crop-specific analysis parameters"""
        self.crop_params = {
            "wheat": {"optimal_height": 3.0, "green_range": [35, 40, 40, 85, 255, 255]},
            "corn": {"optimal_height": 4.0, "green_range": [35, 50, 50, 85, 255, 255]},
            "rice": {"optimal_height": 2.5, "green_range": [35, 60, 60, 85, 255, 255]},
            "cotton": {"optimal_height": 3.5, "green_range": [35, 40, 40, 85, 255, 255]},
            "general": {"optimal_height": 3.0, "green_range": [35, 50, 50, 85, 255, 255]}
        }
        
        self.weather_adjustments = {
            "clear": {"brightness_mult": 1.0, "contrast_mult": 1.0},
            "cloudy": {"brightness_mult": 0.8, "contrast_mult": 1.2},
            "overcast": {"brightness_mult": 0.7, "contrast_mult": 1.3},
            "sunny": {"brightness_mult": 1.2, "contrast_mult": 0.9},
            "rainy": {"brightness_mult": 0.6, "contrast_mult": 1.4}
        }
        
        self.params = self.crop_params.get(self.crop_type, self.crop_params["general"])
        self.weather = self.weather_adjustments.get(self.weather_condition, self.weather_adjustments["clear"])
    
    def capture_frame(self):
        """Capture frame from camera"""
        try:
            if hasattr(self, 'picam2'):
                frame = self.picam2.capture_array()
                if len(frame.shape) == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame
            elif hasattr(self, 'cap'):
                ret, frame = self.cap.read()
                return frame if ret else None
        except Exception as e:
            print(f"Frame capture error: {e}")
            return None
    
    def analyze_frame_quality(self, frame):
        """Quick quality analysis for real-time drone control"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Brightness analysis
        brightness = np.mean(gray)
        brightness_threshold = 120 * self.weather["brightness_mult"]
        
        # Sharpness analysis (critical for height decisions)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        sharpness_threshold = 80 * self.weather["contrast_mult"]
        
        # Crop coverage analysis
        lower_green = np.array(self.params["green_range"][:3])
        upper_green = np.array(self.params["green_range"][3:])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        green_ratio = np.sum(mask > 0) / (mask.shape[0] * mask.shape[1])
        
        return {
            "brightness": brightness,
            "sharpness": sharpness,
            "green_coverage": green_ratio,
            "brightness_threshold": brightness_threshold,
            "sharpness_threshold": sharpness_threshold
        }
    
    def get_height_command(self, analysis):
        """Generate immediate height adjustment command"""
        current_time = time.time()
        
        # Only send commands at specified intervals
        if current_time - self.last_command_time < self.command_interval:
            return None
        
        self.last_command_time = current_time
        
        # Priority-based height adjustments
        priority = 0
        height_change = 0.0
        reason = ""
        
        # Critical sharpness issues (highest priority)
        if analysis["sharpness"] < analysis["sharpness_threshold"] * 0.5:
            height_change = -1.5  # Move down significantly
            priority = 3
            reason = "Very blurry - critical sharpness issues"
        
        # Sharpness issues
        elif analysis["sharpness"] < analysis["sharpness_threshold"]:
            height_change = -0.75  # Move down moderately
            priority = 2
            reason = "Blurry - need sharper crop details"
        
        # Brightness issues
        elif analysis["brightness"] < analysis["brightness_threshold"] * 0.7:
            height_change = -0.5  # Move down for better lighting
            priority = 2
            reason = "Too dark - need better lighting"
        
        elif analysis["brightness"] > analysis["brightness_threshold"] * 1.3:
            height_change = 0.5  # Move up to reduce overexposure
            priority = 2
            reason = "Too bright - reduce overexposure"
        
        # Crop coverage issues
        elif analysis["green_coverage"] < 0.3:
            height_change = -0.5  # Move down to focus on crops
            priority = 1
            reason = "Low crop coverage - focus on field"
        
        # Optimal conditions
        else:
            priority = 0
            reason = "Optimal quality - maintain position"
        
        # Calculate new height
        new_height = max(1.0, min(10.0, self.current_height + height_change))
        
        # Create command
        command = {
            "timestamp": datetime.now().isoformat(),
            "frame_count": self.frame_count,
            "priority": priority,
            "current_height": self.current_height,
            "target_height": new_height,
            "height_change": height_change,
            "reason": reason,
            "quality_metrics": {
                "brightness": analysis["brightness"],
                "sharpness": analysis["sharpness"],
                "green_coverage": analysis["green_coverage"]
            },
            "crop_type": self.crop_type,
            "weather": self.weather_condition
        }
        
        # Update current height
        self.current_height = new_height
        
        return command
    
    def save_command(self, command):
        """Save command to file for drone control system"""
        if command is None:
            return
        
        filename = "drone_height_commands.json"
        
        # Load existing commands or create new list
        try:
            with open(filename, 'r') as f:
                commands = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            commands = []
        
        # Add new command
        commands.append(command)
        
        # Keep only last 100 commands to prevent file from growing too large
        if len(commands) > 100:
            commands = commands[-100:]
        
        # Save updated commands
        try:
            with open(filename, 'w') as f:
                json.dump(commands, f, indent=2)
        except Exception as e:
            print(f"Error saving command: {e}")
    
    def run_controller(self, duration_minutes=30):
        """Run the height controller"""
        print(f"Starting Drone Height Controller")
        print(f"Crop Type: {self.crop_type}")
        print(f"Weather: {self.weather_condition}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Command Interval: {self.command_interval} seconds")
        print("-" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    time.sleep(0.1)
                    continue
                
                self.frame_count += 1
                
                # Analyze frame
                analysis = self.analyze_frame_quality(frame)
                
                # Get height command
                command = self.get_height_command(analysis)
                
                # Save command
                self.save_command(command)
                
                # Display status
                if command:
                    elapsed = time.time() - start_time
                    print(f"Frame {self.frame_count:4d} | Time {elapsed:6.1f}s | "
                          f"Height: {command['current_height']:.1f}m → {command['target_height']:.1f}m "
                          f"({command['height_change']:+.1f}m) | "
                          f"Priority: {command['priority']} | {command['reason']}")
                
                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.1)  # Small delay
                
        except KeyboardInterrupt:
            print("\nController stopped by user")
        finally:
            self.cleanup()
            print(f"\nController completed. Processed {self.frame_count} frames.")
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'picam2'):
            self.picam2.stop()
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    """Main function"""
    print("Drone Height Controller for Crop Quality Analysis")
    print("=" * 55)
    
    # Get configuration
    crop_type = input("Enter crop type (wheat/corn/rice/cotton/general): ").lower() or "general"
    weather = input("Enter weather (clear/cloudy/overcast/sunny/rainy): ").lower() or "clear"
    duration = input("Enter duration in minutes (default 30): ") or "30"
    
    try:
        duration = int(duration)
    except ValueError:
        duration = 30
    
    # Initialize controller
    controller = DroneHeightController(crop_type, weather)
    
    # Run controller
    controller.run_controller(duration)

if __name__ == "__main__":
    main() 