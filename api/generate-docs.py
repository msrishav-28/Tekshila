"""
Vercel Serverless API for Documentation Generation
File: api/generate-docs.py
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import io
import cgi
import tempfile
import zipfile
import requests

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for documentation generation"""
        if self.path == '/api/generate-docs':
            self.handle_generate_docs()
        else:
            self.send_error(404, "Not Found")
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
    
    def handle_generate_docs(self):
        """Generate documentation from uploaded files"""
        try:
            # Parse multipart form data
            ctype, pdict = cgi.parse_header(self.headers.get('Content-Type'))
            if ctype == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                fields = cgi.parse_multipart(self.rfile, pdict)
                
                # Extract form fields
                purpose = fields.get('purpose', ['readme'])[0]
                project_name = fields.get('project_name', [''])[0]
                custom_instructions = fields.get('custom_instructions', [''])[0]
                
                # Extract file contents
                files = fields.get('files', [])
                if not files:
                    self.send_json_response({'error': 'No files uploaded'}, 400)
                    return
                
                # Process files and combine content
                file_contents = {}
                for file_data in files:
                    if isinstance(file_data, bytes):
                        # Try to decode the file content
                        try:
                            content = file_data.decode('utf-8')
                            # Simple filename extraction (in production, handle this better)
                            filename = f"file_{len(file_contents)}.txt"
                            file_contents[filename] = content
                        except:
                            continue
                
                # Generate documentation using AI
                if purpose == 'readme':
                    content = self.generate_readme_with_ai(project_name, file_contents, custom_instructions)
                    doc_type = 'readme'
                    filename = 'README.md'
                else:
                    content = self.generate_comments_with_ai(file_contents, custom_instructions)
                    doc_type = 'comments'
                    filename = 'commented_code.txt'
                
                self.send_json_response({
                    'success': True,
                    'content': content,
                    'type': doc_type,
                    'filename': filename
                })
            else:
                self.send_json_response({'error': 'Invalid content type'}, 400)
                
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def generate_readme_with_ai(self, project_name, file_contents, instructions):
        """Generate README using Gemini AI or fallback to mock"""
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        gemini_api_url = os.getenv('GEMINI_API_URL')
        
        if not gemini_api_key:
            # Fallback to mock generation if no API key
            return self.generate_mock_readme(project_name, instructions)
        
        try:
            # Prepare the prompt
            files_context = "\n\n".join([f"File: {name}\n```\n{content}\n```" for name, content in file_contents.items()])
            
            prompt = f"""
            You are an expert technical writer. Create a comprehensive README.md file for a project called "{project_name}".
            
            Here are the code files:
            {files_context}
            
            {f"Additional instructions: {instructions}" if instructions else ""}
            
            Create a professional README with the following sections:
            1. Project title and description
            2. Features
            3. Installation instructions
            4. Usage examples
            5. Configuration (if applicable)
            6. API documentation (if applicable)
            7. Contributing guidelines
            8. License
            
            Use Markdown formatting with emojis for better readability.
            """
            
            # Call Gemini API
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{gemini_api_url}?key={gemini_api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                return content
            else:
                # Fallback to mock if API fails
                return self.generate_mock_readme(project_name, instructions)
                
        except Exception as e:
            # Fallback to mock on any error
            print(f"AI generation failed: {str(e)}")
            return self.generate_mock_readme(project_name, instructions)
    
    def generate_comments_with_ai(self, file_contents, instructions):
        """Generate code comments using Gemini AI or fallback to mock"""
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        gemini_api_url = os.getenv('GEMINI_API_URL')
        
        if not gemini_api_key:
            return self.generate_mock_comments()
        
        try:
            # For now, process the first file (in production, handle multiple files)
            first_file = list(file_contents.items())[0] if file_contents else ("unknown", "")
            filename, content = first_file
            
            prompt = f"""
            You are an expert code documenter. Add comprehensive inline comments to the following code.
            
            File: {filename}
            ```
            {content}
            ```
            
            {f"Additional instructions: {instructions}" if instructions else ""}
            
            Add comments that:
            1. Explain what each function/class does
            2. Document parameters and return values
            3. Explain complex logic
            4. Add TODO comments for potential improvements
            
            Return the complete code with comments added.
            """
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{gemini_api_url}?key={gemini_api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                # Extract code from markdown if wrapped
                if '```' in content:
                    import re
                    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', content, re.DOTALL)
                    if code_blocks:
                        return code_blocks[0]
                return content
            else:
                return self.generate_mock_comments()
                
        except Exception as e:
            print(f"AI comment generation failed: {str(e)}")
            return self.generate_mock_comments()
    
    def generate_mock_readme(self, project_name, instructions):
        """Generate mock README content as fallback"""
        return f"""# {project_name}

## 🚀 Overview

{project_name} is a cutting-edge application that leverages modern technologies to deliver exceptional performance and user experience.

**Note**: This is a mock README. To generate actual AI-powered documentation, please configure your Gemini API key in the environment variables.

## ✨ Features

- **High Performance**: Optimized for speed and efficiency
- **Scalable Architecture**: Built to grow with your needs
- **Modern Tech Stack**: Using the latest technologies
- **Developer Friendly**: Clear code structure and documentation

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name.lower().replace(' ', '-')}.git

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
# Add your configuration here
API_KEY=your_api_key_here
```

## 📚 Usage

```javascript
// Example usage
import {{ {project_name.replace(' ', '')} }} from '{project_name.lower().replace(' ', '-')}';

// Initialize
const app = new {project_name.replace(' ', '')}();

// Use the application
app.start();
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by the {project_name} Team

{f"Additional notes: {instructions}" if instructions else ""}"""
    
    def generate_mock_comments(self):
        """Generate mock commented code as fallback"""
        return '''"""
Module: example.py
Description: Example module with comprehensive documentation
Note: This is mock commented code. Configure Gemini API for actual AI-generated comments.
"""

import os
import sys
from typing import Dict, List, Optional

# Configuration constants
DEFAULT_TIMEOUT = 30  # Default timeout in seconds
MAX_RETRIES = 3      # Maximum number of retry attempts


class ExampleClass:
    """
    Example class demonstrating documentation best practices.
    
    This class shows how to properly document Python code with
    comprehensive docstrings and inline comments.
    
    Attributes:
        name (str): The name of the instance
        config (dict): Configuration parameters
        is_initialized (bool): Whether the instance is initialized
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        """
        Initialize the ExampleClass instance.
        
        Args:
            name (str): The name for this instance
            config (Optional[Dict]): Configuration dictionary. If None,
                                   default configuration will be used.
        
        Raises:
            ValueError: If name is empty or None
        """
        # Validate input parameters
        if not name:
            raise ValueError("Name cannot be empty")
        
        # Set instance attributes
        self.name = name
        self.config = config or self._get_default_config()
        self.is_initialized = False
        
        # Perform initialization
        self._initialize()
    
    def _get_default_config(self) -> Dict:
        """
        Get the default configuration.
        
        Returns:
            Dict: Default configuration parameters
        """
        return {
            'timeout': DEFAULT_TIMEOUT,
            'retries': MAX_RETRIES,
            'verbose': False
        }
    
    def _initialize(self) -> None:
        """
        Perform initialization tasks.
        
        This method sets up the instance for use.
        """
        # TODO: Add actual initialization logic here
        self.is_initialized = True
        
        # Log initialization if verbose mode is enabled
        if self.config.get('verbose', False):
            print(f"Initialized {self.name}")
    
    def process(self, data: List[str]) -> List[str]:
        """
        Process the input data.
        
        Args:
            data (List[str]): List of strings to process
        
        Returns:
            List[str]: Processed data
        
        Raises:
            RuntimeError: If instance is not initialized
        """
        # Check if initialized
        if not self.is_initialized:
            raise RuntimeError("Instance not initialized")
        
        # Process each item in the data
        result = []
        for item in data:
            # Apply processing logic
            processed_item = self._process_item(item)
            result.append(processed_item)
        
        return result
    
    def _process_item(self, item: str) -> str:
        """
        Process a single item.
        
        Args:
            item (str): Item to process
        
        Returns:
            str: Processed item
        """
        # TODO: Implement actual processing logic
        return item.upper()  # Simple example: convert to uppercase


# Example usage
if __name__ == "__main__":
    # Create an instance with custom configuration
    config = {
        'timeout': 60,
        'verbose': True
    }
    
    example = ExampleClass("MyExample", config)
    
    # Process some data
    input_data = ["hello", "world", "python"]
    output_data = example.process(input_data)
    
    # Display results
    print(f"Processed data: {output_data}")
'''
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())