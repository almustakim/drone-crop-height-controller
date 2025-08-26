#!/usr/bin/env python3
"""
Flight Maneuvering Script for Crop Monitoring
Receives altitude and polygon coordinates from image quality analysis
"""

import sys
import math
import ast
import time # Added missing import for time.sleep

# Constants
FOV_DEG = 110
OVERLAP = 0.25  # 25% overlap

def calculate_pass_width(altitude):
    """Calculate pass width based on altitude"""
    return 2 * altitude * math.tan(math.radians(FOV_DEG / 2)) * (1 - OVERLAP)

def generate_lawnmower_waypoints(polygon_coords, altitude):
    """Generate lawnmower pattern waypoints"""
    print(f"Generating flight plan for altitude: {altitude}m")
    
    # Calculate pass width
    pass_width_m = calculate_pass_width(altitude)
    print(f"Pass width: {pass_width_m:.2f}m")
    
    # For now, just return the polygon corners as waypoints
    # In a full implementation, you would generate the full lawnmower pattern
    waypoints = []
    for lat, lon in polygon_coords:
        waypoints.append((lat, lon, altitude))
    
    print(f"Generated {len(waypoints)} waypoints")
    return waypoints

def simulate_flight_execution(waypoints):
    """Simulate flight execution (replace with actual drone control)"""
    print("Simulating flight execution...")
    for i, (lat, lon, alt) in enumerate(waypoints):
        print(f"Waypoint {i+1}: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.1f}m")
        time.sleep(0.5)  # Simulate flight time
    print("Flight plan completed!")

def main():
    """Main function - receives parameters from image quality script"""
    if len(sys.argv) != 3:
        print("Usage: python3 flight_maneuvering.py <altitude> <polygon>")
        print("Example: python3 flight_maneuvering.py 3.5 '[(23.8103, 90.4125), (23.8103, 90.4145), (23.8083, 90.4145), (23.8083, 90.4125)]'")
        sys.exit(1)
    
    try:
        # Get altitude from command line argument
        altitude = float(sys.argv[1])
        print(f"Received altitude: {altitude}m")
        
        # Get polygon from command line argument
        polygon_str = sys.argv[2]
        polygon_coords = ast.literal_eval(polygon_str)
        print(f"Received polygon: {polygon_coords}")
        
        # Generate waypoints
        waypoints = generate_lawnmower_waypoints(polygon_coords, altitude)
        
        # Simulate flight execution
        simulate_flight_execution(waypoints)
        
        print("Flight maneuvering script completed successfully!")
        
    except ValueError as e:
        print(f"Error parsing altitude: {e}")
        sys.exit(1)
    except SyntaxError as e:
        print(f"Error parsing polygon coordinates: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

