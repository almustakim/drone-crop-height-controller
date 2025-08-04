#!/usr/bin/env python3
"""
Example integration script for drone control system
This shows how to use the CropFieldQualityAnalyzer with a drone control system
"""

import json
import time
from datetime import datetime
from imgquality import CropFieldQualityAnalyzer

class DroneController:
    """Example drone controller that uses quality analysis for positioning"""
    
    def __init__(self, crop_type="wheat", weather_condition="clear"):
        self.analyzer = CropFieldQualityAnalyzer(crop_type, weather_condition)
        self.current_altitude = 3.0  # meters
        self.quality_threshold = 80
        self.consecutive_good_frames = 0
        self.max_good_frames = 10  # Number of good frames before considering position optimal
        
    def process_frame(self, frame):
        """Process a frame and make drone positioning decisions"""
        
        # Analyze frame quality
        analysis = self.analyzer.analyze_frame_quality(frame)
        feedback, priority, adjustments = self.analyzer.get_drone_position_feedback(analysis)
        quality_score = self.analyzer.calculate_overall_quality_score(analysis)
        
        # Log analysis
        log_entry = self.analyzer.log_analysis(analysis, feedback, priority, quality_score)
        
        # Make drone control decisions
        drone_action = self._decide_drone_action(quality_score, priority, adjustments)
        
        # Execute drone action
        self._execute_drone_action(drone_action)
        
        return {
            "quality_score": quality_score,
            "priority": priority,
            "action": drone_action,
            "analysis": analysis,
            "feedback": feedback
        }
    
    def _decide_drone_action(self, quality_score, priority, adjustments):
        """Decide what action the drone should take based on quality analysis"""
        
        # If quality is good enough and we've had consistent good frames
        if quality_score >= self.quality_threshold:
            self.consecutive_good_frames += 1
            if self.consecutive_good_frames >= self.max_good_frames:
                return {
                    "action": "maintain_position",
                    "reason": f"Optimal quality achieved ({quality_score:.1f})",
                    "duration": 5.0  # seconds
                }
        else:
            self.consecutive_good_frames = 0
        
        # Process adjustments based on priority
        if priority >= 3:  # Critical issues
            return self._process_critical_adjustments(adjustments)
        elif priority >= 2:  # Moderate issues
            return self._process_moderate_adjustments(adjustments)
        elif priority >= 1:  # Minor issues
            return self._process_minor_adjustments(adjustments)
        else:
            return {
                "action": "continue_monitoring",
                "reason": "Quality acceptable, continue monitoring",
                "duration": 2.0
            }
    
    def _process_critical_adjustments(self, adjustments):
        """Process critical quality issues"""
        for adj in adjustments:
            if adj["action"] == "decrease_altitude":
                new_altitude = max(1.0, self.current_altitude - adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "fast",
                    "reason": "Critical sharpness issues - moving closer"
                }
            elif adj["action"] == "increase_altitude":
                new_altitude = min(10.0, self.current_altitude + adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "fast",
                    "reason": "Critical brightness issues - moving higher"
                }
        
        return {
            "action": "emergency_hover",
            "reason": "Critical issues detected - hovering for safety",
            "duration": 3.0
        }
    
    def _process_moderate_adjustments(self, adjustments):
        """Process moderate quality issues"""
        for adj in adjustments:
            if adj["action"] == "decrease_altitude":
                new_altitude = max(1.0, self.current_altitude - adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "medium",
                    "reason": "Moderate quality issues - adjusting altitude"
                }
            elif adj["action"] == "increase_altitude":
                new_altitude = min(10.0, self.current_altitude + adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "medium",
                    "reason": "Moderate quality issues - adjusting altitude"
                }
        
        return {
            "action": "fine_tune_position",
            "reason": "Moderate issues - fine-tuning position",
            "duration": 2.0
        }
    
    def _process_minor_adjustments(self, adjustments):
        """Process minor quality issues"""
        for adj in adjustments:
            if adj["action"] == "decrease_altitude":
                new_altitude = max(1.0, self.current_altitude - adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "slow",
                    "reason": "Minor quality issues - slight adjustment"
                }
            elif adj["action"] == "increase_altitude":
                new_altitude = min(10.0, self.current_altitude + adj["value"])
                return {
                    "action": "change_altitude",
                    "target_altitude": new_altitude,
                    "speed": "slow",
                    "reason": "Minor quality issues - slight adjustment"
                }
        
        return {
            "action": "continue_monitoring",
            "reason": "Minor issues - continue monitoring",
            "duration": 1.0
        }
    
    def _execute_drone_action(self, action):
        """Execute the drone action (placeholder for actual drone control)"""
        
        print(f"\n=== DRONE ACTION ===")
        print(f"Action: {action['action']}")
        print(f"Reason: {action['reason']}")
        
        if action['action'] == 'change_altitude':
            old_altitude = self.current_altitude
            self.current_altitude = action['target_altitude']
            print(f"Altitude: {old_altitude:.1f}m → {self.current_altitude:.1f}m")
            print(f"Speed: {action['speed']}")
        elif action['action'] == 'maintain_position':
            print(f"Maintaining position for {action['duration']} seconds")
        elif action['action'] == 'continue_monitoring':
            print(f"Continuing monitoring for {action['duration']} seconds")
        
        print("==================\n")

def simulate_drone_operation():
    """Simulate drone operation with quality analysis"""
    
    print("Starting Drone Quality Control Simulation")
    print("=" * 50)
    
    # Initialize drone controller
    controller = DroneController(crop_type="wheat", weather_condition="clear")
    
    # Simulate different quality scenarios
    scenarios = [
        {"name": "Optimal Quality", "quality": 85, "priority": 0},
        {"name": "Slightly Blurry", "quality": 65, "priority": 2},
        {"name": "Too Dark", "quality": 45, "priority": 2},
        {"name": "Very Blurry", "quality": 25, "priority": 3},
        {"name": "Good Quality", "quality": 75, "priority": 1},
    ]
    
    for i, scenario in enumerate(scenarios):
        print(f"\nScenario {i+1}: {scenario['name']}")
        print("-" * 30)
        
        # Simulate frame processing
        # In real implementation, this would be an actual camera frame
        dummy_frame = None  # Placeholder for actual frame
        
        # Process frame (simulated)
        result = controller.process_frame(dummy_frame)
        
        # Override quality for simulation
        result['quality_score'] = scenario['quality']
        result['priority'] = scenario['priority']
        
        print(f"Quality Score: {result['quality_score']:.1f}/100")
        print(f"Priority Level: {result['priority']}")
        print(f"Action: {result['action']['action']}")
        print(f"Reason: {result['action']['reason']}")
        
        time.sleep(1)  # Simulate processing time

def main():
    """Main function to demonstrate integration"""
    
    print("Crop Field Quality Analysis - Drone Integration Example")
    print("=" * 60)
    
    # Run simulation
    simulate_drone_operation()
    
    print("\nSimulation completed!")
    print("\nTo use with real drone:")
    print("1. Replace dummy_frame with actual camera frame")
    print("2. Implement actual drone control commands in _execute_drone_action()")
    print("3. Add error handling and safety checks")
    print("4. Configure crop type and weather conditions")

if __name__ == "__main__":
    main() 