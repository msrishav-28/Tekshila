from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request
import secrets
from datetime import datetime, timedelta
import jwt

class handler(BaseHTTPRequestHandler):
    
    # Entry points for GET and POST requests
    def do_GET(self):
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
        if self.path.startswith('/api/auth/logout'):
            self.handle_logout()
        else:
            self.send_error(404, "Not Found")

    # --- Main Logic Handlers ---

    def handle_login(self):
        """Initiates the GitHub OAuth flow by redirecting the user to GitHub."""
        try:
            client_id = os.getenv('GITHUB_CLIENT_ID')
            if not client_id:
                self.send_error(500, "Configuration Error: GITHUB_CLIENT_ID is not set.")
                return

            state = secrets.token_urlsafe(32)
            host, protocol = self._get_host_and_protocol()
            
            params = {
                'client_id': client_id,
                'redirect_uri': f"{protocol}://{host}/api/auth/github/callback",
                'scope': 'repo user:email read:user',
                'state': state,
            }
            oauth_url = 'https://github.com/login/oauth/authorize?' + urllib.parse.urlencode(params)
            
            self.send_response(302)
            self.send_header('Location', oauth_url)
            self.send_header('Set-Cookie', f'oauth_state={state}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=600')
            self.end_headers()
        except Exception as e:
            self.send_error(500, f"OAuth initiation failed: {e}")

    def handle_callback(self):
        """Handles the callback from GitHub after user authorization."""
        try:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            code, state, error = params.get('code', [None])[0], params.get('state', [None])[0], params.get('error', [None])[0]

            if error:
                return self.redirect_with_error(f"GitHub OAuth error: {error}")

            stored_state = self.parse_cookies().get('oauth_state')
            if not state or state != stored_state:
                return self.redirect_with_error("Invalid state parameter. CSRF attack suspected.")

            if not code:
                return self.redirect_with_error("No authorization code received from GitHub.")
            
            host, protocol = self._get_host_and_protocol()
            token_data = self._exchange_code_for_token(code, host, protocol)
            user_data = self._get_github_user(token_data['access_token'])
            
            jwt_payload = {
                'github_token': token_data['access_token'],
                'user': user_data,
                'exp': datetime.utcnow() + timedelta(hours=24)
            }
            jwt_token = self._create_jwt_token(jwt_payload)
            
            # Set auth cookie and redirect to main app
            self.send_response(302)
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', f'auth_token={jwt_token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=86400')
            self.send_header('Set-Cookie', 'oauth_state=; Max-Age=0') # Clear state cookie
            self.end_headers()

        except Exception as e:
            self.redirect_with_error(f"Authentication failed: {e}")

    def handle_get_user(self):
        """Verifies the JWT and returns the current user's data."""
        try:
            jwt_token = self.parse_cookies().get('auth_token')
            if not jwt_token:
                return self.send_json_response({'error': 'Not authenticated'}, 401)
            
            payload = self._decode_jwt_token(jwt_token)
            if not payload:
                 return self.send_json_response({'error': 'Invalid or expired token'}, 401)
            
            # We can trust the user data in the payload for some time to avoid frequent API calls
            # For higher security, you could re-validate with GitHub API here.
            self.send_json_response({'user': payload['user']})
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)

    def handle_logout(self):
        """Logs the user out by clearing the authentication cookie."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Set-Cookie', 'auth_token=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0')
        self.end_headers()
        self.wfile.write(json.dumps({'success': True}).encode())

    # --- Helper & Utility Methods ---

    def _exchange_code_for_token(self, code, host, protocol):
        """Helper to exchange the GitHub auth code for an access token."""
        client_id = os.getenv('GITHUB_CLIENT_ID')
        client_secret = os.getenv('GITHUB_CLIENT_SECRET')
        if not client_id or not client_secret:
            raise ValueError("GitHub credentials are not configured on the server.")

        data = urllib.parse.urlencode({
            'client_id': client_id,
            'client_secret': client_secret,
            'code': code,
            'redirect_uri': f"{protocol}://{host}/api/auth/github/callback"
        }).encode()
        
        req = urllib.request.Request(
            'https://github.com/login/oauth/access_token',
            data=data,
            headers={'Accept': 'application/json', 'User-Agent': 'Tekshila-App'}
        )
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if 'error' in result:
                raise Exception(f"GitHub token error: {result.get('error_description', result['error'])}")
            return result

    def _get_github_user(self, access_token):
        """Helper to fetch user data from GitHub API."""
        req = urllib.request.Request(
            'https://api.github.com/user',
            headers={'Authorization': f'token {access_token}', 'User-Agent': 'Tekshila-App'}
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _create_jwt_token(self, payload):
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key: raise ValueError("JWT SECRET_KEY is not configured.")
        return jwt.encode(payload, secret_key, algorithm='HS256')

    def _decode_jwt_token(self, token):
        secret_key = os.getenv('SECRET_KEY')
        if not secret_key: raise ValueError("JWT SECRET_KEY is not configured.")
        try:
            return jwt.decode(token, secret_key, algorithms=['HS256'])
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None
    
    def _get_host_and_protocol(self):
        host = self.headers.get('x-forwarded-host') or self.headers.get('host')
        proto = self.headers.get('x-forwarded-proto') or 'https'
        return host, proto

    def parse_cookies(self):
        return {k.strip(): v for k, v in (c.split('=', 1) for c in self.headers.get('Cookie', '').split(';') if '=' in c)}

    def send_json_response(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def redirect_with_error(self, error):
        self.send_response(302)
        self.send_header('Location', f'/login.html?error={urllib.parse.quote(error)}')
        self.end_headers()
        
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()