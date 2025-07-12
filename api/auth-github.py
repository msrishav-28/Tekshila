"""
Vercel Serverless API for GitHub OAuth Authentication
File: api/auth/github.py
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request
import secrets
from datetime import datetime, timedelta
import jwt
import base64

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests for OAuth flow"""
        path = self.path
        
        if path.startswith('/api/auth/github/login'):
            self.handle_login()
        elif path.startswith('/api/auth/github/callback'):
            self.handle_callback()
        elif path.startswith('/api/auth/user'):
            self.handle_get_user()
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path.startswith('/api/auth/logout'):
            self.handle_logout()
        else:
            self.send_error(404, "Not Found")
    
    def handle_login(self):
        """Initiate GitHub OAuth flow"""
        try:
            # Generate state parameter for security
            state = secrets.token_urlsafe(32)
            
            # Get environment variables
            client_id = os.getenv('GITHUB_CLIENT_ID')
            if not client_id:
                self.send_error(500, "GitHub Client ID not configured")
                return
            
            # Build OAuth URL with secure redirect
            # Use environment variable for production URL or construct from host
            app_url = os.getenv('VERCEL_URL', self.headers.get('host'))
            if not app_url.startswith('http'):
                app_url = f"https://{app_url}"
            
            params = {
                'client_id': client_id,
                'redirect_uri': f"{app_url}/api/auth/github/callback",
                'scope': 'repo user:email read:user',  # Full repo access for push/pull
                'state': state,
                'allow_signup': 'true'
            }
            
            oauth_url = 'https://github.com/login/oauth/authorize?' + urllib.parse.urlencode(params)
            
            # Set state in cookie
            self.send_response(302)
            self.send_header('Location', oauth_url)
            self.send_header('Set-Cookie', f'oauth_state={state}; HttpOnly; Secure; SameSite=Lax; Max-Age=600')
            self.end_headers()
            
        except Exception as e:
            self.send_error(500, f"OAuth initiation failed: {str(e)}")
    
    def handle_callback(self):
        """Handle GitHub OAuth callback"""
        try:
            print('GitHub OAuth callback triggered')
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            print(f'Callback URL: {self.path}')
            params = urllib.parse.parse_qs(parsed_url.query)
            print(f'Parsed params: {params}')
            
            code = params.get('code', [None])[0]
            state = params.get('state', [None])[0]
            error = params.get('error', [None])[0]
            print(f'code: {code}, state: {state}, error: {error}')
            
            # Check for errors
            if error:
                self.redirect_with_error(f"GitHub OAuth error: {error}")
                return
            
            # Verify state parameter
            cookies = self.parse_cookies()
            print(f'Parsed cookies: {cookies}')
            stored_state = cookies.get('oauth_state')
            
            if not state or state != stored_state:
                self.redirect_with_error("Invalid state parameter")
                return
            
            if not code:
                self.redirect_with_error("No authorization code received")
                return
            
            # Exchange code for token
            print('Exchanging code for token...')
            token_data = self.exchange_code_for_token(code)
            print(f'Token data: {token_data}')
            
            # Get user data
            print('Getting GitHub user data...')
            user_data = self.get_github_user(token_data['access_token'])
            print(f'User data: {user_data}')
            
            # Create JWT token for session
            print('Creating JWT token...')
            jwt_token = self.create_jwt_token({
                'github_token': token_data['access_token'],
                'user': user_data,
                'exp': datetime.utcnow() + timedelta(hours=24)
            })
            print(f'JWT token: {jwt_token}')
            
            # Determine if we're in production (HTTPS) or development
            host = self.headers.get('host', '')
            print(f'Host: {host}')
            is_production = 'vercel.app' in host or 'herokuapp.com' in host
            print(f'Is production: {is_production}')
            
            # Set cookie with appropriate security settings
            cookie_flags = 'HttpOnly; SameSite=None; Secure; Max-Age=86400; Path=/'
            print(f'Cookie flags: {cookie_flags}')
            
            # Send HTML page with JS redirect after setting cookie
            print('Sending HTML response with JS redirect...')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Set-Cookie', f'auth_token={jwt_token}; {cookie_flags}')
            self.send_header('Set-Cookie', f'oauth_state=; HttpOnly; SameSite=Lax; Max-Age=0; Path=/')  # Clear state
            self.end_headers()
            self.wfile.write(f'''
<html>
<head>
    <meta charset="UTF-8">
    <title>Redirecting...</title>
</head>
<body>
    <script>
        // Give browser time to set cookie, then redirect
        setTimeout(() => {{
            window.location.href = '/';
        }}, 100);
    </script>
    <p>Authentication successful. Redirecting...</p>
</body>
</html>
'''.encode())
            
        except Exception as e:
            print(f'Exception in handle_callback: {e}')
            self.redirect_with_error(f"Authentication failed: {str(e)}")
    
    def handle_get_user(self):
        """Get current authenticated user"""
        try:
            # Get JWT token from cookie
            cookies = self.parse_cookies()
            jwt_token = cookies.get('auth_token')
            
            if not jwt_token:
                self.send_json_response({'error': 'Not authenticated'}, 401)
                return
            
            # Decode JWT token
            payload = self.decode_jwt_token(jwt_token)
            if not payload:
                self.send_json_response({'error': 'Invalid token'}, 401)
                return
            
            # Verify GitHub token is still valid
            try:
                user_data = self.get_github_user(payload['github_token'])
                self.send_json_response({
                    'user': user_data,
                    'token': payload['github_token']
                })
            except:
                # Token expired, clear cookie
                host = self.headers.get('host', '')
                is_production = 'vercel.app' in host or 'herokuapp.com' in host
                
                cookie_flags = 'HttpOnly; SameSite=Lax; Max-Age=0; Path=/'
                if is_production:
                    cookie_flags += '; Secure'
                    
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Set-Cookie', f'auth_token=; {cookie_flags}')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Token expired'}).encode())
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_logout(self):
        """Logout user"""
        # Determine if we're in production
        host = self.headers.get('host', '')
        is_production = 'vercel.app' in host or 'herokuapp.com' in host
        
        cookie_flags = 'HttpOnly; SameSite=Lax; Max-Age=0; Path=/'
        if is_production:
            cookie_flags += '; Secure'
            
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', f'auth_token=; {cookie_flags}')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())
    
    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        data = {
            'client_id': os.getenv('GITHUB_CLIENT_ID'),
            'client_secret': os.getenv('GITHUB_CLIENT_SECRET'),
            'code': code,
            'redirect_uri': f"https://{self.headers.get('host')}/api/auth/github/callback"
        }
        
        # Convert data to URL-encoded format
        post_data = urllib.parse.urlencode(data).encode()
        
        req = urllib.request.Request(
            'https://github.com/login/oauth/access_token',
            data=post_data,
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Tekshila-App',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"Token exchange failed: {response.status}")
            
            result = json.loads(response.read().decode())
            
            if 'error' in result:
                raise Exception(f"GitHub error: {result.get('error_description', result['error'])}")
            
            return result
    
    def get_github_user(self, access_token):
        """Get user information from GitHub API"""
        req = urllib.request.Request(
            'https://api.github.com/user',
            headers={
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'Tekshila-App'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                raise Exception(f"Failed to get user info: {response.status}")
            
            return json.loads(response.read().decode())
    
    def create_jwt_token(self, payload):
        """Create JWT token"""
        secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
        return jwt.encode(payload, secret_key, algorithm='HS256')
    
    def decode_jwt_token(self, token):
        """Decode JWT token"""
        try:
            secret_key = os.getenv('SECRET_KEY', 'default-secret-key')
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except:
            return None
    
    def parse_cookies(self):
        """Parse cookies from request"""
        cookies = {}
        cookie_header = self.headers.get('Cookie', '')
        
        for cookie in cookie_header.split(';'):
            if '=' in cookie:
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value
        
        return cookies
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def redirect_with_error(self, error):
        """Redirect to frontend with error"""
        error_encoded = urllib.parse.quote(error)
        self.send_response(302)
        self.send_header('Location', f'/login.html?error={error_encoded}')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()