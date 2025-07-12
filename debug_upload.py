#!/usr/bin/env python3
"""
Debug script to identify upload and API key issues
"""

import os
from dotenv import load_dotenv
from core import SUPPORTED_FILES, process_zip_file

# Load environment variables
load_dotenv()

def check_environment():
    """Check environment configuration"""
    print("🔍 Environment Check:")
    print(f"  GEMINI_API_KEY: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set'}")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    print(f"  GEMINI_API_URL: {'✅ Set' if os.getenv('GEMINI_API_URL') else '❌ Not set'}")
    
    # Check if .env file exists
    env_file_exists = os.path.exists('.env')
    print(f"  .env file: {'✅ Exists' if env_file_exists else '❌ Missing'}")
    
    if not env_file_exists:
        print("\n📝 To fix this:")
        print("  1. Create a .env file in the project root")
        print("  2. Add your Gemini API key:")
        print("     GEMINI_API_KEY=your_actual_api_key_here")
        print("  3. Get your API key from: https://makersuite.google.com/app/apikey")

def check_supported_files():
    """Check supported file types"""
    print(f"\n📁 Supported File Types ({len(SUPPORTED_FILES)}):")
    for ext, lang in SUPPORTED_FILES.items():
        print(f"  .{ext} - {lang}")

def test_file_validation():
    """Test file validation logic"""
    print(f"\n🧪 File Validation Test:")
    supported_extensions = list(SUPPORTED_FILES.keys())
    
    test_files = [
        'test.py',
        'app.js', 
        'image.png',
        'document.pdf',
        'no_extension',
        'test.PY'
    ]
    
    for filename in test_files:
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        is_supported = file_ext in supported_extensions
        status = "✅" if is_supported else "❌"
        print(f"  {status} {filename} -> {file_ext} -> {is_supported}")

def check_api_endpoints():
    """Check if API endpoints are accessible"""
    print(f"\n🌐 API Endpoint Check:")
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("  ✅ Backend API is running on http://localhost:8000")
        else:
            print(f"  ⚠️  Backend API responded with status {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("  ❌ Backend API is not running on http://localhost:8000")
        print("     Start it with: python api_bridge.py")
    except Exception as e:
        print(f"  ❌ Error checking API: {e}")

if __name__ == "__main__":
    print("🔧 Tekshila Debug Report")
    print("=" * 50)
    
    check_environment()
    check_supported_files()
    test_file_validation()
    check_api_endpoints()
    
    print(f"\n📋 Summary:")
    print("  If you see '❌ Not set' for GEMINI_API_KEY, that's why uploads fail.")
    print("  The error 'No supported files found' appears when:")
    print("  1. No API key is configured")
    print("  2. Uploaded files don't have supported extensions")
    print("  3. Zip files contain no supported file types") 