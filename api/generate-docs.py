from http.server import BaseHTTPRequestHandler
import json
import time


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Simulate AI processing time
            time.sleep(3)

            # In a real application, you would parse the multipart/form-data,
            # get the uploaded files, and send them to a large language model.
            # For now, we return a mock response based on the "purpose".

            # This is a simplified way to get one of the form fields.
            # A real implementation would need a robust multipart parser.
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')

            purpose = "readme"  # default
            if 'name="purpose"\r\n\r\nreadme' in post_data:
                purpose = "readme"
            elif 'name="purpose"\r\n\r\ncomments' in post_data:
                purpose = "comments"

            if purpose == "readme":
                mock_content = """# Mock Project

This is an AI-generated README for your project.

## 🚀 Features
- Feature A: Does something cool.
- Feature B: Does something else.

## 🛠️ Installation
```bash
npm install mock-project
```
"""
            else:
                mock_content = """# AI-Generated Comments

This function adds two numbers

def add(a, b):
    # returns the sum
    return a + b
"""

            response_data = {
                "success": True,
                "content": mock_content,
                "type": purpose
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())