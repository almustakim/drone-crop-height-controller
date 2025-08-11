#!/usr/bin/env python3
"""
Test script for Image Quality Analyzer
Tests core functionality without camera access
"""

import numpy as np
from imgquality import CropFieldQualityAnalyzer

def test_analyzer_initialization():
    """Test analyzer initialization"""
    print("Testing analyzer initialization...")
    
    try:
        # Test different crop types
        crops = ["wheat", "corn", "rice", "cotton", "general"]
        for crop in crops:
            analyzer = CropFieldQualityAnalyzer(crop_type=crop, weather_condition="clear")
            print(f"✓ {crop.title()} analyzer initialized successfully")
        
        # Test different weather conditions
        weathers = ["clear", "cloudy", "overcast", "sunny"]
        for weather in weathers:
            analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition=weather)
            print(f"✓ {weather.title()} weather analyzer initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Analyzer initialization failed: {e}")
        return False

def test_analysis_with_synthetic_image():
    """Test analysis with synthetic image"""
    print("\nTesting analysis with synthetic image...")
    
    try:
        # Create synthetic test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Initialize analyzer
        analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")
        
        # Analyze image
        analysis = analyzer.analyze_frame_quality(test_image)
        
        # Check analysis results
        expected_metrics = ["brightness", "contrast", "sharpness", "green_coverage", "texture_variance", "focus", "noise", "crop_health"]
        
        for metric in expected_metrics:
            if metric in analysis:
                status, value = analysis[metric]
                print(f"✓ {metric}: {status} ({value:.2f})")
            else:
                print(f"✗ {metric} missing from analysis")
        
        return True
        
    except Exception as e:
        print(f"✗ Analysis test failed: {e}")
        return False

def test_drone_feedback():
    """Test drone positioning feedback"""
    print("\nTesting drone positioning feedback...")
    
    try:
        # Create synthetic test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Initialize analyzer
        analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")
        
        # Analyze image
        analysis = analyzer.analyze_frame_quality(test_image)
        
        # Get drone feedback
        feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
        
        print(f"✓ Priority level: {priority}")
        print(f"✓ Feedback count: {len(feedback)}")
        print(f"✓ Adjustments count: {len(adjustments)}")
        
        for i, msg in enumerate(feedback):
            print(f"  {i+1}. {msg}")
        
        return True
        
    except Exception as e:
        print(f"✗ Drone feedback test failed: {e}")
        return False

def test_quality_scoring():
    """Test quality scoring system"""
    print("\nTesting quality scoring system...")
    
    try:
        # Create synthetic test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Initialize analyzer
        analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")
        
        # Analyze image
        analysis = analyzer.analyze_frame_quality(test_image)
        
        # Calculate quality score
        quality_score = analyzer.calculate_overall_quality_score(analysis)
        
        print(f"✓ Overall quality score: {quality_score:.1f}/100")
        
        # Check score range
        if 0 <= quality_score <= 100:
            print("✓ Quality score is within valid range (0-100)")
        else:
            print("✗ Quality score is outside valid range")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Quality scoring test failed: {e}")
        return False

def test_logging():
    """Test analysis logging"""
    print("\nTesting analysis logging...")
    
    try:
        # Create synthetic test image
        test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        # Initialize analyzer
        analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")
        
        # Analyze image
        analysis = analyzer.analyze_frame_quality(test_image)
        
        # Get drone feedback
        feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
        
        # Calculate quality score
        quality_score = analyzer.calculate_overall_quality_score(analysis)
        
        # Log analysis
        log_entry = analyzer.log_analysis(analysis, feedback, priority, quality_score)
        
        print(f"✓ Log entry created with timestamp: {log_entry['timestamp']}")
        print(f"✓ Log entry contains {len(log_entry)} fields")
        
        # Check required fields
        required_fields = ["timestamp", "frame_count", "crop_type", "weather_condition", "quality_score", "priority", "analysis", "feedback", "recommendations"]
        for field in required_fields:
            if field in log_entry:
                print(f"✓ {field} field present")
            else:
                print(f"✗ {field} field missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        return False

def main():
    """Main test function"""
    print("Image Quality Analyzer - Core Functionality Test")
    print("=" * 50)
    
    tests = [
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Image Analysis", test_analysis_with_synthetic_image),
        ("Drone Feedback", test_drone_feedback),
        ("Quality Scoring", test_quality_scoring),
        ("Analysis Logging", test_logging)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    total_tests = len(tests)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! The analyzer is working correctly.")
        print("\nYou can now run the full system with:")
        print("python3 imgquality.py")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    main() 