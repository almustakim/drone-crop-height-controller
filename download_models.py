#!/usr/bin/env python3
"""
Download and setup pre-trained TensorFlow Lite models for crop quality analysis
"""

import os
import requests
import tempfile
import zipfile
import shutil

def download_model(url, filename, description):
    """Download a model file from URL"""
    print(f"📥 Downloading {description}...")
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✅ {description} downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download {description}: {e}")
        return False

def setup_models():
    """Setup all required models"""
    print("🤖 Setting up AI models for crop quality analysis")
    print("=" * 50)
    
    # Create models directory
    os.makedirs("models", exist_ok=True)
    
    # Model URLs (replace with actual model URLs when available)
    models = {
        "crop_detection_model.tflite": {
            "url": "https://example.com/crop_detection_model.tflite",
            "description": "Crop Detection Model (MobileNet SSD)"
        },
        "quality_assessment_model.tflite": {
            "url": "https://example.com/quality_assessment_model.tflite", 
            "description": "Quality Assessment Model (EfficientNet)"
        }
    }
    
    # Download models
    for filename, model_info in models.items():
        if not os.path.exists(filename):
            success = download_model(
                model_info["url"], 
                filename, 
                model_info["description"]
            )
            
            if not success:
                print(f"⚠️  Using fallback mode for {filename}")
        else:
            print(f"✅ {filename} already exists")
    
    print("\n📋 Model Setup Summary:")
    print("=" * 30)
    
    for filename in models.keys():
        if os.path.exists(filename):
            size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"✅ {filename} ({size:.1f} MB)")
        else:
            print(f"❌ {filename} - Not available")
    
    print("\n💡 Note: If models are not available, the system will use")
    print("   traditional OpenCV-based analysis methods as fallback.")
    print("\n🚀 Ready to run AI-enhanced crop quality analysis!")

if __name__ == "__main__":
    setup_models()
