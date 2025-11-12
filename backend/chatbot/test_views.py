import os
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_env(request):
    """Test endpoint to check environment variables"""
    return JsonResponse({
        'gemini_key_exists': bool(os.getenv('GEMINI_API_KEY')),
        'gemini_key_length': len(os.getenv('GEMINI_API_KEY', '')),
        'groq_key_exists': bool(os.getenv('GROQ_API_KEY')),
        'groq_key_length': len(os.getenv('GROQ_API_KEY', '')),
    })
