"""
SmartGriev Gemini Chatbot Server
Ultra-lightweight HTTP server for Gemini AI chatbot without Django overhead
"""

import http.server
import socketserver
import json
import os
import time
import uuid
from urllib.parse import parse_qs, urlparse
import google.generativeai as genai

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk')
genai.configure(api_key=GEMINI_API_KEY)

PORT = 8000

# Conversation storage
conversations = {}

# Supported languages
LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'bn': 'Bengali',
    'kn': 'Kannada',
    'ml': 'Malayalam',
}

class GeminiChatbotHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for Gemini Chatbot"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        
        # Gemini chat endpoint
        if parsed_url.path in ['/api/chatbot/chat/', '/api/chatbot/gemini/chat/']:
            self.handle_chat()
            return
        
        self.send_error_response("Not found", 404)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        # Health check
        if parsed_url.path in ['/api/chatbot/health/', '/api/health/']:
            self.send_json_response({
                'status': 'healthy',
                'service': 'SmartGriev Gemini Chatbot',
                'model': 'Gemini 2.0 Flash Exp',
                'timestamp': time.time(),
                'languages': list(LANGUAGES.values())
            })
            return
        
        self.send_error_response("Not found", 404)
    
    def handle_chat(self):
        """Handle chatbot conversation"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            message = data.get('message', '').strip()
            session_id = data.get('session_id', str(uuid.uuid4()))
            language = data.get('language', 'en')
            
            if not message:
                self.send_error_response('Message is required', 400)
                return
            
            # Get language name
            language_name = LANGUAGES.get(language, 'English')
            
            # Build system prompt for natural conversation
            system_prompt = f"""You are CivicAI, a helpful AI assistant for SmartGriev - India's citizen complaint management system.

LANGUAGE: Respond in {language_name}. If user speaks in {language_name}, respond in {language_name}.

YOUR ROLE:
- Help citizens register complaints about civic issues (roads, water, electricity, garbage, etc.)
- Have natural, friendly conversations
- Extract complaint details: category, location, urgency, contact
- Be empathetic and understanding

CONVERSATION STYLE:
- Speak naturally like a helpful friend
- DON'T repeat the same greeting every time
- Remember context from previous messages
- Ask follow-up questions only when needed
- Keep responses concise (2-3 sentences max)

COMPLAINT CATEGORIES:
- road (सड़क/રસ્તો): Potholes, damage, construction
- water (पानी/પાણી): Supply issues, leakage, quality
- electricity (बिजली/વીજળી): Power cuts, billing, poles
- garbage (कचरा/કચરો): Collection, disposal, cleanliness
- drainage (नाली/ગટર): Blockage, overflow, sewage

FIELD EXTRACTION:
When you have enough information, extract:
{{
  "category": "road/water/electricity/garbage/drainage",
  "location": "specific area/landmark",
  "urgency": "low/medium/high",
  "contact": "phone/email if provided",
  "description": "brief summary"
}}

IMPORTANT:
- If user just says "Hello/Hi", greet warmly and ask how you can help
- DON'T ask all questions at once
- Make it conversational, not robotic
- Validate the complaint is actionable
"""

            # Get or create conversation history
            if session_id not in conversations:
                conversations[session_id] = {
                    'messages': [],
                    'created_at': time.time(),
                    'language': language
                }
            
            conversation = conversations[session_id]
            conversation['messages'].append({
                'role': 'user',
                'content': message
            })
            
            # Call Gemini API (use stable 1.5-flash model)
            model = genai.GenerativeModel(
                model_name='models/gemini-1.5-flash',
                generation_config={
                    'temperature': 0.9,  # More natural
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 500,
                }
            )
            
            # Build chat history
            chat_history = []
            for msg in conversation['messages'][-10:]:  # Last 10 messages for context
                chat_history.append({
                    'role': msg['role'],
                    'parts': [msg['content']]
                })
            
            # Start chat with system instruction
            chat = model.start_chat(history=chat_history[:-1])  # Exclude last user message
            
            # Send message with system prompt prepended only on first message
            if len(conversation['messages']) == 1:
                prompt = f"{system_prompt}\n\nUser: {message}"
            else:
                prompt = message
            
            response = chat.send_message(prompt)
            ai_response = response.text.strip()
            
            # Save AI response to conversation
            conversation['messages'].append({
                'role': 'model',
                'content': ai_response
            })
            
            # Try to extract structured data
            complaint_data = self.extract_complaint_data(conversation['messages'])
            
            # Send response
            self.send_json_response({
                'session_id': session_id,
                'response': ai_response,
                'complaint_data': complaint_data,
                'conversation_complete': bool(complaint_data.get('category') and complaint_data.get('location')),
                'language': language
            })
            
        except Exception as e:
            print(f"Chat error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error_response(f"Chat failed: {str(e)}", 500)
    
    def extract_complaint_data(self, messages):
        """Extract structured complaint data from conversation"""
        complaint_data = {
            'category': None,
            'location': None,
            'urgency': 'medium',
            'contact': None,
            'description': ''
        }
        
        # Combine all user messages
        full_text = ' '.join([msg['content'] for msg in messages if msg['role'] == 'user']).lower()
        
        # Extract category (simple keyword matching)
        if any(word in full_text for word in ['road', 'pothole', 'सड़क', 'રસ્તો']):
            complaint_data['category'] = 'road'
        elif any(word in full_text for word in ['water', 'leak', 'पानी', 'પાણી']):
            complaint_data['category'] = 'water'
        elif any(word in full_text for word in ['electricity', 'power', 'बिजली', 'વીજળી']):
            complaint_data['category'] = 'electricity'
        elif any(word in full_text for word in ['garbage', 'trash', 'कचरा', 'કચરો']):
            complaint_data['category'] = 'garbage'
        elif any(word in full_text for word in ['drainage', 'sewage', 'नाली', 'ગટર']):
            complaint_data['category'] = 'drainage'
        
        # Extract urgency
        if any(word in full_text for word in ['urgent', 'emergency', 'तुरंत', 'તાત્કાલિક']):
            complaint_data['urgency'] = 'high'
        
        # Extract location (look for place names, landmarks)
        for msg in messages:
            if msg['role'] == 'user':
                # Simple location extraction - look for city names or specific markers
                text = msg['content']
                if any(marker in text.lower() for marker in ['near', 'at', 'પાસે', 'નજીક', 'पास']):
                    complaint_data['location'] = text[:100]  # Take snippet
                    break
        
        # Create description
        complaint_data['description'] = ' '.join([msg['content'] for msg in messages if msg['role'] == 'user'])[:500]
        
        return complaint_data
    
    def send_cors_headers(self):
        """Send CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '3600')
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response with CORS headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, error, status_code=400):
        """Send error response"""
        self.send_json_response({'error': error}, status_code)
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server():
    """Start the chatbot server"""
    with socketserver.TCPServer(("", PORT), GeminiChatbotHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║  SmartGriev Gemini AI Chatbot Server                    ║
╠══════════════════════════════════════════════════════════╣
║  🚀 Status: RUNNING                                      ║
║  🌐 Port: {PORT}                                          ║
║  🤖 Model: Gemini 2.5 Flash (Stable)                     ║
║  🔑 API Key: {GEMINI_API_KEY[:20]}...                    ║
║                                                          ║
║  📝 Endpoints:                                           ║
║     POST /api/chatbot/chat/                              ║
║     POST /api/chatbot/gemini/chat/                       ║
║     GET  /api/chatbot/health/                            ║
║     GET  /api/health/                                    ║
║                                                          ║
║  🌍 Supported Languages ({len(LANGUAGES)}):                              ║
║     {', '.join(list(LANGUAGES.values())[:5])}            ║
║     {', '.join(list(LANGUAGES.values())[5:])}            ║
║                                                          ║
║  ✅ Features:                                            ║
║     - Natural conversation in 10 languages               ║
║     - Context-aware responses                            ║
║     - Automatic complaint data extraction                ║
║     - CORS enabled for localhost:3000                    ║
║                                                          ║
║  🔗 Frontend URL: http://localhost:3000                  ║
╚══════════════════════════════════════════════════════════╝
""")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down chatbot server...")
            httpd.shutdown()


if __name__ == '__main__':
    run_server()
