"""
Lightweight chatbot-only server to bypass heavy ML dependencies
Run this when main server has issues loading
"""

import os
import sys
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')

# Initialize Django (minimal setup)
import django
django.setup()

# Import chatbot
from chatbot.google_ai_chat import get_chatbot_response

class ChatbotHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chatbot/chat/':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                message = data.get('message', '')
                conversation_history = data.get('conversation_history', [])
                
                # Get AI response
                result = get_chatbot_response(message, conversation_history)
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'response': result['response'],
                    'success': result['success'],
                    'model': result.get('model', 'gemini-2.5-flash')
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_data = {
                    'success': False,
                    'error': str(e),
                    'response': 'Sorry, an error occurred.'
                }
                
                self.wfile.write(json.dumps(error_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chatbot/health/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'api_configured': True,
                'message': 'Lightweight chatbot server is ready!'
            }
            
            self.wfile.write(json.dumps(health_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Log with colors"""
        print(f"[CHATBOT] {format % args}")

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChatbotHandler)
    print(f"""
==============================================================
  SmartGriev Lightweight Chatbot Server
  
  Server running on: http://localhost:{port}
  Chatbot API: http://localhost:{port}/api/chatbot/chat/
  Health Check: http://localhost:{port}/api/chatbot/health/
  
  Press Ctrl+C to stop
==============================================================
""")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n[CHATBOT] Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
