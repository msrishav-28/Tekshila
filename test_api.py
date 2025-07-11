#!/usr/bin/env python3
"""
Local test script to simulate Vercel serverless function calls
"""

import os
import sys
import json
from io import StringIO
from unittest.mock import Mock

# Add the api directory to the path
sys.path.insert(0, 'api')

def test_config_endpoint():
    """Test the config endpoint"""
    print("🧪 Testing /api/config endpoint...")
    
    # Set test environment variables
    os.environ['GITHUB_CLIENT_ID'] = 'test_client_id_123'
    os.environ['GITHUB_CLIENT_SECRET'] = 'test_secret_456'
    os.environ['VERCEL_URL'] = 'test-app.vercel.app'
    
    try:
        # Import the handler
        from config import handler
        
        # Create mock request
        mock_handler = handler()
        mock_handler.send_response = Mock()
        mock_handler.send_header = Mock()
        mock_handler.end_headers = Mock()
        mock_handler.headers = {'host': 'test-app.vercel.app'}
        
        # Capture output
        output = StringIO()
        mock_handler.wfile = output
        
        # Call the handler
        mock_handler.do_GET()
        
        # Get the response
        response_data = output.getvalue()
        
        if response_data:
            config = json.loads(response_data)
            print("✅ Config endpoint working!")
            print(f"   Status: {config.get('status')}")
            print(f"   GitHub Client ID: {config.get('github_client_id')}")
            print(f"   App URL: {config.get('app_url')}")
            print(f"   Environment: {config.get('environment')}")
            
            if config.get('missing_variables'):
                print(f"   ⚠️  Missing variables: {config.get('missing_variables')}")
            
            return True
        else:
            print("❌ No response data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing config endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_health_endpoint():
    """Test the health endpoint"""
    print("\n🧪 Testing /api/health endpoint...")
    
    try:
        # Import the handler
        from health import handler
        
        # Create mock request
        mock_handler = handler()
        mock_handler.send_response = Mock()
        mock_handler.send_header = Mock()
        mock_handler.end_headers = Mock()
        mock_handler.headers = {'host': 'test-app.vercel.app', 'user-agent': 'test-agent'}
        mock_handler.path = '/api/health'
        
        # Capture output
        output = StringIO()
        mock_handler.wfile = output
        
        # Call the handler
        mock_handler.do_GET()
        
        # Get the response
        response_data = output.getvalue()
        
        if response_data:
            health = json.loads(response_data)
            print("✅ Health endpoint working!")
            print(f"   Status: {health.get('status')}")
            print(f"   Host: {health.get('host')}")
            print(f"   Environment Variables:")
            env_vars = health.get('environment', {})
            for key, value in env_vars.items():
                print(f"     {key}: {value}")
            
            return True
        else:
            print("❌ No response data")
            return False
            
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Testing Tekshila API Endpoints Locally")
    print("=" * 50)
    
    # Change to project directory
    if not os.path.exists('api'):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    config_ok = test_config_endpoint()
    health_ok = test_health_endpoint()
    
    print("\n" + "=" * 50)
    if config_ok and health_ok:
        print("🎉 All tests passed! Your API endpoints should work on Vercel.")
        print("   Next steps:")
        print("   1. Commit and push your changes")
        print("   2. Verify environment variables are set in Vercel dashboard")
        print("   3. Test the live endpoints")
    else:
        print("❌ Some tests failed. Please check the errors above.")
