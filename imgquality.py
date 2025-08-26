#!/usr/bin/env python3
"""
AI-Enhanced Image Quality Analysis for Crop Monitoring
Uses OpenCV + TensorFlow Lite for intelligent crop detection and quality assessment
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
import os
import subprocess
try:
    import tflite_runtime.interpreter as tflite
    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
import requests
import tempfile
import zipfile

class CropFieldQualityAnalyzer:
    def __init__(self, crop_type="general", weather_condition="clear", drone_height=None, close_up_mode=False):
        """
        Initialize analyzer with crop-specific parameters and AI models
        
        Args:
            crop_type: Type of crop (wheat, corn, rice, cotton, etc.)
            weather_condition: Current weather (clear, cloudy, overcast, etc.)
            drone_height: Current drone height in meters (from telemetry)
            close_up_mode: Enable close-up mode for table/desk scenarios
        """
        self.crop_type = crop_type
        self.weather_condition = weather_condition
        # self.drone_height = drone_height  # Commented out height functionality
        self.frame_count = 0
        self.quality_history = []
        self.close_up_mode = close_up_mode
        
        # Crop-specific parameters
        self.crop_params = self._get_crop_parameters()
        
        # Weather-based adjustments
        self._get_weather_adjustments()
        
        # Quality thresholds (adjusted based on crop, weather, and close-up mode)
        self.thresholds = self._calculate_thresholds()
        
        # Initialize TensorFlow Lite models
        self.tflite_models = {}
        self._initialize_ai_models()
        
        # AI detection results cache
        self.detection_cache = {}
        self.cache_valid_frames = 30  # Cache results for 30 frames
        
    # def update_drone_height(self, height):  # Commented out height functionality
    #     """Update current drone height from telemetry"""
    #     self.drone_height = height
    #     print(f"Drone height updated: {height}m")
    
    # def get_height_feedback(self):  # Commented out height functionality
    #     """Get height-specific feedback based on current altitude"""
    #     if self.drone_height is None:
    #         return "Height data not available - check drone telemetry"
    #     
    #     optimal_height = self.crop_params["optimal_height"]
    #     height_diff = self.drone_height - optimal_height
    #     
    #     if abs(height_diff) < 0.5:
    #         return f"Optimal height: {self.drone_height:.1f}m (within 0.5m of target)"
    #     elif height_diff > 0:
    #         return f"Too high: {self.drone_height:.1f}m (decrease by {height_diff:.1f}m to reach {optimal_height}m)"
    #     else:
    #         return f"Too low: {self.drone_height:.1f}m (increase by {abs(height_diff):.1f}m to reach {optimal_height}m)"
    
    # def get_height_recommendation(self):  # Commented out height functionality
    #     """Get specific height adjustment recommendation"""
    #     if self.drone_height is None:
    #         return None
    #     
    #     optimal_height = self.crop_params["optimal_height"]
    #     height_diff = self.drone_height - optimal_height
    #     
    #     if abs(height_diff) < 0.5:
    #         return {"action": "maintain_height", "reason": "Optimal altitude achieved"}
    #     elif height_diff > 0:
    #         return {"action": "decrease_height", "value": height_diff, "reason": f"Too high for {self.crop_type}"}
    #     else:
    #         return {"action": "increase_height", "value": abs(height_diff), "reason": f"Too low for {self.crop_type}"}
    
    def _get_crop_parameters(self):
        """Define crop-specific analysis parameters"""
        crop_params = {
            "wheat": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 1.2,
                "detail_importance": "high",
                # "optimal_height": 3.0,  # Commented out height functionality
                "min_resolution": 0.5,   # cm per pixel
                # "height_tolerance": 0.5   # Commented out height functionality
            },
            "corn": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                # "optimal_height": 4.0,  # Commented out height functionality
                "min_resolution": 0.8,
                # "height_tolerance": 0.8  # Commented out height functionality
            },
            "rice": {
                "green_range": ([35, 60, 60], [85, 255, 255]),
                "texture_sensitivity": 1.1,
                "detail_importance": "high",
                # "optimal_height": 2.5,  # Commented out height functionality
                "min_resolution": 0.4,
                # "height_tolerance": 0.4  # Commented out height functionality
            },
            "cotton": {
                "green_range": ([35, 40, 40], [85, 255, 255]),
                "texture_sensitivity": 0.9,
                "detail_importance": "medium",
                # "optimal_height": 3.5,  # Commented out height functionality
                "min_resolution": 0.6,
                # "height_tolerance": 0.6  # Commented out height functionality
            },
            "general": {
                "green_range": ([35, 50, 50], [85, 255, 255]),
                "texture_sensitivity": 1.0,
                "detail_importance": "medium",
                # "optimal_height": 3.0,  # Commented out height functionality
                "min_resolution": 0.5,
                # "height_tolerance": 0.5  # Commented out height functionality
            }
        }
        return crop_params.get(self.crop_type, crop_params["general"])
    
    def _initialize_ai_models(self):
        """Initialize TensorFlow Lite models for crop detection and quality assessment"""
        if not TFLITE_AVAILABLE:
            return
        
        try:
            # Download and setup pre-trained models if not available
            self._setup_crop_detection_model()
            self._setup_quality_assessment_model()
        except Exception as e:
            pass  # Silently fall back to traditional methods
    
    def _setup_crop_detection_model(self):
        """Setup crop detection model (using MobileNet SSD for object detection)"""
        if not TFLITE_AVAILABLE:
            return
            
        model_path = "crop_detection_model.tflite"
        
        if not os.path.exists(model_path):
            self._download_crop_model()
        
        if os.path.exists(model_path):
            try:
                interpreter = tflite.Interpreter(model_path=model_path)
                interpreter.allocate_tensors()
                self.tflite_models['crop_detection'] = interpreter
            except Exception as e:
                pass
    
    def _setup_quality_assessment_model(self):
        """Setup quality assessment model (using EfficientNet for image classification)"""
        if not TFLITE_AVAILABLE:
            return
            
        model_path = "quality_assessment_model.tflite"
        
        if not os.path.exists(model_path):
            self._download_quality_model()
        
        if os.path.exists(model_path):
            try:
                interpreter = tflite.Interpreter(model_path=model_path)
                interpreter.allocate_tensors()
                self.tflite_models['quality_assessment'] = interpreter
            except Exception as e:
                pass
    
    def _download_crop_model(self):
        """Download pre-trained crop detection model"""
        # For now, we'll use a placeholder. In production, download from your model repository
        pass
    
    def _download_quality_model(self):
        """Download pre-trained quality assessment model"""
        # For now, we'll use a placeholder. In production, download from your model repository
        pass
    
    def _get_weather_adjustments(self):
        """Adjust thresholds based on weather conditions"""
        adjustments = {
            "clear": {"brightness_mult": 1.0, "contrast_mult": 1.0, "sharpness_mult": 1.0},
            "cloudy": {"brightness_mult": 0.8, "contrast_mult": 1.2, "sharpness_mult": 0.9},
            "overcast": {"brightness_mult": 0.7, "contrast_mult": 1.3, "sharpness_mult": 0.8},
            "sunny": {"brightness_mult": 1.2, "contrast_mult": 0.9, "sharpness_mult": 1.1}
        }
        return adjustments.get(self.weather_condition, adjustments["clear"])
    
    def _auto_detect_close_up_mode(self, gray):
        """Auto-detect if we're in close-up mode based on image characteristics"""
        try:
            # Calculate image statistics
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            
            # Close-up images typically have:
            # - Lower overall brightness (closer to objects)
            # - Higher contrast (more detail visible)
            # - Different texture patterns
            
            # Adjust thresholds based on detected mode
            if mean_intensity < 100 and std_intensity > 40:
                if not self.close_up_mode:
                    self.close_up_mode = True
                    self.thresholds = self._calculate_thresholds()  # Recalculate with new mode
            elif mean_intensity > 120 and std_intensity < 35:
                if self.close_up_mode:
                    self.close_up_mode = False
                    self.thresholds = self._calculate_thresholds()  # Recalculate with new mode
                    
        except Exception as e:
            pass  # Silently fail if detection fails
    
    def _calculate_thresholds(self):
        """Calculate dynamic thresholds based on crop, weather, and close-up mode"""
        adj = self.weather_adjustments
        
        if self.close_up_mode:
            # Close-up mode thresholds (for table/desk scenarios)
            return {
                "brightness": {
                    "min": 30 * adj["brightness_mult"],  # Very low for close-up
                    "max": 220 * adj["brightness_mult"],  # Higher range for close-up
                    "optimal": 100 * adj["brightness_mult"]  # Lower optimal for close-up
                },
                "contrast": {
                    "min": 15 * adj["contrast_mult"],  # Lower for close-up
                    "optimal": 30 * adj["contrast_mult"]  # Lower optimal for close-up
                },
                "sharpness": {
                    "min": 20 * adj["sharpness_mult"],  # Much lower for close-up
                    "optimal": 80 * adj["sharpness_mult"]  # Lower optimal for close-up
                },
                "green_coverage": {
                    "min": 0.05,  # Very low for close-up (table surfaces)
                    "optimal": 0.3  # Lower optimal for close-up
                },
                "texture_variance": {
                    "min": 20 * self.crop_params["texture_sensitivity"],  # Lower for close-up
                    "optimal": 60 * self.crop_params["texture_sensitivity"]  # Lower optimal for close-up
                }
            }
        else:
            # Normal mode thresholds (for crop field scenarios)
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
        """Comprehensive frame quality analysis for crop monitoring with AI enhancement"""
        # Traditional OpenCV analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Auto-detect close-up mode based on image characteristics
        if self.frame_count % 30 == 0:  # Check every 30 frames
            self._auto_detect_close_up_mode(gray)
        
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
        
        # 9. AI-Powered Analysis (if available)
        ai_crops = None
        ai_quality = None
        
        if self.frame_count % 5 == 0:  # Run AI analysis every 5 frames for performance
            try:
                ai_crops = self.detect_crops_ai(frame)
                ai_quality = self.assess_quality_ai(frame)
                
                # Cache AI results
                self.detection_cache = {
                    'crops': ai_crops,
                    'quality': ai_quality,
                    'frame': self.frame_count
                }
            except Exception as e:
                pass
        
        # Use cached AI results if available
        if self.detection_cache and (self.frame_count - self.detection_cache['frame']) < self.cache_valid_frames:
            ai_crops = self.detection_cache['crops']
            ai_quality = self.detection_cache['quality']
        
        # Combine traditional and AI analysis
        combined_analysis = {
            "brightness": (brightness_score, brightness),
            "contrast": (contrast_score, contrast),
            "sharpness": (sharpness_score, sharpness),
            "green_coverage": (coverage_score, green_coverage),
            "texture_variance": (texture_score, texture_variance),
            "focus": (focus_score, focus_score),
            "noise": (noise_score, noise_level),
            "crop_health": (crop_health["status"], crop_health["score"])
        }
        
        # Add AI results if available
        if ai_crops:
            combined_analysis["ai_crops"] = ai_crops
        if ai_quality:
            combined_analysis["ai_quality"] = ai_quality
        
        return combined_analysis
    
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
    
    def detect_crops_ai(self, frame):
        """AI-powered crop detection using TensorFlow Lite"""
        if 'crop_detection' not in self.tflite_models:
            return self._fallback_crop_detection(frame)
        
        try:
            # Preprocess frame for AI model
            input_tensor = self._preprocess_frame_for_ai(frame)
            
            # Run inference
            interpreter = self.tflite_models['crop_detection']
            interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_tensor)
            interpreter.invoke()
            
            # Get detection results
            detection_boxes = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
            detection_classes = interpreter.get_tensor(interpreter.get_output_details()[1]['index'])
            detection_scores = interpreter.get_tensor(interpreter.get_output_details()[2]['index'])
            
            # Process detections
            crops = self._process_crop_detections(frame, detection_boxes, detection_classes, detection_scores)
            
            return crops
            
        except Exception as e:
            return self._fallback_crop_detection(frame)
    
    def assess_quality_ai(self, frame):
        """AI-powered quality assessment using TensorFlow Lite"""
        if 'quality_assessment' not in self.tflite_models:
            return self._fallback_quality_assessment(frame)
        
        try:
            # Preprocess frame for AI model
            input_tensor = self._preprocess_frame_for_ai(frame)
            
            # Run inference
            interpreter = self.tflite_models['quality_assessment']
            interpreter.set_tensor(interpreter.get_input_details()[0]['index'], input_tensor)
            interpreter.invoke()
            
            # Get quality assessment results
            quality_scores = interpreter.get_tensor(interpreter.get_output_details()[0]['index'])
            
            # Process quality scores
            quality_assessment = self._process_quality_scores(quality_scores)
            
            return quality_assessment
            
        except Exception as e:
            return self._fallback_quality_assessment(frame)
    
    def _preprocess_frame_for_ai(self, frame):
        """Preprocess frame for AI model input"""
        # Resize to model input size (typically 224x224 or 299x299)
        input_size = (224, 224)
        resized = cv2.resize(frame, input_size)
        
        # Convert BGR to RGB
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        # Normalize pixel values to [0, 1]
        normalized = rgb.astype(np.float32) / 255.0
        
        # Add batch dimension
        batched = np.expand_dims(normalized, axis=0)
        
        return batched
    
    def _process_crop_detections(self, frame, boxes, classes, scores):
        """Process AI crop detection results"""
        crops = []
        height, width = frame.shape[:2]
        
        for i in range(len(scores[0])):
            if scores[0][i] > 0.5:  # Confidence threshold
                box = boxes[0][i]
                class_id = int(classes[0][i])
                
                # Convert normalized coordinates to pixel coordinates
                ymin, xmin, ymax, xmax = box
                x1 = int(xmin * width)
                y1 = int(ymin * height)
                x2 = int(xmax * width)
                y2 = int(ymax * height)
                
                crop_info = {
                    'bbox': (x1, y1, x2, y2),
                    'class_id': class_id,
                    'confidence': float(scores[0][i]),
                    'crop_type': self._get_crop_class_name(class_id)
                }
                
                crops.append(crop_info)
        
        return crops
    
    def _process_quality_scores(self, scores):
        """Process AI quality assessment scores"""
        # Assuming the model outputs scores for different quality aspects
        quality_aspects = ['overall', 'sharpness', 'brightness', 'contrast', 'crop_health']
        
        if len(scores[0]) >= len(quality_aspects):
            quality_assessment = {}
            for i, aspect in enumerate(quality_aspects):
                quality_assessment[aspect] = float(scores[0][i])
            return quality_assessment
        else:
            # Fallback: use overall score
            return {'overall': float(scores[0][0])}
    
    def _get_crop_class_name(self, class_id):
        """Get crop class name from class ID"""
        crop_classes = {
            0: 'wheat', 1: 'corn', 2: 'rice', 3: 'cotton', 4: 'soybean',
            5: 'barley', 6: 'oats', 7: 'rye', 8: 'sorghum', 9: 'millet'
        }
        return crop_classes.get(class_id, 'unknown_crop')
    
    def _fallback_crop_detection(self, frame):
        """Fallback crop detection using OpenCV color-based methods"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Use existing crop coverage analysis
        green_coverage = self._analyze_crop_coverage(hsv)
        
        # Create a simple crop detection result
        height, width = frame.shape[:2]
        crops = [{
            'bbox': (0, 0, width, height),
            'class_id': 0,
            'confidence': 0.8,
            'crop_type': self.crop_type,
            'coverage': green_coverage
        }]
        
        return crops
    
    def _fallback_quality_assessment(self, frame):
        """Fallback quality assessment using traditional OpenCV methods"""
        # Use basic analysis methods to avoid recursion
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Basic metrics
        brightness = np.mean(gray)
        contrast = np.std(gray)
        sharpness = self._analyze_sharpness(gray)
        green_coverage = self._analyze_crop_coverage(hsv)
        crop_health = self._analyze_crop_health(hsv)
        
        # Convert to AI-style output format
        quality_assessment = {
            'overall': 0.7,  # Default moderate quality
            'sharpness': min(sharpness / 200.0, 1.0),  # Normalize sharpness
            'brightness': min(max(brightness / 255.0, 0.0), 1.0),  # Normalize brightness
            'contrast': min(max(contrast / 100.0, 0.0), 1.0),  # Normalize contrast
            'crop_health': crop_health["score"]  # Already normalized 0-1
        }
        
        return quality_assessment
    
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
        
        # Height-based adjustments (highest priority) - Commented out height functionality
        # height_rec = self.get_height_recommendation()
        # if height_rec:
        #     if height_rec["action"] == "decrease_height":
        #         feedback.append(f"Decrease altitude by {height_rec['value']:.1f}m to {height_rec['reason']}")
        #         adjustments.append({"action": "decrease_height", "value": height_rec["value"], "type": "height"})
        #         priority = max(priority, 3)
        #     elif height_rec["action"] == "increase_height":
        #         feedback.append(f"Increase altitude by {height_rec['value']:.1f}m to {height_rec['reason']}")
        #         adjustments.append({"action": "increase_height", "value": height_rec["value"], "type": "height"})
        #         priority = max(priority, 3)
        #     else:
        #         feedback.append(f"Optimal height: {self.drone_height:.1f}m")
        
        # Smart positioning logic based on current quality
        quality_score = self.calculate_overall_quality_score(analysis)
        
        # If quality is already good, don't recommend moving closer
        if quality_score >= 80:
            feedback.append("Excellent quality! Maintain current position")
            priority = 0
            return feedback, priority, adjustments
        elif quality_score >= 70:
            feedback.append("Good quality. Slight adjustments possible")
            priority = 1
        elif quality_score >= 50:
            feedback.append("Moderate quality. Consider adjustments")
            priority = 2
        else:
            feedback.append("Poor quality. Significant adjustments needed")
            priority = 3
        
        # Brightness adjustments - only if significantly off
        if "Too Dark" in analysis["brightness"][0]:
            feedback.append("Move closer by 0.5-1.0m for better lighting")
            adjustments.append({"action": "decrease_altitude", "value": 0.75, "type": "lighting"})
        elif "Too Bright" in analysis["brightness"][0]:
            feedback.append("Move farther by 0.5-1.0m to reduce overexposure")
            adjustments.append({"action": "increase_altitude", "value": 0.75, "type": "lighting"})
        
        # Sharpness adjustments - only if very blurry
        if "Blurry" in analysis["sharpness"][0]:
            feedback.append("Move closer by 1.0-1.5m for sharper crop details")
            adjustments.append({"action": "decrease_altitude", "value": 1.25, "type": "focus"})
        elif "Very Sharp" in analysis["sharpness"][0]:
            feedback.append("Sharpness is excellent! Consider moving slightly farther for wider coverage")
            adjustments.append({"action": "increase_altitude", "value": 0.5, "type": "coverage"})
        
        # Coverage adjustments - only if coverage is very low
        if "Low Crop Coverage" in analysis["green_coverage"][0]:
            feedback.append("Adjust camera angle downward or move closer to focus on crop field")
            adjustments.append({"action": "adjust_angle", "value": "downward", "type": "coverage"})
        
        # Texture adjustments - only if texture is very poor
        if "Low Texture Detail" in analysis["texture_variance"][0]:
            feedback.append("Move closer by 0.5-1.0m for better crop detail detection")
            adjustments.append({"action": "decrease_altitude", "value": 0.75, "type": "detail"})
        
        # Noise adjustments - only if noise is very high
        if "High Noise" in analysis["noise"][0]:
            feedback.append("Move slightly farther to reduce noise")
            adjustments.append({"action": "increase_altitude", "value": 0.5, "type": "noise"})
        
        # Crop health adjustments
        if "Poor Health" in analysis["crop_health"][0]:
            feedback.append("Focus on this area for detailed disease monitoring")
        
        # If no specific adjustments needed but quality is moderate
        if not adjustments and quality_score < 70:
            feedback.append("Quality is acceptable. Fine-tune position if needed")
        
        return feedback, priority, adjustments
    
    def send_flight_parameters(self, analysis):
        """Send optimal altitude and polygon to flight maneuvering script"""
        
        # Get optimal altitude based on quality
        quality_score = self.calculate_overall_quality_score(analysis)
        
        if quality_score >= 85:
            altitude = 4.0  # Excellent quality - can go higher
        elif quality_score >= 70:
            altitude = 3.5  # Good quality - maintain height
        elif quality_score >= 50:
            altitude = 3.0  # Moderate quality - move closer
        else:
            altitude = 2.5  # Poor quality - move much closer
        
        # Define your crop field polygon (replace with your actual coordinates)
        polygon = [(23.8103, 90.4125), (23.8103, 90.4145), 
                   (23.8083, 90.4145), (23.8083, 90.4125)]
        
        try:
            # Send to flight maneuvering script
            result = subprocess.run([
                "python3", 
                "flight_maneuvering.py", 
                str(altitude), 
                str(polygon)
            ], capture_output=True, text=True)
            
            return True
            
        except Exception as e:
            return False
    
    def send_analysis_data(self, analysis, quality_score, priority):
        """Send key analysis values via subprocess"""
        try:
            # Extract key values
            crop_name = self.crop_type
            crop_quality = analysis.get('crop_health', [None, 0])[1] * 100 if 'crop_health' in analysis else 0
            footage_quality = quality_score
            action_needed = "optimal" if priority == 0 else "adjust" if priority <= 2 else "move_closer"
            current_height = getattr(self, 'drone_height', None) or "unknown"
            
            # Create data dictionary
            analysis_data = {
                "crop_name": crop_name,
                "crop_quality": round(crop_quality, 1),
                "footage_quality": round(footage_quality, 1),
                "action_needed": action_needed,
                "current_height": current_height,
                "timestamp": time.strftime('%H:%M:%S'),
                "frame_count": self.frame_count
            }
            
            # Save to single file
            self.save_analysis_to_file(analysis_data)
            
            # Send via subprocess (uncomment and modify as needed)
            # Example: Send to another script
            # result = subprocess.run(["python3", "your_script.py", json.dumps(analysis_data)], capture_output=True, text=True)
            
            # Example: Send to a web service
            # result = subprocess.run(["curl", "-X", "POST", "-H", "Content-Type: application/json", "-d", json.dumps(analysis_data), "http://your-api.com/endpoint"], capture_output=True, text=True)
            
            # Example: Send to a local service
            # result = subprocess.run(["echo", json.dumps(analysis_data)], capture_output=True, text=True)
            
            return True, analysis_data
            
        except Exception as e:
            return False, None
    
    def save_analysis_to_file(self, data):
        """Save analysis data to a single file"""
        try:
            filename = "crop_analysis_data.json"
            
            # Load existing data if file exists
            existing_data = []
            if os.path.exists(filename):
                try:
                    with open(filename, 'r') as f:
                        existing_data = json.load(f)
                except:
                    existing_data = []
            
            # Add new data
            existing_data.append(data)
            
            # Keep only last 100 entries to prevent file from getting too large
            if len(existing_data) > 100:
                existing_data = existing_data[-100:]
            
            # Save back to file
            with open(filename, 'w') as f:
                json.dump(existing_data, f, indent=2)
                
        except Exception as e:
            pass  # Silently fail if can't save
    
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
        
        # Save to file for drone control system - Commented out to prevent file spam
        # self._save_to_file(log_entry)
        
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
            pass

def main():
    """Main function with AI-enhanced crop quality analysis"""
    print("🌾 Crop Quality Analysis")
    print("=" * 30)
    
    # Initialize analyzer with crop type and weather condition, enable close-up mode for table scenarios
    analyzer = CropFieldQualityAnalyzer(crop_type="general", weather_condition="clear", close_up_mode=True)
    
    # Initialize camera (0 for USB webcam, adjust for Pi Camera if needed)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Error: Could not open camera.")
        return
    
    # Set camera properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("📹 Camera ready")
    print("🌾 Crop:", analyzer.crop_type.title())
    print("\n🎯 Analysis started - Press 'q' to quit, 'i' for status")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Error: Could not read frame.")
                break
            
            analyzer.frame_count += 1
            
            # Analyze frame quality with AI enhancement
            analysis = analyzer.analyze_frame_quality(frame)
            
            # Get drone positioning feedback
            feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
            
            # Calculate overall quality score
            quality_score = analyzer.calculate_overall_quality_score(analysis)
            
            # Log analysis for drone control
            log_entry = analyzer.log_analysis(analysis, feedback, priority, quality_score)
            
            # Display simplified status
            crop_health_score = analysis.get('crop_health', [None, 0])[1] * 100 if 'crop_health' in analysis else 0
            
            print(f"[{time.strftime('%H:%M:%S')}] 🌾 {analyzer.crop_type.title()} | 📹 {quality_score:.0f}/100 | 🌱 {crop_health_score:.0f}/100 | {'🟢 Optimal' if priority == 0 else '🟡 Adjust' if priority <= 2 else '🔴 Move Closer'}")
            
            # Save analysis data to file
            success, saved_data = analyzer.send_analysis_data(analysis, quality_score, priority)
            if success:
                print(f"💾 Saved: {saved_data['crop_name']} | Q:{saved_data['footage_quality']} | Action:{saved_data['action_needed']}")
            
            # Display results on frame
            display_results(frame, analysis, feedback, priority, quality_score, analyzer)
            
            # Show the frame
            cv2.imshow("🤖 AI-Enhanced Crop Quality Analysis", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('i'):
                # Show simplified info
                print(f"\n📊 Status: {analyzer.crop_type.title()} | Quality: {quality_score:.0f}/100 | Action: {'Optimal' if priority == 0 else 'Adjust' if priority <= 2 else 'Move Closer'}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("\n✅ Analysis completed")

def display_results(frame, analysis, feedback, priority, quality_score, analyzer=None):
    """Display simplified analysis results on the frame"""
    # Create overlay for better visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (400, 200), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    y_pos = 30
    
    # 1. Crop Name and Mode
    mode_text = " (Close-up)" if analyzer and analyzer.close_up_mode else ""
    cv2.putText(frame, f"Crop: {analyzer.crop_type.title() if analyzer else 'General'}{mode_text}", 
               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    y_pos += 35
    
    # 2. Footage Quality (Overall Quality Score)
    color = (0, 255, 0) if quality_score >= 80 else (0, 255, 255) if quality_score >= 60 else (0, 0, 255)
    cv2.putText(frame, f"Footage Quality: {quality_score:.0f}/100", 
               (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    y_pos += 35
    
    # 3. Crop Quality (Crop Health)
    if "crop_health" in analysis:
        crop_health_score = analysis['crop_health'][1] * 100
        crop_color = (0, 255, 0) if crop_health_score >= 80 else (0, 255, 255) if crop_health_score >= 60 else (0, 0, 255)
        cv2.putText(frame, f"Crop Quality: {crop_health_score:.0f}/100", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, crop_color, 2)
        y_pos += 35
    
    # 4. Height Information
    if analyzer and hasattr(analyzer, 'drone_height') and analyzer.drone_height is not None:
        cv2.putText(frame, f"Height: {analyzer.drone_height:.1f}m", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "Height: Not Available", 
                   (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
    y_pos += 35
    
    # 5. Action Required (Close/Far)
    if priority == 0:
        action_text = "Position: Optimal"
        action_color = (0, 255, 0)
    elif priority >= 3:
        action_text = "Action: Move Closer"
        action_color = (0, 0, 255)
    elif priority >= 2:
        action_text = "Action: Adjust Position"
        action_color = (0, 255, 255)
    else:
        action_text = "Action: Fine Tune"
        action_color = (0, 255, 255)
    
    cv2.putText(frame, action_text, (10, y_pos), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, action_color, 2)

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