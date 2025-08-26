#!/usr/bin/env python3
import time
import cv2
import numpy as np

# Try to import MAVLink for drone functionality
try:
    from pymavlink import mavutil
    MAVLINK_AVAILABLE = True
    print("MAVLink available - drone mode enabled")
except ImportError:
    MAVLINK_AVAILABLE = False
    print("MAVLink not available - webcam mode only")

# Connection parameters for drone
connection_string = '/dev/ttyAMA0'  # Use ttyAMA0 for hardware UART
baud_rate = 57600

def connect_pixhawk():
    """Connect to Pixhawk drone controller"""
    if not MAVLINK_AVAILABLE:
        return None
    
    print("Connecting to Pixhawk...")
    try:
        master = mavutil.mavlink_connection(connection_string, baud=baud_rate)
        print("Waiting for heartbeat...")
        master.wait_heartbeat()
        print("Heartbeat received from system (system %u component %u)" % (master.target_system, master.target_component))
        return master
    except Exception as e:
        print(f"Failed to connect to drone: {e}")
        return None

def get_footage_quality(frame):
    """Analyze frame quality and return recommendation"""
    if frame is None:
        return "No frame", 0
    
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Quality metrics
    brightness = np.mean(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = np.std(gray)
    
    # Quality score (0-100) - weighted combination
    quality = min(100, (brightness / 255) * 30 + (sharpness / 200) * 40 + (contrast / 100) * 30)
    
    # Determine recommendation
    if quality < 30:
        return "Too dark/blurry - adjust lighting or focus", quality
    elif quality < 60:
        return "Poor quality - needs improvement", quality
    elif quality < 80:
        return "Acceptable quality", quality
    else:
        return "Excellent quality", quality

def drone_mode(master):
    """Run in drone mode - analyze footage and get altitude data"""
    print("Running in DRONE MODE")
    print("Press 'q' to quit, 'w' to switch to webcam mode")
    
    while True:
        try:
            # Get altitude
            msg = master.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)
            if msg is None:
                print("No message received. Reconnecting...")
                master = connect_pixhawk()
                if master is None:
                    print("Switching to webcam mode...")
                    return False
                continue

            # Extract altitude
            altitude_m = msg.alt / 1000.0  # Convert mm to meters
            
            # Analyze footage quality and get drone movement recommendations
            recommendation, quality_score, distance_recommendation = analyze_crop_footage_quality(altitude_m)
            
            # Timestamp
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # Output with drone movement instructions
            print(f"[{ts}] Height: {altitude_m:.2f}m | Quality: {quality_score:.1f}/100")
            print(f"  → {recommendation}")
            print(f"  → {distance_recommendation}")
            print("-" * 60)
            
            time.sleep(2)  # Check every 2 seconds
            
        except Exception as e:
            print("Error:", e)
            print("Reconnecting in 2 seconds...")
            time.sleep(2)
            master = connect_pixhawk()
            if master is None:
                print("Switching to webcam mode...")
                return False

def analyze_crop_footage_quality(altitude_m):
    """Analyze crop footage quality and give drone movement recommendations"""
    
    # Quality score based on altitude (lower altitude = better quality for crops)
    if altitude_m < 2.0:
        quality = 90  # Too close - risk of collision
        recommendation = "DRONE TOO CLOSE! Move UP to 3-5 meters for safety"
        distance_recommendation = "Recommended height: 3-5 meters for crop analysis"
    elif altitude_m < 3.0:
        quality = 85  # Very close - excellent detail
        recommendation = "Excellent detail! Current height is perfect for crop inspection"
        distance_recommendation = "Maintain current height: {:.1f}m".format(altitude_m)
    elif altitude_m < 5.0:
        quality = 75  # Good detail
        recommendation = "Good quality. Move DOWN to 2-3m for better crop detail"
        distance_recommendation = "Optimal height: 2-3 meters for detailed crop analysis"
    elif altitude_m < 8.0:
        quality = 60  # Moderate detail
        recommendation = "Moderate quality. Move DOWN to 3-5m for better crop footage"
        distance_recommendation = "Recommended height: 3-5 meters for crop monitoring"
    elif altitude_m < 12.0:
        quality = 40  # Poor detail
        recommendation = "Poor quality. Move DOWN to 5-8m for acceptable crop footage"
        distance_recommendation = "Acceptable height: 5-8 meters for general crop overview"
    else:
        quality = 25  # Very poor detail
        recommendation = "Very poor quality. Move DOWN to 8-10m for basic crop footage"
        distance_recommendation = "Maximum height: 8-10 meters for crop surveillance"
    
    return recommendation, quality, distance_recommendation

def webcam_mode():
    """Run in webcam mode - analyze webcam quality in real-time"""
    print("Running in WEBCAM MODE")
    print("Press 'q' to quit, 'd' to try drone mode")
    print("Camera positioning: Move closer/farther based on real-time feedback")
    
    # Initialize webcam with better error handling
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        print("Trying to check webcam permissions...")
        
        # Try to get webcam info
        cap_info = cv2.VideoCapture(0)
        if cap_info.isOpened():
            print("Webcam is accessible but may need permissions")
            print("Please check System Preferences > Security & Privacy > Camera")
        else:
            print("Webcam not found or not accessible")
        return False
    
    print("Webcam opened successfully!")
    
    # Set webcam properties for better quality
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Wait a moment for camera to initialize
    time.sleep(1)
    
    frame_count = 0
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            print("Trying to reconnect...")
            cap.release()
            time.sleep(1)
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                print("Failed to reconnect to webcam")
                break
            continue
        
        frame_count += 1
        
        # Get quality analysis with camera positioning recommendations
        recommendation, quality_score, camera_advice = analyze_webcam_positioning(frame)
        
        # Calculate FPS
        current_time = time.time()
        fps = frame_count / (current_time - start_time)
        
        # Add text overlay to frame
        cv2.putText(frame, f"Quality: {quality_score:.1f}/100", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, recommendation[:40], (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Add camera positioning advice
        cv2.putText(frame, camera_advice, (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, "Webcam Mode", (10, 150), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Display the frame
        cv2.imshow('Webcam Quality Analysis', frame)
        
        # Print console output every 15 frames (about 0.5 second at 30fps) for real-time feedback
        if frame_count % 15 == 0:
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{ts}] Quality: {quality_score:.1f}/100 | {camera_advice}")
        
        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('d') and MAVLINK_AVAILABLE:
            print("Switching to drone mode...")
            cap.release()
            cv2.destroyAllWindows()
            return True
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    return False

def analyze_webcam_positioning(frame):
    """Analyze webcam frame and give camera positioning recommendations"""
    if frame is None:
        return "No frame", 0, "Camera error"
    
    # Convert to grayscale for analysis
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Quality metrics
    brightness = np.mean(gray)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    contrast = np.std(gray)
    
    # Quality score (0-100) - weighted combination
    quality = min(100, (brightness / 255) * 30 + (sharpness / 200) * 40 + (contrast / 100) * 30)
    
    # Camera positioning recommendations based on quality metrics
    if quality < 30:
        if brightness < 50:
            camera_advice = "MOVE CLOSER + Better lighting needed"
        elif sharpness < 50:
            camera_advice = "MOVE CLOSER - Too blurry"
        else:
            camera_advice = "MOVE CLOSER + Adjust focus"
        recommendation = "Very poor quality"
    elif quality < 50:
        if sharpness < 100:
            camera_advice = "MOVE CLOSER - Improve sharpness"
        else:
            camera_advice = "MOVE CLOSER - Better detail needed"
        recommendation = "Poor quality"
    elif quality < 70:
        if sharpness < 150:
            camera_advice = "MOVE CLOSER - More detail possible"
        else:
            camera_advice = "Current position OK"
        recommendation = "Acceptable quality"
    elif quality < 85:
        if sharpness < 200:
            camera_advice = "MOVE CLOSER - Excellent detail possible"
        else:
            camera_advice = "Perfect position!"
        recommendation = "Good quality"
    else:
        if sharpness > 250:
            camera_advice = "PERFECT! Maintain distance"
        else:
            camera_advice = "Excellent! Slight adjustment possible"
        recommendation = "Excellent quality"
    
    return recommendation, quality, camera_advice

def main():
    print("=== Image Quality Analysis System ===")
    print("Supports both DRONE and WEBCAM modes")
    print("=" * 40)
    
    # Try to connect to drone first
    if MAVLINK_AVAILABLE:
        master = connect_pixhawk()
        if master is not None:
            # Run in drone mode
            if drone_mode(master):
                # If drone mode fails, switch to webcam
                webcam_mode()
        else:
            print("Drone connection failed, switching to webcam mode...")
            webcam_mode()
    else:
        # MAVLink not available, run webcam mode directly
        print("MAVLink not available, running in webcam mode only")
        webcam_mode()
    
    print("Program finished")

if __name__ == "__main__":
    main()



