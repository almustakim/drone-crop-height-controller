#!/usr/bin/env python3
"""
MAVLink Height Integration for Crop Quality Analysis
Raspberry Pi compatible drone height monitoring and image quality analysis
"""

import cv2
import numpy as np
import time
import threading
import json
from datetime import datetime
import os
import sys

# MAVLink imports
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
except ImportError:
    print("Warning: pymavlink not available. Install with: pip install pymavlink")
    MAVLINK_AVAILABLE = False

# Import our analyzer
from imgquality import CropFieldQualityAnalyzer

class MAVLinkHeightMonitor:
    """Real-time height monitoring from MAVLink drone"""
    
    def __init__(self, connection_string="udpin:localhost:14550"):
        self.connection_string = connection_string
        self.connection = None
        self.current_height = None
        self.is_connected = False
        self.running = False
        self.height_thread = None
        
        # Height smoothing
        self.height_history = []
        self.max_history = 5
        
    def connect(self):
        """Connect to MAVLink drone"""
        if not MAVLINK_AVAILABLE:
            print("MAVLink not available - using simulated height")
            return False
            
        try:
            print(f"Connecting to MAVLink at {self.connection_string}...")
            self.connection = mavutil.mavlink_connection(self.connection_string)
            
            # Wait for heartbeat
            self.connection.wait_heartbeat(timeout=10)
            print("MAVLink connection established!")
            
            self.is_connected = True
            return True
            
        except Exception as e:
            print(f"MAVLink connection failed: {e}")
            return False
    
    def start_height_monitoring(self):
        """Start height monitoring in background thread"""
        if self.is_connected:
            self.running = True
            self.height_thread = threading.Thread(target=self._height_monitor_loop)
            self.height_thread.daemon = True
            self.height_thread.start()
            print("Height monitoring started")
        else:
            print("Using simulated height (no MAVLink connection)")
    
    def _height_monitor_loop(self):
        """Background thread for continuous height monitoring"""
        while self.running:
            try:
                # Get altitude from GLOBAL_POSITION_INT message
                msg = self.connection.recv_match(type='GLOBAL_POSITION_INT', timeout=1.0)
                if msg:
                    # Convert altitude from mm to meters
                    altitude_mm = msg.alt
                    altitude_m = altitude_mm / 1000.0
                    
                    # Apply smoothing
                    self.height_history.append(altitude_m)
                    if len(self.height_history) > self.max_history:
                        self.height_history.pop(0)
                    
                    # Use median for stability
                    self.current_height = np.median(self.height_history)
                    
            except Exception as e:
                print(f"Height monitoring error: {e}")
                time.sleep(1)
    
    def get_current_height(self):
        """Get current drone height in meters"""
        if self.current_height is not None:
            return self.current_height
        elif self.is_connected:
            return 3.0  # Default height if no data yet
        else:
            return 3.0  # Simulated height
    
    def stop(self):
        """Stop height monitoring"""
        self.running = False
        if self.height_thread:
            self.height_thread.join(timeout=2)
        if self.connection:
            self.connection.close()

class CropDetector:
    """Simple crop detection using color and contour analysis"""
    
    def __init__(self):
        # Color ranges for different crop types
        self.crop_colors = {
            "wheat": ([35, 40, 40], [85, 255, 255]),      # Green
            "corn": ([35, 50, 50], [85, 255, 255]),       # Green
            "rice": ([35, 60, 60], [85, 255, 255]),       # Green
            "cotton": ([35, 40, 40], [85, 255, 255]),     # Green
            "soybean": ([35, 45, 45], [85, 255, 255])     # Green
        }
    
    def detect_crops(self, frame):
        """Detect crops in the frame"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        crop_results = {}
        
        for crop_type, (lower, upper) in self.crop_colors.items():
            # Create mask for this crop color
            mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
            
            # Find contours
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Filter contours by size
            min_area = 100  # Minimum contour area
            valid_contours = [c for c in contours if cv2.contourArea(c) > min_area]
            
            if valid_contours:
                # Calculate total area and coverage
                total_area = sum(cv2.contourArea(c) for c in valid_contours)
                frame_area = frame.shape[0] * frame.shape[1]
                coverage = total_area / frame_area
                
                crop_results[crop_type] = {
                    "detected": True,
                    "contours": valid_contours,
                    "coverage": coverage,
                    "count": len(valid_contours)
                }
            else:
                crop_results[crop_type] = {
                    "detected": False,
                    "coverage": 0.0,
                    "count": 0
                }
        
        return crop_results
    
    def draw_crop_detections(self, frame, crop_results):
        """Draw detected crops on frame"""
        for crop_type, result in crop_results.items():
            if result["detected"]:
                # Draw contours
                color = (0, 255, 0)  # Green
                cv2.drawContours(frame, result["contours"], -1, color, 2)
                
                # Add label
                for contour in result["contours"]:
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                        cv2.putText(frame, crop_type, (cx, cy), 
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame

class DronePositionController:
    """Generate precise drone positioning commands"""
    
    def __init__(self):
        self.last_commands = []
        self.command_history = []
    
    def generate_position_commands(self, analysis, height_feedback, quality_score):
        """Generate specific drone movement commands"""
        commands = []
        
        # Height adjustments (highest priority)
        if "Too high" in height_feedback:
            commands.append({
                "action": "decrease_height",
                "value": 0.5,
                "priority": "high",
                "reason": "Reduce altitude for better image quality"
            })
        elif "Too low" in height_feedback:
            commands.append({
                "action": "increase_height", 
                "value": 0.5,
                "priority": "high",
                "reason": "Increase altitude for better coverage"
            })
        
        # Quality-based adjustments
        if quality_score < 60:
            if "Blurry" in str(analysis.get("sharpness", [""])):
                commands.append({
                    "action": "decrease_height",
                    "value": 1.0,
                    "priority": "high",
                    "reason": "Critical: Image too blurry for crop analysis"
                })
            
            if "Too Dark" in str(analysis.get("brightness", [""])):
                commands.append({
                    "action": "decrease_height",
                    "value": 0.75,
                    "priority": "medium",
                    "reason": "Improve lighting by reducing altitude"
                })
        
        # Coverage adjustments
        if analysis.get("green_coverage", [0, 0])[1] < 0.3:
            commands.append({
                "action": "adjust_camera_angle",
                "value": "downward",
                "priority": "medium",
                "reason": "Low crop coverage - adjust camera angle"
            })
        
        return commands
    
    def format_commands_for_drone(self, commands):
        """Format commands for drone control system"""
        if not commands:
            return "MAINTAIN_POSITION"
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        commands.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        # Format for drone control
        formatted = []
        for cmd in commands:
            if cmd["action"] == "decrease_height":
                formatted.append(f"DESCEND_{cmd['value']:.1f}m")
            elif cmd["action"] == "increase_height":
                formatted.append(f"ASCEND_{cmd['value']:.1f}m")
            elif cmd["action"] == "adjust_camera_angle":
                formatted.append(f"TILT_{cmd['value'].upper()}")
        
        return " | ".join(formatted)

def main():
    """Main function for MAVLink height integration"""
    print("🌾 MAVLink Crop Quality Analyzer")
    print("=" * 40)
    
    # Initialize components
    height_monitor = MAVLinkHeightMonitor()
    crop_detector = CropDetector()
    position_controller = DronePositionController()
    
    # Initialize analyzer
    analyzer = CropFieldQualityAnalyzer(
        crop_type="wheat",  # Change based on your crop
        weather_condition="clear"
    )
    
    # Try to connect to MAVLink
    if not height_monitor.connect():
        print("⚠️  Using simulated height mode")
    
    # Start height monitoring
    height_monitor.start_height_monitoring()
    
    # Initialize camera (adjust for Pi Camera if needed)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera")
        return
    
    print("📹 Camera initialized")
    print("🎮 Controls: 'q'=quit, 's'=save, 'h'=height info")
    print("🔄 Starting analysis...")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame")
                break
            
            frame_count += 1
            
            # Update drone height
            current_height = height_monitor.get_current_height()
            analyzer.update_drone_height(current_height)
            
            # Analyze frame quality
            analysis = analyzer.analyze_frame_quality(frame)
            
            # Detect crops
            crop_results = crop_detector.detect_crops(frame)
            
            # Get drone positioning feedback
            feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
            
            # Calculate overall quality score
            quality_score = analyzer.calculate_overall_quality_score(analysis)
            
            # Generate position commands
            height_feedback = analyzer.get_height_feedback()
            position_commands = position_controller.generate_position_commands(
                analysis, height_feedback, quality_score
            )
            
            # Format commands for drone
            drone_commands = position_controller.format_commands_for_drone(position_commands)
            
            # Log analysis
            log_entry = analyzer.log_analysis(analysis, feedback, priority, quality_score)
            
            # Display results
            display_enhanced_results(
                frame, analysis, feedback, priority, quality_score, 
                analyzer, crop_results, drone_commands
            )
            
            # Show frame
            cv2.imshow("MAVLink Crop Quality Analysis", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                save_frame_with_data(frame, analysis, quality_score, current_height, crop_results)
            elif key == ord('h'):
                print(f"Current Height: {current_height:.2f}m")
                print(f"Height Feedback: {height_feedback}")
                print(f"Drone Commands: {drone_commands}")
            
            # Performance monitoring
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"FPS: {fps:.1f}, Height: {current_height:.2f}m, Quality: {quality_score:.1f}")
    
    except KeyboardInterrupt:
        print("\n🛑 Analysis interrupted by user")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        height_monitor.stop()
        print("✅ Analysis completed")

def display_enhanced_results(frame, analysis, feedback, priority, quality_score, 
                           analyzer, crop_results, drone_commands):
    """Enhanced display with crop detection and drone commands"""
    # Create overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (600, 400), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Quality score
    color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
    cv2.putText(frame, f"Quality Score: {quality_score:.1f}/100", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Priority
    priority_color = (0, 255, 0) if priority == 0 else (0, 255, 255) if priority <= 2 else (0, 0, 255)
    cv2.putText(frame, f"Priority: {priority}", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
    
    # Height information (prominent)
    y_pos = 90
    if analyzer and analyzer.drone_height is not None:
        height_color = (0, 255, 0)
        cv2.putText(frame, f"Current Height: {analyzer.drone_height:.1f}m", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, height_color, 2)
        y_pos += 30
        
        optimal_height = analyzer.crop_params["optimal_height"]
        cv2.putText(frame, f"Optimal Height: {optimal_height:.1f}m", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, height_color, 2)
        y_pos += 30
        
        # Height status
        height_feedback = analyzer.get_height_feedback()
        if "Optimal" in height_feedback:
            status_color = (0, 255, 0)
        elif "Too high" in height_feedback or "Too low" in height_feedback:
            status_color = (0, 0, 255)
        else:
            status_color = (0, 255, 255)
        
        cv2.putText(frame, f"Height Status: {height_feedback.split('(')[0].strip()}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        y_pos += 30
    
    # Drone commands (important!)
    y_pos += 10
    cv2.putText(frame, "DRONE COMMANDS:", 
               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    
    if drone_commands != "MAINTAIN_POSITION":
        cv2.putText(frame, drone_commands, 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    else:
        cv2.putText(frame, "MAINTAIN_POSITION", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    y_pos += 40
    
    # Crop detection results
    cv2.putText(frame, "CROP DETECTION:", 
               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    y_pos += 25
    
    detected_crops = [crop for crop, result in crop_results.items() if result["detected"]]
    if detected_crops:
        for crop in detected_crops[:3]:  # Show first 3 detected crops
            result = crop_results[crop]
            cv2.putText(frame, f"{crop.title()}: {result['coverage']:.1%}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            y_pos += 20
    else:
        cv2.putText(frame, "No crops detected", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 128, 128), 1)
        y_pos += 20
    
    # Key metrics
    y_pos += 10
    metrics = ["brightness", "sharpness", "green_coverage"]
    for metric in metrics:
        if metric in analysis:
            status, value = analysis[metric]
            if "Good" in status or "Optimal" in status:
                color = (0, 255, 0)
            elif "Poor" in status or "Low" in status or "Blurry" in status:
                color = (0, 0, 255)
            else:
                color = (0, 255, 255)
            
            # Format value display
            if isinstance(value, float):
                display_value = f"{value:.2f}"
            else:
                display_value = str(value)
            
            cv2.putText(frame, f"{metric.replace('_', ' ').title()}: {status} ({display_value})", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 20

def save_frame_with_data(frame, analysis, quality_score, height, crop_results):
    """Save frame with all analysis data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"crop_analysis_{timestamp}_h{height:.1f}_q{quality_score:.1f}.jpg"
    
    # Add analysis overlay to saved frame
    save_frame = frame.copy()
    
    # Add timestamp and data
    cv2.putText(save_frame, f"Height: {height:.1f}m | Quality: {quality_score:.1f}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    
    # Add crop detection info
    detected_crops = [crop for crop, result in crop_results.items() if result["detected"]]
    if detected_crops:
        cv2.putText(save_frame, f"Crops: {', '.join(detected_crops)}", 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    cv2.imwrite(filename, save_frame)
    print(f"📸 Frame saved: {filename}")

if __name__ == "__main__":
    main() 