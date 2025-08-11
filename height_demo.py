#!/usr/bin/env python3
"""
Height Integration Demo for Image Quality Analyzer
Shows how to integrate drone height data with the system
"""

import numpy as np
from imgquality import CropFieldQualityAnalyzer

def simulate_drone_height():
    """Simulate drone height changes for demo"""
    heights = [2.0, 2.5, 3.0, 3.5, 4.0, 3.5, 3.0, 2.5, 2.0]
    for height in heights:
        yield height

def main():
    """Main demo function showing height integration"""
    print("🚁 Height Integration Demo for Image Quality Analyzer")
    print("=" * 60)
    
    # Initialize analyzer with wheat crop
    print("Initializing wheat crop analyzer...")
    analyzer = CropFieldQualityAnalyzer(crop_type="wheat", weather_condition="clear")
    print("✓ Analyzer initialized successfully")
    
    print(f"\nOptimal height for wheat: {analyzer.crop_params['optimal_height']}m")
    print(f"Height tolerance: ±{analyzer.crop_params['height_tolerance']}m")
    
    # Create sample image
    print("\nCreating sample crop field image...")
    sample_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print("✓ Sample image created")
    
    print("\n" + "="*60)
    print("SIMULATING DRONE FLIGHT WITH HEIGHT CHANGES")
    print("="*60)
    
    # Simulate different heights
    for i, height in enumerate(simulate_drone_height()):
        print(f"\n--- Flight Step {i+1} ---")
        
        # Update drone height
        analyzer.update_drone_height(height)
        
        # Get height feedback
        height_feedback = analyzer.get_height_feedback()
        print(f"Current Height: {height:.1f}m")
        print(f"Height Feedback: {height_feedback}")
        
        # Get height recommendation
        height_rec = analyzer.get_height_recommendation()
        if height_rec:
            print(f"Recommendation: {height_rec['action']} - {height_rec['reason']}")
        
        # Analyze image quality
        analysis = analyzer.analyze_frame_quality(sample_image)
        
        # Get drone positioning feedback
        feedback, priority, adjustments = analyzer.get_drone_position_feedback(analysis)
        
        # Calculate quality score
        quality_score = analyzer.calculate_overall_quality_score(analysis)
        
        print(f"Quality Score: {quality_score:.1f}/100")
        print(f"Priority Level: {priority}")
        
        # Show height-specific adjustments
        height_adjustments = [adj for adj in adjustments if adj.get("type") == "height"]
        if height_adjustments:
            print("Height Adjustments:")
            for adj in height_adjustments:
                action = adj["action"]
                value = adj["value"]
                if action == "decrease_height":
                    print(f"  📉 Decrease height by {value:.1f}m")
                elif action == "increase_height":
                    print(f"  📈 Increase height by {value:.1f}m")
                elif action == "maintain_height":
                    print(f"  ✅ Maintain current height")
        
        print("-" * 40)
    
    print("\n" + "="*60)
    print("HEIGHT INTEGRATION FEATURES")
    print("="*60)
    
    print("✅ Real-time height monitoring")
    print("✅ Height-based priority adjustments")
    print("✅ Optimal height recommendations")
    print("✅ Height tolerance management")
    print("✅ Height-specific drone commands")
    
    print("\n" + "="*60)
    print("INTEGRATION METHODS")
    print("="*60)
    
    print("1. **DJI Drone SDK**:")
    print("   from djitellopy import Tello")
    print("   drone = Tello()")
    print("   height = drone.get_height() / 100  # Convert cm to meters")
    print("   analyzer.update_drone_height(height)")
    
    print("\n2. **ArduPilot/MAVLink**:")
    print("   from pymavlink import mavutil")
    print("   connection = mavutil.mavlink_connection('udpin:0.0.0.0:14550')")
    print("   msg = connection.recv_match(type='GLOBAL_POSITION_INT')")
    print("   height = msg.alt / 1000  # Convert mm to meters")
    print("   analyzer.update_drone_height(height)")
    
    print("\n3. **Custom Telemetry**:")
    print("   # Your custom height sensor data")
    print("   height = get_height_from_sensor()")
    print("   analyzer.update_drone_height(height)")
    
    print("\n" + "="*60)
    print("🎉 Height integration demo completed!")
    print("\nThe system now provides:")
    print("- Real-time height monitoring")
    print("- Height-based quality optimization")
    print("- Precise altitude recommendations")
    print("- Height-aware drone control commands")

if __name__ == "__main__":
    main() 