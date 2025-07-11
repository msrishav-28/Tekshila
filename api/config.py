import os
import json
from http.server import BaseHTTPRequestHandler
# Updated: 2025-07-11 - Fresh deployment configuration

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
            app_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
            
            # Return public configuration
            config = {
                'github_client_id': github_client_id,
                'app_url': app_url,
                'status': 'ok' if github_client_id else 'missing_config'
            }
            
            self.wfile.write(json.dumps(config).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'error': 'Internal server error',
                'message': str(e),
                'status': 'error'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
