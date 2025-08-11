#!/usr/bin/env python3
"""
Clean Image Quality Analysis for Crop Monitoring
Simple, efficient analysis without heavy AI dependencies
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os

class CropFieldQualityAnalyzer:
    def __init__(self, crop_type="general", weather_condition="clear", drone_height=None):
        """
        Initialize analyzer with crop-specific parameters
        
        Args:
            crop_type: Type of crop (wheat, corn, rice, cotton, etc.)
            weather_condition: Current weather (clear, cloudy, overcast, etc.)
            drone_height: Current drone height in meters (from telemetry)
        """
        self.crop_type = crop_type
        self.weather_condition = weather_condition
        self.drone_height = drone_height
        self.frame_count = 0
        self.quality_history = []
        
        # Crop-specific parameters
        self.crop_params = self._get_crop_parameters()
        
        # Weather-based adjustments
        self.weather_adjustments = self._get_weather_adjustments()
        
        # Quality thresholds (adjusted based on crop and weather)
        self.thresholds = self._calculate_thresholds()
        
    def update_drone_height(self, height):
        """Update current drone height from telemetry"""
        self.drone_height = height
        print(f"Drone height updated: {height}m")
    
    def get_height_feedback(self):
        """Get height-specific feedback based on current altitude"""
        if self.drone_height is None:
            return "Height data not available - check drone telemetry"
        
        optimal_height = self.crop_params["optimal_height"]
        height_diff = self.drone_height - optimal_height
        
        if abs(height_diff) < 0.5:
            return f"Optimal height: {self.drone_height:.1f}m (within 0.5m of target)"
        elif height_diff > 0:
            return f"Too high: {self.drone_height:.1f}m (decrease by {height_diff:.1f}m to reach {optimal_height}m)"
        else:
            return f"Too low: {self.drone_height:.1f}m (increase by {abs(height_diff):.1f}m to reach {optimal_height}m)"
    
    def get_height_recommendation(self):
        """Get specific height adjustment recommendation"""
        if self.drone_height is None:
            return None
        
        optimal_height = self.crop_params["optimal_height"]
        height_diff = self.drone_height - optimal_height
        
        if abs(height_diff) < 0.5:
            return {"action": "maintain_height", "reason": "Optimal altitude achieved"}
        elif height_diff > 0:
            return {"action": "decrease_height", "value": height_diff, "reason": f"Too high for {self.crop_type}"}
        else:
            return {"action": "increase_height", "value": abs(height_diff), "reason": f"Too low for {self.crop_type}"}
    
    def _get_crop_parameters(self):
        """Define crop-specific analysis parameters"""
        crop_params = {
            "wheat": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 1.2,
                "detail_importance": "high",
                "optimal_height": 3.0,  # meters
                "min_resolution": 0.5,   # cm per pixel
                "height_tolerance": 0.5   # meters
            },
            "corn": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                "optimal_height": 4.0,
                "min_resolution": 0.8,
                "height_tolerance": 0.8
            },
            "rice": {
                "green_range": ([35, 60, 60], [85, 255, 255]),
                "texture_sensitivity": 1.1,
                "detail_importance": "high",
                "optimal_height": 2.5,
                "min_resolution": 0.4,
                "height_tolerance": 0.4
            },
            "cotton": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 0.9,
                "detail_importance": "medium",
                "optimal_height": 3.5,
                "min_resolution": 0.6,
                "height_tolerance": 0.6
            },
            "general": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                "optimal_height": 3.0,
                "min_resolution": 0.5,
                "height_tolerance": 0.5
            }
        }
        return crop_params.get(self.crop_type, crop_params["general"])
    
    def _get_weather_adjustments(self):
        """Adjust thresholds based on weather conditions"""
        adjustments = {
            "clear": {"brightness_mult": 1.0, "contrast_mult": 1.0, "sharpness_mult": 1.0},
            "cloudy": {"brightness_mult": 0.8, "contrast_mult": 1.2, "sharpness_mult": 0.9},
            "overcast": {"brightness_mult": 0.7, "contrast_mult": 1.3, "sharpness_mult": 0.8},
            "sunny": {"brightness_mult": 1.2, "contrast_mult": 0.9, "sharpness_mult": 1.1}
        }
        return adjustments.get(self.weather_condition, adjustments["clear"])
    
    def _calculate_thresholds(self):
        """Calculate dynamic thresholds based on crop and weather"""
        adj = self.weather_adjustments
        
        return {
            "brightness": {
                "min": 60 * adj["brightness_mult"],
                "max": 180 * adj["brightness_mult"],
                "optimal": 120 * adj["brightness_mult"]
            },
            "contrast": {
                "min": 25 * adj["contrast_mult"],
                "optimal": 40 * adj["contrast_mult"]
            },
            "sharpness": {
                "min": 80 * adj["sharpness_mult"],
                "optimal": 150 * adj["sharpness_mult"]
            },
            "green_coverage": {
                "min": 0.3,
                "optimal": 0.6
            },
            "texture_variance": {
                "min": 50 * self.crop_params["texture_sensitivity"],
                "optimal": 100 * self.crop_params["texture_sensitivity"]
            }
        }
    
    def analyze_frame_quality(self, frame):
        """Comprehensive frame quality analysis for crop monitoring"""
        # Convert frame to different color spaces
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 1. Brightness Analysis
        brightness = np.mean(gray)
        brightness_score = self._calculate_brightness_score(brightness)
        
        # 2. Contrast Analysis
        contrast = np.std(gray)
        contrast_score = self._calculate_contrast_score(contrast)
        
        # 3. Sharpness Analysis (Enhanced for crop details)
        sharpness = self._analyze_sharpness(gray)
        sharpness_score = self._calculate_sharpness_score(sharpness)
        
        # 4. Crop Coverage Analysis
        green_coverage = self._analyze_crop_coverage(hsv)
        coverage_score = self._calculate_coverage_score(green_coverage)
        
        # 5. Texture Analysis (Important for disease detection)
        texture_variance = self._analyze_texture(gray)
        texture_score = self._calculate_texture_score(texture_variance)
        
        # 6. Focus Analysis
        focus_score = self._analyze_focus(gray)
        
        # 7. Noise Analysis
        noise_level = self._analyze_noise(gray)
        noise_score = self._calculate_noise_score(noise_level)
        
        # 8. Enhanced Crop Health Analysis
        crop_health = self._analyze_crop_health(hsv)
        
        return {
            "brightness": (brightness_score, brightness),
            "contrast": (contrast_score, contrast),
            "sharpness": (sharpness_score, sharpness),
            "green_coverage": (coverage_score, green_coverage),
            "texture_variance": (texture_score, texture_variance),
            "focus": (focus_score, focus_score),
            "noise": (noise_score, noise_level),
            "crop_health": (crop_health["status"], crop_health["score"])
        }
    
    def _analyze_crop_health(self, hsv):
        """Analyze crop health using color analysis"""
        try:
            # Define color ranges for different health states
            healthy_green = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
            stressed_yellow = cv2.inRange(hsv, np.array([20, 50, 50]), np.array([35, 255, 255]))
            diseased_brown = cv2.inRange(hsv, np.array([10, 50, 50]), np.array([20, 255, 255]))
            
            # Calculate percentages
            total_pixels = hsv.shape[0] * hsv.shape[1]
            healthy_pixels = np.sum(healthy_green > 0)
            stressed_pixels = np.sum(stressed_yellow > 0)
            diseased_pixels = np.sum(diseased_brown > 0)
            
            healthy_ratio = healthy_pixels / total_pixels
            stressed_ratio = stressed_pixels / total_pixels
            diseased_ratio = diseased_pixels / total_pixels
            
            # Calculate health score (0-1)
            health_score = healthy_ratio * 1.0 + stressed_ratio * 0.5 + diseased_ratio * 0.0
            
            # Determine health status
            if health_score > 0.8:
                status = "Excellent Health"
            elif health_score > 0.6:
                status = "Good Health"
            elif health_score > 0.4:
                status = "Moderate Health"
            else:
                status = "Poor Health"
            
            return {
                "status": status,
                "score": health_score,
                "healthy_ratio": healthy_ratio,
                "stressed_ratio": stressed_ratio,
                "diseased_ratio": diseased_ratio
            }
            
        except Exception as e:
            return {
                "status": "Health Analysis Failed",
                "score": 0.0
            }
    
    def _analyze_sharpness(self, gray):
        """Enhanced sharpness analysis using multiple methods"""
        # Laplacian variance
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_var = laplacian.var()
        
        # Sobel edge detection
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
        sobel_mean = np.mean(sobel_magnitude)
        
        # Combined sharpness metric
        return (laplacian_var * 0.7 + sobel_mean * 0.3)
    
    def _analyze_crop_coverage(self, hsv):
        """Analyze crop coverage with crop-specific color ranges"""
        lower_green, upper_green = self.crop_params["green_range"]
        mask = cv2.inRange(hsv, np.array(lower_green), np.array(upper_green))
        
        # Calculate coverage ratio
        total_pixels = mask.shape[0] * mask.shape[1]
        green_pixels = np.sum(mask > 0)
        coverage_ratio = green_pixels / total_pixels
        
        return coverage_ratio
    
    def _analyze_texture(self, gray):
        """Analyze texture variance for crop detail detection"""
        # Apply Gaussian blur to get texture
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        texture = cv2.absdiff(gray, blurred)
        return np.var(texture)
    
    def _analyze_focus(self, gray):
        """Analyze focus using frequency domain analysis"""
        # FFT for focus analysis
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.log(np.abs(f_shift) + 1)
        
        # Calculate focus score based on high-frequency content
        center_y, center_x = gray.shape[0] // 2, gray.shape[1] // 2
        high_freq_region = magnitude_spectrum[center_y-50:center_y+50, center_x-50:center_x+50]
        focus_score = np.mean(high_freq_region)
        
        return focus_score
    
    def _analyze_noise(self, gray):
        """Analyze noise level in the image"""
        # Apply median filter to estimate noise
        median_filtered = cv2.medianBlur(gray, 3)
        noise = cv2.absdiff(gray, median_filtered)
        return np.mean(noise)
    
    def _calculate_brightness_score(self, brightness):
        """Calculate brightness quality score"""
        if brightness < self.thresholds["brightness"]["min"]:
            return "Too Dark"
        elif brightness > self.thresholds["brightness"]["max"]:
            return "Too Bright"
        elif abs(brightness - self.thresholds["brightness"]["optimal"]) < 20:
            return "Optimal Brightness"
        else:
            return "Acceptable Brightness"
    
    def _calculate_contrast_score(self, contrast):
        """Calculate contrast quality score"""
        if contrast < self.thresholds["contrast"]["min"]:
            return "Low Contrast"
        elif contrast > self.thresholds["contrast"]["optimal"]:
            return "High Contrast"
        else:
            return "Good Contrast"
    
    def _calculate_sharpness_score(self, sharpness):
        """Calculate sharpness quality score"""
        if sharpness < self.thresholds["sharpness"]["min"]:
            return "Blurry"
        elif sharpness > self.thresholds["sharpness"]["optimal"]:
            return "Very Sharp"
        else:
            return "Good Sharpness"
    
    def _calculate_coverage_score(self, coverage):
        """Calculate crop coverage quality score"""
        if coverage < self.thresholds["green_coverage"]["min"]:
            return "Low Crop Coverage"
        elif coverage > self.thresholds["green_coverage"]["optimal"]:
            return "High Crop Coverage"
        else:
            return "Good Crop Coverage"
    
    def _calculate_texture_score(self, texture):
        """Calculate texture quality score"""
        if texture < self.thresholds["texture_variance"]["min"]:
            return "Low Texture Detail"
        elif texture > self.thresholds["texture_variance"]["optimal"]:
            return "High Texture Detail"
        else:
            return "Good Texture Detail"
    
    def _calculate_noise_score(self, noise):
        """Calculate noise quality score"""
        if noise < 5:
            return "Low Noise"
        elif noise < 15:
            return "Acceptable Noise"
        else:
            return "High Noise"
    
    def get_drone_position_feedback(self, analysis):
        """Generate precise drone positioning recommendations"""
        feedback = []
        priority = 0
        adjustments = []
        
        # Height-based adjustments (highest priority)
        height_rec = self.get_height_recommendation()
        if height_rec:
            if height_rec["action"] == "decrease_height":
                feedback.append(f"Decrease altitude by {height_rec['value']:.1f}m to {height_rec['reason']}")
                adjustments.append({"action": "decrease_height", "value": height_rec["value"], "type": "height"})
                priority = max(priority, 3)
            elif height_rec["action"] == "increase_height":
                feedback.append(f"Increase altitude by {height_rec['value']:.1f}m to {height_rec['reason']}")
                adjustments.append({"action": "increase_height", "value": height_rec["value"], "type": "height"})
                priority = max(priority, 3)
            else:
                feedback.append(f"Optimal height: {self.drone_height:.1f}m")
        
        # Brightness adjustments
        if "Too Dark" in analysis["brightness"][0]:
            feedback.append("Decrease altitude by 0.5-1.0m for better lighting")
            adjustments.append({"action": "decrease_altitude", "value": 0.75, "type": "lighting"})
            priority = max(priority, 2)
        elif "Too Bright" in analysis["brightness"][0]:
            feedback.append("Increase altitude by 0.5-1.0m to reduce overexposure")
            adjustments.append({"action": "increase_altitude", "value": 0.75, "type": "lighting"})
            priority = max(priority, 2)
        
        # Sharpness adjustments
        if "Blurry" in analysis["sharpness"][0]:
            feedback.append("Decrease altitude by 1.0-1.5m for sharper crop details")
            adjustments.append({"action": "decrease_altitude", "value": 1.25, "type": "focus"})
            priority = max(priority, 3)
        
        # Coverage adjustments
        if "Low Crop Coverage" in analysis["green_coverage"][0]:
            feedback.append("Adjust camera angle or move closer to focus on crop field")
            adjustments.append({"action": "adjust_angle", "value": "downward", "type": "coverage"})
            priority = max(priority, 2)
        
        # Texture adjustments
        if "Low Texture Detail" in analysis["texture_variance"][0]:
            feedback.append("Decrease altitude by 0.5-1.0m for better crop detail detection")
            adjustments.append({"action": "decrease_altitude", "value": 0.75, "type": "detail"})
            priority = max(priority, 2)
        
        # Noise adjustments
        if "High Noise" in analysis["noise"][0]:
            feedback.append("Increase altitude slightly to reduce noise")
            adjustments.append({"action": "increase_altitude", "value": 0.5, "type": "noise"})
            priority = max(priority, 1)
        
        # Crop health adjustments
        if "Poor Health" in analysis["crop_health"][0]:
            feedback.append("Focus on this area for detailed disease monitoring")
            priority = max(priority, 2)
        
        if not feedback:
            feedback.append("Optimal footage quality for crop analysis")
            priority = 0
        
        return feedback, priority, adjustments
    
    def calculate_overall_quality_score(self, analysis):
        """Calculate overall quality score (0-100)"""
        scores = []
        
        # Weighted scoring based on importance for crop monitoring
        weights = {
            "sharpness": 0.20,
            "brightness": 0.15,
            "contrast": 0.10,
            "green_coverage": 0.15,
            "texture_variance": 0.10,
            "noise": 0.05,
            "crop_health": 0.25
        }
        
        for metric, weight in weights.items():
            if metric in analysis:
                if metric == "crop_health":
                    # Crop health is already normalized (0-1)
                    score = analysis[metric][1] * 100
                else:
                    score = self._metric_to_score(analysis[metric][0])
                scores.append(score * weight)
        
        return sum(scores) if scores else 0
    
    def _metric_to_score(self, status):
        """Convert status to numerical score"""
        score_map = {
            "Too Dark": 30, "Too Bright": 40, "Optimal Brightness": 100, "Acceptable Brightness": 80,
            "Low Contrast": 40, "Good Contrast": 80, "High Contrast": 90,
            "Blurry": 20, "Good Sharpness": 90, "Very Sharp": 100,
            "Low Crop Coverage": 30, "Good Crop Coverage": 80, "High Crop Coverage": 90,
            "Low Texture Detail": 40, "Good Texture Detail": 80, "High Texture Detail": 90,
            "Low Noise": 90, "Acceptable Noise": 70, "High Noise": 40
        }
        return score_map.get(status, 50)
    
    def log_analysis(self, analysis, feedback, priority, quality_score):
        """Log analysis results for drone control system"""
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "frame_count": self.frame_count,
            "crop_type": self.crop_type,
            "weather_condition": self.weather_condition,
            "quality_score": quality_score,
            "priority": priority,
            "analysis": analysis,
            "feedback": feedback,
            "recommendations": self._generate_drone_commands(priority, feedback)
        }
        
        # Save to file for drone control system
        self._save_to_file(log_entry)
        
        return log_entry
    
    def _generate_drone_commands(self, priority, feedback):
        """Generate specific drone control commands"""
        commands = {
            "priority": priority,
            "actions": []
        }
        
        if priority == 0:
            commands["actions"].append({"command": "maintain_position", "reason": "Optimal quality achieved"})
        elif priority >= 3:
            commands["actions"].append({"command": "immediate_adjustment", "reason": "Critical quality issues"})
        elif priority >= 2:
            commands["actions"].append({"command": "gradual_adjustment", "reason": "Moderate quality issues"})
        else:
            commands["actions"].append({"command": "fine_tune", "reason": "Minor quality issues"})
        
        return commands
    
    def _save_to_file(self, log_entry):
        """Save analysis results to file for drone control system"""
        filename = f"crop_quality_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(log_entry, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save analysis log: {e}")

def main():
    """Main function"""
    # Initialize analyzer with crop type and weather condition
    analyzer = CropFieldQualityAnalyzer(crop_type="general", weather_condition="clear")
    
    # Initialize camera (0 for USB webcam, adjust for Pi Camera if needed)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    print("Crop Field Quality Analysis Started")
    print("Press 'q' to quit, 's' to save current frame")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            
            analyzer.frame_count += 1
            
            # Analyze frame quality
            analysis = analyzer.analyze_frame_quality(frame)
            
            # Get drone positioning feedback
            feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
            
            # Calculate overall quality score
            quality_score = analyzer.calculate_overall_quality_score(analysis)
            
            # Log analysis for drone control
            log_entry = analyzer.log_analysis(analysis, feedback, priority, quality_score)
            
            # Display results on frame
            display_results(frame, analysis, feedback, priority, quality_score, analyzer)
            
            # Show the frame
            cv2.imshow("Crop Field Quality Analysis", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                save_frame(frame, analysis, quality_score)
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Analysis completed.")

def display_results(frame, analysis, feedback, priority, quality_score, analyzer=None):
    """Display analysis results on the frame with height information"""
    # Create overlay for better visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (500, 350), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Display quality score prominently
    color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
    cv2.putText(frame, f"Quality Score: {quality_score:.1f}/100", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Display priority
    priority_color = (0, 255, 0) if priority == 0 else (0, 255, 255) if priority <= 2 else (0, 0, 255)
    cv2.putText(frame, f"Priority: {priority}", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
    
    # Display height information
    y_pos = 90
    if analyzer and analyzer.drone_height is not None:
        height_color = (0, 255, 0)  # Green for height info
        cv2.putText(frame, f"Current Height: {analyzer.drone_height:.1f}m", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, height_color, 2)
        y_pos += 30
        
        optimal_height = analyzer.crop_params["optimal_height"]
        cv2.putText(frame, f"Optimal Height: {optimal_height:.1f}m", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, height_color, 2)
        y_pos += 30
        
        # Height status
        height_feedback = analyzer.get_height_feedback()
        if "Optimal" in height_feedback:
            status_color = (0, 255, 0)  # Green
        elif "Too high" in height_feedback or "Too low" in height_feedback:
            status_color = (0, 0, 255)  # Red
        else:
            status_color = (0, 255, 255)  # Yellow
        
        cv2.putText(frame, f"Height Status: {height_feedback.split('(')[0].strip()}", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
        y_pos += 30
    else:
        cv2.putText(frame, "Height: Not Available", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128, 128, 128), 2)
        y_pos += 30
    
    # Display metrics
    metrics = ["brightness", "contrast", "sharpness", "green_coverage", "crop_health"]
    for metric in metrics:
        if metric in analysis:
            status, value = analysis[metric]
            if "Good" in status or "Optimal" in status or "Excellent" in status:
                color = (0, 255, 0)
            elif "Poor" in status or "Low" in status or "Blurry" in status:
                color = (0, 0, 255)
            else:
                color = (0, 255, 255)
            cv2.putText(frame, f"{metric.replace('_', ' ').title()}: {status}", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 25
    
    # Display feedback
    y_pos += 10
    for i, msg in enumerate(feedback[:2]):  # Show first 2 feedback messages
        cv2.putText(frame, msg, (10, y_pos + i*20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def save_frame(frame, analysis, quality_score):
    """Save current frame with analysis data"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"crop_frame_{timestamp}_quality_{quality_score:.1f}.jpg"
    
    # Add analysis text to saved frame
    save_frame = frame.copy()
    cv2.putText(save_frame, f"Quality: {quality_score:.1f}", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imwrite(filename, save_frame)
    print(f"Frame saved as {filename}")

if __name__ == "__main__":
    main()