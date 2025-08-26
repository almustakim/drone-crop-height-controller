#!/usr/bin/env python3
"""
Simple camera test script to verify webcam access
"""

import cv2
import time

def test_camera():
    print("🔍 Testing camera access...")
    
    # Try different camera indices
    for camera_index in [0, 1, 2]:
        print(f"Trying camera index {camera_index}...")
        
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Camera {camera_index} could not be opened")
            continue
        
        # Try to read a frame
        ret, frame = cap.read()
        if not ret:
            print(f"❌ Camera {camera_index} opened but couldn't read frame")
            cap.release()
            continue
        
        print(f"✅ Camera {camera_index} working! Frame shape: {frame.shape}")
        
        # Show the frame briefly
        cv2.imshow(f"Camera Test {camera_index}", frame)
        cv2.waitKey(2000)  # Show for 2 seconds
        cv2.destroyAllWindows()
        
        cap.release()
        return camera_index
    
    print("❌ No working camera found")
    return None

def test_camera_stream(camera_index=0):
    """Test continuous camera stream"""
    print(f"🎥 Testing continuous stream from camera {camera_index}...")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("❌ Could not open camera")
        return
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("📹 Camera stream started. Press 'q' to quit, 's' to save frame")
    
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Could not read frame")
                break
            
            frame_count += 1
            
            # Calculate FPS
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"FPS: {fps:.1f}")
            
            # Display frame
            cv2.imshow("Camera Test Stream", frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite(f"test_frame_{frame_count}.jpg", frame)
                print(f"Frame saved as test_frame_{frame_count}.jpg")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("🎉 Camera test completed")

if __name__ == "__main__":
    # First test basic camera access
    working_camera = test_camera()
    
    if working_camera is not None:
        print(f"\n🎯 Working camera found at index {working_camera}")
        
        # Ask user if they want to test stream
        response = input("Test continuous stream? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            test_camera_stream(working_camera)
    else:
        print("\n❌ No working camera found. Please check:")
        print("1. Camera permissions in System Preferences > Security & Privacy > Privacy > Camera")
        print("2. Camera is not being used by another application")
        print("3. Camera is properly connected")
