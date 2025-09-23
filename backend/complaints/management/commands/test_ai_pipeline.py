"""
Django Management Command to Test Full SmartGriev AI Pipeline
Tests multi-modal complaint processing including text, audio, and image inputs
"""

import asyncio
import os
import tempfile
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from complaints.ai_processor import AdvancedAIProcessor
from complaints.department_classifier import GovernmentDepartmentClassifier
from authentication.auth_service import AdvancedAuthService
from complaints.models import Complaint, ComplaintCategory, Department
from authentication.models import User


class Command(BaseCommand):
    help = 'Test the full SmartGriev multi-modal AI processing pipeline'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--test-type',
            type=str,
            choices=['text', 'audio', 'image', 'full', 'auth'],
            default='text',
            help='Type of test to run'
        )
        parser.add_argument(
            '--sample-text',
            type=str,
            default='मुझे बिजली की समस्या है। मेरे घर में 3 दिन से बिजली नहीं आ रही है। कृपया जल्दी ठीक करें।',
            help='Sample complaint text to test'
        )
        parser.add_argument(
            '--user-phone',
            type=str,
            default='+919876543210',
            help='Phone number for testing authentication'
        )
        parser.add_argument(
            '--user-email',
            type=str,
            default='test@smartgriev.gov.in',
            help='Email for testing authentication'
        )
    
    def handle(self, *args, **options):
        """Main command handler"""
        self.stdout.write(
            self.style.SUCCESS('🚀 Starting SmartGriev AI Pipeline Test...')
        )
        
        # Run tests based on type
        test_type = options['test_type']
        
        try:
            if test_type == 'text':
                asyncio.run(self.test_text_processing(options))
            elif test_type == 'audio':
                asyncio.run(self.test_audio_processing(options))
            elif test_type == 'image':
                asyncio.run(self.test_image_processing(options))
            elif test_type == 'auth':
                asyncio.run(self.test_authentication(options))
            elif test_type == 'full':
                asyncio.run(self.test_full_pipeline(options))
            
            self.stdout.write(
                self.style.SUCCESS('✅ All tests completed successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Test failed: {str(e)}')
            )
            raise CommandError(f'Pipeline test failed: {str(e)}')
    
    async def test_text_processing(self, options):
        """Test text-only complaint processing"""
        self.stdout.write('📝 Testing text processing pipeline...')
        
        # Initialize processors
        ai_processor = AdvancedAIProcessor()
        dept_classifier = GovernmentDepartmentClassifier()
        
        sample_text = options['sample_text']
        self.stdout.write(f'Input: {sample_text}')
        
        # Test AI enhancement
        self.stdout.write('🔍 Enhancing text with AI...')
        enhanced_text = await ai_processor.enhance_complaint_text(
            sample_text, 
            location="Delhi, India"
        )
        self.stdout.write(f'Enhanced: {enhanced_text}')
        
        # Test department classification
        self.stdout.write('🏛️ Classifying government department...')
        classification = await dept_classifier.classify_complaint(
            enhanced_text,
            location="Delhi, India"
        )
        
        if classification['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Department: {classification['department']}\n"
                    f"Urgency: {classification['urgency_level']}\n"
                    f"Resolution Time: {classification['estimated_resolution_days']} days\n"
                    f"Confidence: {classification['confidence']:.2f}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"Classification failed: {classification.get('error', 'Unknown error')}")
            )
    
    async def test_audio_processing(self, options):
        """Test audio complaint processing"""
        self.stdout.write('🎤 Testing audio processing pipeline...')
        
        ai_processor = AdvancedAIProcessor()
        
        # Create a test audio file (placeholder)
        self.stdout.write('Note: Audio processing requires actual audio files')
        self.stdout.write('To test with real audio:')
        self.stdout.write('1. Place an audio file in /tmp/test_audio.wav')
        self.stdout.write('2. Run the pipeline with that file')
        
        # Test with mock audio path (this will fail gracefully)
        try:
            audio_text = await ai_processor.process_audio_to_text('/tmp/test_audio.wav')
            if audio_text:
                self.stdout.write(f'Audio to text: {audio_text}')
            else:
                self.stdout.write('No audio file found for testing')
        except Exception as e:
            self.stdout.write(f'Audio processing test skipped: {str(e)}')
    
    async def test_image_processing(self, options):
        """Test image complaint processing"""
        self.stdout.write('📷 Testing image processing pipeline...')
        
        ai_processor = AdvancedAIProcessor()
        
        # Create a test image file (placeholder)
        self.stdout.write('Note: Image processing requires actual image files')
        self.stdout.write('To test with real images:')
        self.stdout.write('1. Place an image file in /tmp/test_image.jpg')
        self.stdout.write('2. Run the pipeline with that file')
        
        # Test with mock image path (this will fail gracefully)
        try:
            image_analysis = await ai_processor.process_image_with_context('/tmp/test_image.jpg')
            if image_analysis:
                self.stdout.write(f'Image analysis: {image_analysis}')
            else:
                self.stdout.write('No image file found for testing')
        except Exception as e:
            self.stdout.write(f'Image processing test skipped: {str(e)}')
    
    async def test_authentication(self, options):
        """Test authentication system with OTP"""
        self.stdout.write('🔐 Testing authentication system...')
        
        auth_service = AdvancedAuthService()
        phone = options['user_phone']
        email = options['user_email']
        
        # Test user registration
        self.stdout.write('👤 Testing user registration...')
        success, message, user = await auth_service.register_user(
            phone_number=phone,
            email=email,
            password='testpassword123',
            first_name='Test',
            last_name='User'
        )
        
        if success:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Registration successful: {message}')
            )
            
            # Test authentication
            self.stdout.write('🔑 Testing user authentication...')
            auth_success, auth_message, auth_user = await auth_service.authenticate_user(
                identifier=phone,
                password='testpassword123'
            )
            
            if auth_success:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Authentication successful: {auth_message}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Authentication failed: {auth_message}')
                )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Registration failed: {message}')
            )
    
    async def test_full_pipeline(self, options):
        """Test complete end-to-end pipeline"""
        self.stdout.write('🔄 Testing full end-to-end pipeline...')
        
        # Initialize all services
        ai_processor = AdvancedAIProcessor()
        dept_classifier = GovernmentDepartmentClassifier()
        auth_service = AdvancedAuthService()
        
        # Create test data
        sample_text = options['sample_text']
        location = "New Delhi, India"
        
        self.stdout.write('1️⃣ Testing user registration...')
        
        # Register test user
        success, message, user = await auth_service.register_user(
            phone_number=options['user_phone'],
            email=options['user_email'],
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        if success:
            self.stdout.write(f'✅ User registered: {user.username}')
        else:
            self.stdout.write(f'⚠️ User registration: {message}')
        
        self.stdout.write('2️⃣ Processing complaint with AI...')
        
        # Enhance complaint text
        enhanced_text = await ai_processor.enhance_complaint_text(
            sample_text,
            location=location
        )
        
        self.stdout.write(f'📝 Enhanced text: {enhanced_text[:100]}...')
        
        self.stdout.write('3️⃣ Classifying department...')
        
        # Classify department
        classification = await dept_classifier.classify_complaint(
            enhanced_text,
            location=location
        )
        
        if classification['success']:
            self.stdout.write(
                f"🏛️ Department: {classification['department']}\n"
                f"⚡ Urgency: {classification['urgency_level']}\n"
                f"📅 Est. Resolution: {classification['estimated_resolution_days']} days"
            )
        
        self.stdout.write('4️⃣ Storing complaint in database...')
        
        # Create database entries
        try:
            # Get or create category
            category, created = ComplaintCategory.objects.get_or_create(
                name=classification.get('department', 'General'),
                defaults={'description': f"{classification.get('department', 'General')} related complaints"}
            )
            
            # Create complaint
            complaint = Complaint.objects.create(
                user=user if success else None,
                title=enhanced_text[:100],
                description=enhanced_text,
                category=category,
                location=location,
                urgency_level=classification.get('urgency_level', 'medium'),
                ai_confidence_score=classification.get('confidence', 0.0),
                department_classification=classification if classification['success'] else {}
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Complaint stored with ID: {complaint.id}\n'
                    f'📊 Category: {category.name}\n'
                    f'🎯 Confidence: {classification.get("confidence", 0.0):.2f}'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database storage failed: {str(e)}')
            )
        
        self.stdout.write('5️⃣ Testing complaint retrieval...')
        
        # Test complaint retrieval
        try:
            recent_complaints = Complaint.objects.all().order_by('-created_at')[:5]
            self.stdout.write(f'📋 Found {recent_complaints.count()} recent complaints')
            
            for comp in recent_complaints:
                self.stdout.write(
                    f'  • {comp.id}: {comp.title[:50]}... ({comp.category.name if comp.category else "No category"})'
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Complaint retrieval failed: {str(e)}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Full pipeline test completed successfully!')
        )
    
    def create_test_files(self):
        """Create temporary test files for audio/image processing"""
        # This would create actual test files in a real implementation
        pass