"""
Fast Complaint Submission Server
Ultra-lightweight HTTP server for complaint submission without Django/ML overhead
"""

import http.server
import socketserver
import json
import os
import sys
import time
from urllib.parse import parse_qs, urlparse
from pathlib import Path

# Add Django project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartgriev.settings')

# Initialize Django with minimal settings
import django
django.setup()

from django.core.files.base import ContentFile
from complaints.models import Complaint, Department
from django.contrib.auth import get_user_model

User = get_user_model()

PORT = 8000

class ComplaintHandler(http.server.BaseHTTPRequestHandler):
    """HTTP Request Handler for Complaint Submission"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_url = urlparse(self.path)
        
        # Health check
        if parsed_url.path == '/api/health/':
            self.send_json_response({
                'status': 'healthy',
                'service': 'SmartGriev Complaint Server',
                'timestamp': time.time()
            })
            return
        
        # Get complaints list
        if parsed_url.path == '/api/complaints/':
            try:
                complaints = Complaint.objects.all().order_by('-created_at')[:50]
                data = [{
                    'id': c.id,
                    'title': c.title,
                    'description': c.description,
                    'status': c.status,
                    'created_at': str(c.created_at),
                    'priority': c.priority if hasattr(c, 'priority') else 'medium'
                } for c in complaints]
                self.send_json_response({'complaints': data, 'count': len(data)})
            except Exception as e:
                self.send_error_response(f"Failed to fetch complaints: {str(e)}", 500)
            return
        
        self.send_error_response("Not found", 404)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_url = urlparse(self.path)
        
        # Complaint submission
        if parsed_url.path == '/api/complaints/submit/':
            self.handle_complaint_submission()
            return
        
        # Quick complaint submission
        if parsed_url.path == '/api/complaints/submit/quick/':
            self.handle_complaint_submission()
            return
        
        self.send_error_response("Not found", 404)
    
    def handle_complaint_submission(self):
        """Handle multipart/form-data complaint submission"""
        try:
            content_type = self.headers.get('Content-Type', '')
            
            # Parse multipart form data
            if 'multipart/form-data' in content_type:
                boundary = content_type.split('boundary=')[1]
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parse multipart data
                parts = body.split(f'--{boundary}'.encode())
                form_data = {}
                files = {}
                
                for part in parts:
                    if not part or part == b'--\r\n' or part == b'--':
                        continue
                    
                    try:
                        headers, content = part.split(b'\r\n\r\n', 1)
                        headers = headers.decode('utf-8', errors='ignore')
                        content = content.rstrip(b'\r\n')
                        
                        # Extract field name
                        if 'name="' in headers:
                            name_start = headers.find('name="') + 6
                            name_end = headers.find('"', name_start)
                            field_name = headers[name_start:name_end]
                            
                            # Check if it's a file
                            if 'filename="' in headers:
                                files[field_name] = content
                            else:
                                form_data[field_name] = content.decode('utf-8', errors='ignore')
                    except:
                        continue
                
                # Create complaint
                complaint_data = {
                    'title': form_data.get('title', 'Untitled Complaint'),
                    'description': form_data.get('description', form_data.get('complaintDescription', '')),
                    'category': form_data.get('category', 'other'),
                    'priority': form_data.get('priority', 'medium'),
                    'urgency_level': form_data.get('urgencyLevel', form_data.get('urgency_level', 'medium')),
                    'status': 'pending',
                    'location': form_data.get('location', ''),
                    'latitude': form_data.get('latitude'),
                    'longitude': form_data.get('longitude'),
                }
                
                # Get or create department
                try:
                    dept_id = form_data.get('department')
                    if dept_id:
                        complaint_data['department_id'] = int(dept_id)
                    else:
                        # Get default department or create one
                        dept, _ = Department.objects.get_or_create(
                            name='General',
                            defaults={'description': 'General complaints'}
                        )
                        complaint_data['department'] = dept
                except:
                    pass
                
                # Get user or create anonymous
                try:
                    # For now, allow anonymous complaints
                    user, _ = User.objects.get_or_create(
                        username='anonymous',
                        defaults={
                            'email': 'anonymous@smartgriev.in',
                            'first_name': 'Anonymous',
                            'last_name': 'User'
                        }
                    )
                    complaint_data['user'] = user
                except Exception as e:
                    print(f"User creation failed: {e}")
                
                # Create complaint
                complaint = Complaint.objects.create(**complaint_data)
                
                # Handle file uploads
                if 'imageFile' in files or 'image' in files:
                    image_data = files.get('imageFile') or files.get('image')
                    complaint.image_file.save(f'complaint_{complaint.id}.jpg', ContentFile(image_data), save=True)
                
                if 'audioFile' in files or 'audio' in files:
                    audio_data = files.get('audioFile') or files.get('audio')
                    complaint.audio_file.save(f'complaint_{complaint.id}.webm', ContentFile(audio_data), save=True)
                
                # Success response
                self.send_json_response({
                    'success': True,
                    'message': 'Complaint submitted successfully!',
                    'complaint': {
                        'id': complaint.id,
                        'title': complaint.title,
                        'status': complaint.status,
                        'tracking_number': f'COMP-{complaint.id:06d}',
                        'created_at': str(complaint.created_at)
                    }
                }, status_code=201)
                
            else:
                # Handle JSON data
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Create complaint from JSON
                user, _ = User.objects.get_or_create(
                    username='anonymous',
                    defaults={'email': 'anonymous@smartgriev.in'}
                )
                
                complaint = Complaint.objects.create(
                    user=user,
                    title=data.get('title', 'Untitled'),
                    description=data.get('description', ''),
                    category=data.get('category', 'other'),
                    priority=data.get('priority', 'medium'),
                    status='pending'
                )
                
                self.send_json_response({
                    'success': True,
                    'complaint_id': complaint.id,
                    'tracking_number': f'COMP-{complaint.id:06d}'
                }, status_code=201)
                
        except Exception as e:
            print(f"Complaint submission error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.send_error_response(f"Complaint submission failed: {str(e)}", 500)
    
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
    """Start the complaint server"""
    with socketserver.TCPServer(("", PORT), ComplaintHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║  SmartGriev Complaint Submission Server                 ║
╠══════════════════════════════════════════════════════════╣
║  🚀 Status: RUNNING                                      ║
║  🌐 Port: {PORT}                                          ║
║  📝 Endpoints:                                           ║
║     POST /api/complaints/submit/                         ║
║     POST /api/complaints/submit/quick/                   ║
║     GET  /api/complaints/                                ║
║     GET  /api/health/                                    ║
║                                                          ║
║  ✅ Features:                                            ║
║     - Fast complaint submission                          ║
║     - Image & Audio file upload                          ║
║     - CORS enabled for localhost:3000                    ║
║     - Anonymous submissions allowed                      ║
║                                                          ║
║  🔗 Frontend URL: http://localhost:3000                  ║
╚══════════════════════════════════════════════════════════╝
""")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Shutting down complaint server...")
            httpd.shutdown()


if __name__ == '__main__':
    run_server()
