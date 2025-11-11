import os
import json
import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Direct Google Gemini integration
import google.generativeai as genai

# Configure Gemini
GEMINI_API_KEY = 'AIzaSyA6jaqmJJOF69GjtYGz8d7lZ2DLg9nImWk'
genai.configure(api_key=GEMINI_API_KEY)

# Portal configuration (expandable)
PORTAL_MAPPINGS = {
    "electricity": {
        "portal_name": "Electricity Department",
        "api_url": "http://electricity.gov.in/api/complaints",
        "required_fields": ["location", "contact"]
    },
    "water": {
        "portal_name": "Water Supply Department", 
        "api_url": "http://watersupply.gov.in/api/complaints",
        "required_fields": ["location", "contact"]
    },
    "road": {
        "portal_name": "Municipal Roads Department",
        "api_url": "http://roads.municipal.gov.in/api/complaints",
        "required_fields": ["location", "contact"]
    },
    "garbage": {
        "portal_name": "Waste Management",
        "api_url": "http://waste.municipal.gov.in/api/complaints",
        "required_fields": ["location", "contact"]
    },
    "billing": {
        "portal_name": "Billing Department",
        "api_url": "http://billing.gov.in/api/complaints",
        "required_fields": ["contact", "evidence"]
    }
}

# Advanced multilingual system prompt with field extraction
SYSTEM_PROMPT = """You are SmartGriev Voice Assistant for citizen complaints in India.

🔴 CRITICAL RULES:

1. LANGUAGE DETECTION & MATCHING:
   - Auto-detect language from user's script/words
   - Gujarati (ગુજરાતી/gu) → Reply 100% in Gujarati
   - Marathi (मराठी/mr) → Reply 100% in Marathi  
   - Hindi (हिंदी/hi) → Reply 100% in Hindi
   - English (en) → Reply 100% in English
   - NEVER mix languages in single response!

2. PHONE-CALL STYLE:
   - Ultra-short (1-2 sentences max)
   - Friendly, warm, natural tone
   - Confirm important details clearly
   - Ask only ONE question at a time

3. FIELD EXTRACTION (collect these):
   - Category: electricity|water|road|sanitation|billing|garbage|other
   - Location: specific address + area + city
   - Contact: phone number or email
   - Urgency: low|medium|high
   - Description: brief details
   - Evidence: mention if user has photo/document

4. STRUCTURED RESPONSE FORMAT:
   First line: JSON with extracted fields (if any)
   Rest: Natural spoken reply in user's language

EXAMPLES:

Gujarati:
User: "રસ્તા પર મોટા ખાડા પડ્યા છે, અમદાવાદ નરોડા વિસ્તાર"
You: {"category":"road","location":"નરોડા વિસ્તાર, અમદાવાદ","urgency":"medium"}
સમજાયું. નરોડા વિસ્તારમાં રસ્તા પર ખાડાની ફરિયાદ છે. તમારો ફોન નંબર શું છે?

Marathi:
User: "पाण्याचा पुरवठा बंद आहे, ठाणे शहर"
You: {"category":"water","location":"ठाणे शहर","urgency":"high"}
समजलं. ठाणे शहरात पाणी बंद आहे. कृपया तुमचा फोन नंबर द्या?

Hindi:
User: "बिजली का मीटर खराब है फोटो भेजी है"
You: {"category":"electricity","urgency":"medium","evidence":"photo"}
ठीक है. मीटर की फोटो मिली. आपका पता क्या है?

English:
User: "Garbage not collected for 3 days, Borivali West"
You: {"category":"garbage","location":"Borivali West","urgency":"medium"}
Got it. Garbage issue in Borivali West. Your contact number?

MISSING FIELDS: Ask for ONE missing critical field (location/contact) per turn.
IMAGE/OCR: If user mentions photo/document, acknowledge and ask for key details.
TICKET CREATION: After collecting required fields, confirm ticket number clearly."""

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
                context = data.get('context', '')  # Optional conversation history
                
                # Get AI response
                model = genai.GenerativeModel(
                    model_name='gemini-2.0-flash-exp',
                    system_instruction=SYSTEM_PROMPT
                )
                
                # Build prompt with context if available
                full_prompt = f"CONTEXT: {context}\nUSER: {user_message}" if context else user_message
                
                response = model.generate_content(full_prompt)
                ai_response = response.text
                
                # Try to extract JSON fields from first line
                extracted_fields = {}
                spoken_reply = ai_response
                
                lines = ai_response.strip().split('\n')
                if lines and lines[0].strip().startswith('{'):
                    try:
                        extracted_fields = json.loads(lines[0].strip())
                        spoken_reply = '\n'.join(lines[1:]).strip()
                    except:
                        pass  # No JSON found, use full response
                
                # Check if we can route to portal
                portal_info = None
                if extracted_fields.get('category'):
                    category = extracted_fields['category']
                    if category in PORTAL_MAPPINGS:
                        portal = PORTAL_MAPPINGS[category]
                        # Check if all required fields are present
                        has_all_fields = all(
                            extracted_fields.get(field) 
                            for field in portal['required_fields']
                        )
                        if has_all_fields:
                            portal_info = {
                                "ready_to_submit": True,
                                "portal_name": portal['portal_name'],
                                "api_url": portal['api_url']
                            }
                        else:
                            missing = [f for f in portal['required_fields'] 
                                     if not extracted_fields.get(f)]
                            portal_info = {
                                "ready_to_submit": False,
                                "missing_fields": missing
                            }
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response_data = {
                    'response': spoken_reply or ai_response,
                    'extracted_fields': extracted_fields,
                    'portal_info': portal_info,
                    'success': True
                }
                
                self.wfile.write(json.dumps(response_data).encode('utf-8'))
                
                # Log for debugging
                print(f"✅ User: {user_message[:50]}...")
                if extracted_fields:
                    print(f"📋 Extracted: {extracted_fields}")
                print(f"💬 Reply: {spoken_reply[:50] if spoken_reply else ai_response[:50]}...")
                
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
