#!/usr/bin/env python3
"""
Raspberry Pi Camera version of Crop Field Quality Analysis
Optimized for Pi Camera with better performance
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os
import sys

# Try to import PiCamera2, fallback to regular OpenCV if not available
try:
    from picamera2 import Picamera2
    from picamera2.encoders import JpegEncoder
    from picamera2.outputs import FileOutput
    PICAMERA_AVAILABLE = True
except ImportError:
    PICAMERA_AVAILABLE = False
    print("Warning: PiCamera2 not available, using regular OpenCV camera")

# Import the main analyzer class
from imgquality import CropFieldQualityAnalyzer

class PiCameraQualityAnalyzer:
    def __init__(self, crop_type="general", weather_condition="clear"):
        self.analyzer = CropFieldQualityAnalyzer(crop_type, weather_condition)
        self.picam2 = None
        self.cap = None
        self.setup_camera()
        
    def setup_camera(self):
        """Setup camera with optimal settings for crop analysis"""
        if PICAMERA_AVAILABLE:
            self.setup_picamera()
        else:
            self.setup_opencv_camera()
        
    def setup_picamera(self):
        """Setup Pi Camera with optimal settings"""
        try:
            self.picam2 = Picamera2()
            
            # Configure camera for crop analysis
            config = self.picam2.create_preview_configuration(
                main={"size": (1280, 720), "format": "RGB888"},
                controls={"FrameDurationLimits": (33333, 33333)}  # 30 FPS
            )
            
            self.picam2.configure(config)
            self.picam2.start()
            
            # Wait for camera to start
            time.sleep(2)
            print("Pi Camera initialized successfully")
            
        except Exception as e:
            print(f"Error setting up Pi Camera: {e}")
            print("Falling back to OpenCV camera")
            self.setup_opencv_camera()
    
    def setup_opencv_camera(self):
        """Setup regular OpenCV camera as fallback"""
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            print("Error: Could not open camera")
            sys.exit(1)
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        
        print("OpenCV camera initialized successfully")
        
    def capture_frame(self):
        """Capture a frame from camera"""
        try:
            if self.picam2:
                frame = self.picam2.capture_array()
                # Convert BGR to RGB if needed
                if len(frame.shape) == 3:
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return frame
            elif self.cap:
                ret, frame = self.cap.read()
                if ret:
                    return frame
                else:
                    return None
        except Exception as e:
            print(f"Error capturing frame: {e}")
            return None
    
    def run_analysis(self, duration_minutes=30):
        """Run continuous analysis for specified duration"""
        print(f"Starting crop quality analysis for {duration_minutes} minutes...")
        print("Press Ctrl+C to stop early")
        print(f"Crop Type: {self.analyzer.crop_type}")
        print(f"Weather: {self.analyzer.weather_condition}")
        print("-" * 50)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        frame_count = 0
        
        try:
            while time.time() < end_time:
                # Capture frame
                frame = self.capture_frame()
                if frame is None:
                    print("Failed to capture frame, retrying...")
                    time.sleep(1)
                    continue
                
                frame_count += 1
                
                # Analyze frame quality
                analysis = self.analyzer.analyze_frame_quality(frame)
                feedback, priority, adjustments = self.analyzer.get_drone_position_feedback(analysis)
                quality_score = self.analyzer.calculate_overall_quality_score(analysis)
                
                # Log analysis
                log_entry = self.analyzer.log_analysis(analysis, feedback, priority, quality_score)
                
                # Display results
                self.display_results(frame, analysis, feedback, priority, quality_score)
                
                # Print console output
                elapsed = time.time() - start_time
                print(f"Frame {frame_count:4d} | Time {elapsed:6.1f}s | Quality: {quality_score:5.1f}/100 | Priority: {priority} | {feedback[0] if feedback else 'Optimal'}")
                
                # Save frame if quality is good
                if quality_score > 80:
                    self.save_quality_frame(frame, quality_score)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nStopped by user (q key)")
                    break
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nAnalysis stopped by user (Ctrl+C)")
        finally:
            self.cleanup()
            print(f"\nAnalysis completed. Processed {frame_count} frames.")
    
    def display_results(self, frame, analysis, feedback, priority, quality_score):
        """Display analysis results on frame"""
        # Create overlay for better visibility
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (450, 300), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Display quality score prominently
        color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
        cv2.putText(frame, f"Quality: {quality_score:.1f}/100", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Display priority
        priority_color = (0, 255, 0) if priority == 0 else (0, 255, 255) if priority <= 2 else (0, 0, 255)
        cv2.putText(frame, f"Priority: {priority}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
        
        # Display crop and weather info
        cv2.putText(frame, f"Crop: {self.analyzer.crop_type.title()}", 
                   (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Weather: {self.analyzer.weather_condition.title()}", 
                   (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Display key metrics
        y_pos = 130
        for metric, (status, value) in analysis.items():
            if metric in ["brightness", "contrast", "sharpness", "green_coverage"]:
                color = (0, 255, 0) if "Good" in status or "Optimal" in status else (0, 0, 255)
                cv2.putText(frame, f"{metric.title()}: {status} ({value:.1f})", 
                           (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_pos += 25
        
        # Display feedback
        y_pos += 10
        for i, msg in enumerate(feedback[:2]):  # Show first 2 feedback messages
            cv2.putText(frame, msg, (10, y_pos + i*20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Show the frame
        cv2.imshow("Crop Quality Analysis - Pi Camera", frame)
    
    def save_quality_frame(self, frame, quality_score):
        """Save high-quality frames"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"quality_frame_{timestamp}_score_{quality_score:.1f}.jpg"
        
        # Create output directory if it doesn't exist
        os.makedirs("quality_frames", exist_ok=True)
        filepath = os.path.join("quality_frames", filename)
        
        cv2.imwrite(filepath, frame)
        print(f"  ✓ Saved quality frame: {filepath}")
    
    def cleanup(self):
        """Cleanup resources"""
        if self.picam2:
            self.picam2.stop()
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def load_config():
    """Load configuration from file"""
    config_file = "pi_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config file: {e}")
    
    # Default configuration
    return {
        "camera_settings": {
            "resolution": [1280, 720],
            "fps": 15,
            "quality": 85
        },
        "analysis_settings": {
            "analysis_interval": 2,
            "save_interval": 5,
            "quality_threshold": 70
        }
    }

def main():
    """Main function for Pi Camera analysis"""
    print("Raspberry Pi Crop Quality Analysis")
    print("=" * 50)
    
    # Load configuration
    config = load_config()
    
    # Get user input
    print("\nConfiguration:")
    crop_type = input("Enter crop type (wheat/corn/rice/cotton/general): ").lower() or "general"
    weather = input("Enter weather condition (clear/cloudy/overcast/sunny/rainy): ").lower() or "clear"
    duration = input("Enter analysis duration in minutes (default 30): ") or "30"
    
    try:
        duration = int(duration)
    except ValueError:
        duration = 30
    
    print(f"\nStarting analysis with:")
    print(f"  Crop Type: {crop_type}")
    print(f"  Weather: {weather}")
    print(f"  Duration: {duration} minutes")
    print(f"  Camera: {'Pi Camera' if PICAMERA_AVAILABLE else 'OpenCV Camera'}")
    
    # Initialize analyzer
    try:
        analyzer = PiCameraQualityAnalyzer(crop_type, weather)
        
        # Run analysis
        analyzer.run_analysis(duration)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("Please check camera connection and try again")

if __name__ == "__main__":
    main() 