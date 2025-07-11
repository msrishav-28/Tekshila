import os
import json

def handler(request, response):
    # Set CORS headers
    response.setHeader('Content-Type', 'application/json')
    response.setHeader('Access-Control-Allow-Origin', '*')
    response.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
    response.setHeader('Access-Control-Allow-Headers', 'Content-Type')
    
    # Handle OPTIONS request
    if request.method == 'OPTIONS':
        response.status(200).end()
        return
    
    try:
        # Get environment variables
        github_client_id = os.getenv('GITHUB_CLIENT_ID', '')
        app_url = os.getenv('VERCEL_URL', 'http://localhost:3000')
        
        # Return public configuration
        config = {
            'github_client_id': github_client_id,
            'app_url': app_url,
            'status': 'ok' if github_client_id else 'missing_config'
        }
        
        response.status(200).json(config)
        
    except Exception as e:
        error_response = {
            'error': 'Internal server error',
            'message': str(e),
            'status': 'error'
        }
        response.status(500).json(error_response)
