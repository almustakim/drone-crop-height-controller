#!/usr/bin/env python3
"""
Real-time Drone Height Controller for Crop Quality Analysis
Provides immediate height adjustment commands for drone control system
Optimized for Raspberry Pi with USB Webcam
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os
import sys

class DroneHeightController:
    def __init__(self, crop_type="general", weather_condition="clear", show_ui=True):
        self.crop_type = crop_type
        self.weather_condition = weather_condition
        self.current_height = 3.0  # meters
        self.frame_count = 0
        self.last_command_time = 0
        self.command_interval = 2.0  # seconds between commands
        self.show_ui = show_ui
        self.setup_webcam()
        self.setup_analysis_parameters()
        
    def setup_webcam(self):
        """Setup USB webcam for optimal performance"""
        print("🔌 Setting up webcam...")
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open webcam at index 0")
            print("Trying alternative camera indices...")
            # Try different camera indices
            for i in range(1, 4):
                self.cap = cv2.VideoCapture(i)
                if self.cap.isOpened():
                    print(f"✓ Webcam found at index {i}")
                    break
            else:
                print("❌ No webcam found. Please check connection.")
                print("Available video devices:")
                os.system("ls /dev/video* 2>/dev/null || echo 'No video devices found'")
                sys.exit(1)
        
        # Set camera properties for optimal performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Enable autofocus
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Auto exposure
        
        # Test camera
        ret, test_frame = self.cap.read()
        if ret:
            print(f"✓ Webcam initialized successfully")
            print(f"  Resolution: {test_frame.shape[1]}x{test_frame.shape[0]}")
        else:
            print("❌ Failed to capture test frame from webcam")
            sys.exit(1)
    
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
        """Capture frame from webcam"""
        try:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                print("Warning: Failed to capture frame from webcam")
                return None
        except Exception as e:
            print(f"Frame capture error: {e}")
            return None
    
    def display_ui(self, frame, analysis, command):
        """Display analysis results on frame with UI overlay"""
        if not self.show_ui:
            return
        
        # Create overlay for better visibility
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (500, 350), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Calculate quality score
        quality_score = self.calculate_quality_score(analysis)
        
        # Display quality score prominently
        if quality_score >= 80:
            color = (0, 255, 0)  # Green
        elif quality_score >= 60:
            color = (0, 255, 255)  # Yellow
        else:
            color = (0, 0, 255)  # Red
            
        cv2.putText(frame, f"Quality Score: {quality_score:.1f}/100", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Display current height and target
        if command:
            priority_color = (0, 255, 0) if command['priority'] == 0 else (0, 255, 255) if command['priority'] <= 2 else (0, 0, 255)
            cv2.putText(frame, f"Height: {command['current_height']:.1f}m → {command['target_height']:.1f}m", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
            cv2.putText(frame, f"Priority: {command['priority']}", 
                       (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, priority_color, 2)
        
        # Display crop and weather info
        cv2.putText(frame, f"Crop: {self.crop_type.title()}", 
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Weather: {self.weather_condition.title()}", 
                   (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Camera: USB Webcam", 
                   (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display metrics
        y_pos = 175
        for metric, value in analysis.items():
            if metric in ["brightness", "sharpness", "green_coverage"]:
                # Determine color based on quality
                if metric == "brightness":
                    threshold = analysis["brightness_threshold"]
                    color = (0, 255, 0) if abs(value - threshold) < 20 else (0, 0, 255)
                elif metric == "sharpness":
                    threshold = analysis["sharpness_threshold"]
                    color = (0, 255, 0) if value >= threshold else (0, 0, 255)
                elif metric == "green_coverage":
                    color = (0, 255, 0) if value >= 0.3 else (0, 0, 255)
                else:
                    color = (255, 255, 255)
                
                cv2.putText(frame, f"{metric.title()}: {value:.1f}", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_pos += 25
        
        # Display command reason
        if command and command['reason']:
            y_pos += 10
            cv2.putText(frame, f"Action: {command['reason']}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display frame count and timestamp
        cv2.putText(frame, f"Frame: {self.frame_count}", 
                   (10, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(frame, f"Press 'q' to quit", 
                   (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        
        # Show the frame
        cv2.imshow("Drone Height Controller - Crop Analysis", frame)
    
    def calculate_quality_score(self, analysis):
        """Calculate overall quality score (0-100)"""
        scores = []
        
        # Brightness score
        brightness_diff = abs(analysis["brightness"] - analysis["brightness_threshold"])
        brightness_score = max(0, 100 - brightness_diff / 2)
        scores.append(brightness_score * 0.3)
        
        # Sharpness score
        sharpness_ratio = analysis["sharpness"] / analysis["sharpness_threshold"]
        sharpness_score = min(100, sharpness_ratio * 100)
        scores.append(sharpness_score * 0.4)
        
        # Coverage score
        coverage_score = min(100, analysis["green_coverage"] * 200)
        scores.append(coverage_score * 0.3)
        
        return sum(scores)
    
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
            "weather": self.weather_condition,
            "camera_type": "webcam"
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
        print(f"Camera: USB Webcam")
        print(f"UI Display: {'Enabled' if self.show_ui else 'Disabled'}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Command Interval: {self.command_interval} seconds")
        print("-" * 60)
        
        if self.show_ui:
            print("📺 UI Display: Press 'q' to quit the application")
        
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
                
                # Display UI
                self.display_ui(frame, analysis, command)
                
                # Display console output
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
        if hasattr(self, 'cap'):
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    """Main function"""
    print("Drone Height Controller for Crop Quality Analysis")
    print("=" * 55)
    print("📹 USB Webcam Version")
    print("=" * 55)
    
    # Get configuration
    crop_type = input("Enter crop type (wheat/corn/rice/cotton/general): ").lower() or "general"
    weather = input("Enter weather (clear/cloudy/overcast/sunny/rainy): ").lower() or "clear"
    duration = input("Enter duration in minutes (default 30): ") or "30"
    
    # Ask about UI display
    ui_choice = input("Show UI display? (y/n, default y): ").lower() or "y"
    show_ui = ui_choice in ['y', 'yes', '1', 'true']
    
    try:
        duration = int(duration)
    except ValueError:
        duration = 30
    
    # Initialize controller
    controller = DroneHeightController(crop_type, weather, show_ui)
    
    # Run controller
    controller.run_controller(duration)

if __name__ == "__main__":
    main() 