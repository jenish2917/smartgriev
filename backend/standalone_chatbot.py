"""
Ultra-lightweight standalone chatbot server
NO Django, NO ML dependencies, JUST Google Gemini chat
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Direct Google Gemini integration
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk'
genai.configure(api_key=GEMINI_API_KEY)

# Natural conversation system prompt
SYSTEM_PROMPT = """You are a helpful assistant for SmartGriev citizen complaint system in India.

🔴 MOST IMPORTANT RULE - LANGUAGE MATCHING:
YOU MUST respond in THE EXACT SAME LANGUAGE as the user's message!
- Gujarati script (ગુજરાતી) → Reply in Gujarati ONLY
- Hindi script (हिंदी) → Reply in Hindi ONLY
- Marathi script (मराठी) → Reply in Marathi ONLY
- English → Reply in English ONLY

NEVER mix languages! If user writes in Gujarati, your ENTIRE response must be in Gujarati!

CONVERSATION STYLE:
- Talk like a friendly phone call
- Ultra-short (1-2 sentences)
- Natural and warm
- NO robotic language

EXAMPLES:
Gujarati User: "રસ્તા પર ખાડા છે"
You (Gujarati): "ક્યાં છે આ ખાડા? તમારો વિસ્તાર જણાવો."

Hindi User: "सड़क पर गड्ढे हैं"
You (Hindi): "कहाँ है यह गड्ढा? इलाका बताइए।"

English User: "Potholes on road"
You (English): "Where exactly? Tell me your area."

Remember: ALWAYS match the user's language perfectly!"""

class ChatbotHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        """Handle chatbot requests"""
        try:
            parsed_path = urlparse(self.path)
            
            if parsed_path.path == '/api/chatbot/chat/':
                # Read request
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                data = json.loads(body)
                
                user_message = data.get('message', '')
                
                # Get AI response
                model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash-exp',
                    system_instruction=SYSTEM_PROMPT
                )
                
                response = model.generate_content(user_message)
                ai_response = response.text
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'response': ai_response,
                    'success': True
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                print(f"✅ User: {user_message[:50]}...")
                print(f"✅ Bot: {ai_response[:50]}...")
            else:
                self.send_response(404)
                self.end_headers()
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_data = {
                'error': str(e),
                'success': False
            }
            
            self.wfile.write(json.dumps(error_data).encode('utf-8'))
    
    def do_GET(self):
        """Handle health check"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/api/chatbot/health/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            health_data = {
                'status': 'healthy',
                'api_configured': True,
                'message': 'Ultra-lightweight chatbot ready! 🚀'
            }
            
            self.wfile.write(json.dumps(health_data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ChatbotHandler)
    print(f"""
╔══════════════════════════════════════════════════╗
║  SmartGriev Ultra-Light Chatbot Server          ║
║                                                  ║
║  🚀 Server: http://localhost:{port}              ║
║  💬 Chat: http://localhost:{port}/api/chatbot/chat/
║  ❤️  Health: http://localhost:{port}/api/chatbot/health/
║                                                  ║
║  Press Ctrl+C to stop                            ║
╚══════════════════════════════════════════════════╝
""")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
