import cv2
import numpy as np
import json
import time
from datetime import datetime
import os

class CropFieldQualityAnalyzer:
    def __init__(self, crop_type="general", weather_condition="clear"):
        """
        Initialize analyzer with crop-specific parameters
        
        Args:
            crop_type: Type of crop (wheat, corn, rice, cotton, etc.)
            weather_condition: Current weather (clear, cloudy, overcast, etc.)
        """
        self.crop_type = crop_type
        self.weather_condition = weather_condition
        self.frame_count = 0
        self.quality_history = []
        
        # Crop-specific parameters
        self.crop_params = self._get_crop_parameters()
        
        # Weather-based adjustments
        self.weather_adjustments = self._get_weather_adjustments()
        
        # Quality thresholds (adjusted based on crop and weather)
        self.thresholds = self._calculate_thresholds()
        
    def _get_crop_parameters(self):
        """Define crop-specific analysis parameters"""
        crop_params = {
            "wheat": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 1.2,
                "detail_importance": "high",
                "optimal_height": 3.0,  # meters
                "min_resolution": 0.5   # cm per pixel
            },
            "corn": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                "optimal_height": 4.0,
                "min_resolution": 0.8
            },
            "rice": {
                "green_range": ([35, 60, 60], [85, 255, 255]),
                "texture_sensitivity": 1.1,
                "detail_importance": "high",
                "optimal_height": 2.5,
                "min_resolution": 0.4
            },
            "cotton": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 0.9,
                "detail_importance": "medium",
                "optimal_height": 3.5,
                "min_resolution": 0.6
            },
            "general": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                "optimal_height": 3.0,
                "min_resolution": 0.5
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
        
        return {
            "brightness": (brightness_score, brightness),
            "contrast": (contrast_score, contrast),
            "sharpness": (sharpness_score, sharpness),
            "green_coverage": (coverage_score, green_coverage),
            "texture_variance": (texture_score, texture_variance),
            "focus": (focus_score, focus_score),
            "noise": (noise_score, noise_level)
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
        
        # Brightness adjustments
        if "Too Dark" in analysis["brightness"][0]:
            feedback.append("Decrease altitude by 0.5-1.0m for better lighting")
            adjustments.append({"action": "decrease_altitude", "value": 0.75})
            priority = max(priority, 2)
        elif "Too Bright" in analysis["brightness"][0]:
            feedback.append("Increase altitude by 0.5-1.0m to reduce overexposure")
            adjustments.append({"action": "increase_altitude", "value": 0.75})
            priority = max(priority, 2)
        
        # Sharpness adjustments
        if "Blurry" in analysis["sharpness"][0]:
            feedback.append("Decrease altitude by 1.0-1.5m for sharper crop details")
            adjustments.append({"action": "decrease_altitude", "value": 1.25})
            priority = max(priority, 3)
        
        # Coverage adjustments
        if "Low Crop Coverage" in analysis["green_coverage"][0]:
            feedback.append("Adjust camera angle or move closer to focus on crop field")
            adjustments.append({"action": "adjust_angle", "value": "downward"})
            priority = max(priority, 2)
        
        # Texture adjustments
        if "Low Texture Detail" in analysis["texture_variance"][0]:
            feedback.append("Decrease altitude by 0.5-1.0m for better crop detail detection")
            adjustments.append({"action": "decrease_altitude", "value": 0.75})
            priority = max(priority, 2)
        
        # Noise adjustments
        if "High Noise" in analysis["noise"][0]:
            feedback.append("Increase altitude slightly to reduce noise")
            adjustments.append({"action": "increase_altitude", "value": 0.5})
            priority = max(priority, 1)
        
        if not feedback:
            feedback.append("Optimal footage quality for crop analysis")
            priority = 0
        
        return feedback, priority, adjustments
    
    def calculate_overall_quality_score(self, analysis):
        """Calculate overall quality score (0-100)"""
        scores = []
        
        # Weighted scoring based on importance for crop monitoring
        weights = {
            "sharpness": 0.25,
            "brightness": 0.20,
            "contrast": 0.15,
            "green_coverage": 0.20,
            "texture_variance": 0.15,
            "noise": 0.05
        }
        
        for metric, weight in weights.items():
            if metric in analysis:
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
            display_results(frame, analysis, feedback, priority, quality_score)
            
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

def analyze_frame_quality(frame):
    """Wrapper function for backward compatibility"""
    analyzer = CropFieldQualityAnalyzer()
    return analyzer.analyze_frame_quality(frame)

def get_drone_position_feedback(analysis):
    """Wrapper function for backward compatibility"""
    analyzer = CropFieldQualityAnalyzer()
    return analyzer.get_drone_position_feedback(analysis)

def calculate_overall_quality_score(analysis):
    """Wrapper function for backward compatibility"""
    analyzer = CropFieldQualityAnalyzer()
    return analyzer.calculate_overall_quality_score(analysis)

def log_analysis(analysis, feedback, priority, quality_score):
    """Wrapper function for backward compatibility"""
    analyzer = CropFieldQualityAnalyzer()
    return analyzer.log_analysis(analysis, feedback, priority, quality_score)

def display_results(frame, analysis, feedback, priority, quality_score):
    """Display analysis results on the frame"""
    # Create overlay for better visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (400, 280), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    # Display quality score prominently
    color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
    cv2.putText(frame, f"Quality Score: {quality_score:.1f}/100", 
               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Display priority
    priority_color = (0, 255, 0) if priority == 0 else (0, 255, 255) if priority <= 2 else (0, 0, 255)
    cv2.putText(frame, f"Priority: {priority}", 
               (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, priority_color, 2)
    
    # Display metrics
    y_pos = 90
    for metric, (status, value) in analysis.items():
        if metric in ["brightness", "contrast", "sharpness", "green_coverage"]:
            color = (0, 255, 0) if "Good" in status or "Optimal" in status else (0, 0, 255)
            cv2.putText(frame, f"{metric.title()}: {status} ({value:.1f})", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            y_pos += 25
    
    # Display feedback
    y_pos += 10
    for i, msg in enumerate(feedback[:3]):  # Show first 3 feedback messages
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