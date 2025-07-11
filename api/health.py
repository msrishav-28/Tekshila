"""
Health check endpoint for diagnosing application issues
"""

import os
import json
from http.server import BaseHTTPRequestHandler
from datetime import datetime

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
            
            # Get environment info (without exposing secrets)
            env_vars = {
                'VERCEL_URL': os.getenv('VERCEL_URL', 'Not Set'),
                'VERCEL_ENV': os.getenv('VERCEL_ENV', 'Not Set'),
                'GITHUB_CLIENT_ID': 'Set' if os.getenv('GITHUB_CLIENT_ID') else 'Not Set',
                'GITHUB_CLIENT_SECRET': 'Set' if os.getenv('GITHUB_CLIENT_SECRET') else 'Not Set'
            }
            
            # Health check response
            health = {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'environment': env_vars,
                'host': self.headers.get('host', 'unknown'),
                'user_agent': self.headers.get('user-agent', 'unknown'),
                'path': self.path,
                'version': '1.0.0'
            }
            
            self.wfile.write(json.dumps(health, indent=2).encode())
            
        except Exception as e:
            # Send error response
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            self.wfile.write(json.dumps(error_response, indent=2).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
