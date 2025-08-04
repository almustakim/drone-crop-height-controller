#!/usr/bin/env python3
"""
Drone Command Reader
Reads the latest height commands from drone_height_commands.json
For integration with drone control system
"""

import json
import time
import os
from datetime import datetime

def get_latest_command():
    """Get the most recent drone height command"""
    filename = "drone_height_commands.json"
    
    if not os.path.exists(filename):
        return None
    
    try:
        with open(filename, 'r') as f:
            commands = json.load(f)
        
        if commands:
            return commands[-1]  # Return the latest command
        else:
            return None
            
    except Exception as e:
        print(f"Error reading commands: {e}")
        return None

def get_all_commands():
    """Get all drone height commands"""
    filename = "drone_height_commands.json"
    
    if not os.path.exists(filename):
        return []
    
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading commands: {e}")
        return []

def monitor_commands(interval=1.0):
    """Monitor commands in real-time"""
    print("Monitoring drone height commands...")
    print("Press Ctrl+C to stop")
    print("-" * 80)
    
    last_command_count = 0
    
    try:
        while True:
            commands = get_all_commands()
            
            if len(commands) > last_command_count:
                # New command available
                latest = commands[-1]
                
                print(f"\n🆕 NEW COMMAND at {latest['timestamp']}")
                print(f"   Frame: {latest['frame_count']}")
                print(f"   Priority: {latest['priority']}")
                print(f"   Height: {latest['current_height']:.1f}m → {latest['target_height']:.1f}m ({latest['height_change']:+.1f}m)")
                print(f"   Reason: {latest['reason']}")
                print(f"   Crop: {latest['crop_type']}, Weather: {latest['weather']}")
                
                # Quality metrics
                metrics = latest['quality_metrics']
                print(f"   Quality - Brightness: {metrics['brightness']:.1f}, Sharpness: {metrics['sharpness']:.1f}, Coverage: {metrics['green_coverage']:.3f}")
                
                last_command_count = len(commands)
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")

def print_latest_command():
    """Print the latest command"""
    command = get_latest_command()
    
    if command:
        print("📋 LATEST DRONE COMMAND")
        print("=" * 50)
        print(f"Timestamp: {command['timestamp']}")
        print(f"Frame: {command['frame_count']}")
        print(f"Priority: {command['priority']}")
        print(f"Current Height: {command['current_height']:.1f}m")
        print(f"Target Height: {command['target_height']:.1f}m")
        print(f"Height Change: {command['height_change']:+.1f}m")
        print(f"Reason: {command['reason']}")
        print(f"Crop Type: {command['crop_type']}")
        print(f"Weather: {command['weather']}")
        
        print("\nQuality Metrics:")
        metrics = command['quality_metrics']
        print(f"  Brightness: {metrics['brightness']:.1f}")
        print(f"  Sharpness: {metrics['sharpness']:.1f}")
        print(f"  Green Coverage: {metrics['green_coverage']:.3f}")
        
        # Drone action recommendation
        if command['priority'] == 0:
            print("\n🎯 DRONE ACTION: Maintain current position")
        elif command['priority'] >= 3:
            print(f"\n🚨 DRONE ACTION: IMMEDIATE - Move to {command['target_height']:.1f}m")
        elif command['priority'] >= 2:
            print(f"\n⚠️  DRONE ACTION: ADJUST - Move to {command['target_height']:.1f}m")
        else:
            print(f"\n🔧 DRONE ACTION: FINE-TUNE - Move to {command['target_height']:.1f}m")
            
    else:
        print("No commands available yet")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "latest":
            print_latest_command()
        elif command == "monitor":
            interval = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
            monitor_commands(interval)
        elif command == "all":
            commands = get_all_commands()
            print(f"Total commands: {len(commands)}")
            for i, cmd in enumerate(commands[-5:]):  # Show last 5
                print(f"{i+1}. Frame {cmd['frame_count']}: {cmd['current_height']:.1f}m → {cmd['target_height']:.1f}m ({cmd['height_change']:+.1f}m) - {cmd['reason']}")
        else:
            print("Usage:")
            print("  python3 read_drone_commands.py latest    # Show latest command")
            print("  python3 read_drone_commands.py monitor   # Monitor commands in real-time")
            print("  python3 read_drone_commands.py all       # Show all commands")
    else:
        print_latest_command()

if __name__ == "__main__":
    main() 