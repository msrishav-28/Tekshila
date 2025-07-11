import os
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # CORS headers
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Get environment variables
            github_client_id = os.getenv('GITHUB_CLIENT_ID', '')
            github_client_secret = os.getenv('GITHUB_CLIENT_SECRET', '')
            app_url = os.getenv('VERCEL_URL')
            
            # If VERCEL_URL is not set, try to construct from request
            if not app_url:
                host = self.headers.get('host', 'localhost:3000')
                protocol = 'https' if 'vercel.app' in host or 'herokuapp.com' in host else 'http'
                app_url = f"{protocol}://{host}"
            
            # Validate required environment variables
            missing_vars = []
            if not github_client_id:
                missing_vars.append('GITHUB_CLIENT_ID')
            if not github_client_secret:
                missing_vars.append('GITHUB_CLIENT_SECRET')
            
            # Return configuration
            config = {
                'github_client_id': github_client_id,
                'app_url': app_url,
                'status': 'ok' if not missing_vars else 'missing_config',
                'missing_variables': missing_vars,
                'environment': 'production' if 'vercel.app' in app_url else 'development',
                'timestamp': str(datetime.utcnow().isoformat()) + 'Z'
            }
            
            if missing_vars:
                config['error'] = f"Missing required environment variables: {', '.join(missing_vars)}"
                config['help'] = "Please configure the missing environment variables in your deployment settings."
            
            self.wfile.write(json.dumps(config, indent=2).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'Internal server error',
                'message': str(e),
                'status': 'error',
                'timestamp': str(datetime.utcnow().isoformat()) + 'Z'
            }
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
