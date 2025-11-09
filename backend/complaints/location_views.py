"""
Location and GIS API Views
Provides geocoding, reverse geocoding, place search, Plus Codes, and ward assignment
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
import logging

from .services.location_service import (
    mapmyindia_service,
    ward_service,
    PlusCode
)

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def geocode_address(request):
    """
    Convert address to coordinates with Plus Code
    
    POST /api/complaints/geocode/
    Body: {"address": "Connaught Place, New Delhi"}
    
    Returns:
        {
            "latitude": 28.6315,
            "longitude": 77.2197,
            "formatted_address": "Connaught Place, New Delhi, Delhi 110001",
            "plus_code": "7JWWJ6J9+2V",
            "accuracy": "high",
            "components": {
                "street": "Connaught Place",
                "city": "New Delhi",
                "state": "Delhi",
                "postal_code": "110001",
                "country": "India"
            },
            "ward": {
                "ward_id": "Central",
                "ward_name": "Connaught Place",
                "city": "Delhi",
                "confidence": "high"
            }
        }
    """
    address = request.data.get('address')
    
    if not address:
        return Response(
            {'error': 'Address is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Geocode address
    result = mapmyindia_service.geocode(address)
    
    if not result:
        return Response(
            {'error': 'Could not geocode address'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Assign ward if coordinates available
    if result.get('latitude') and result.get('longitude'):
        city = result.get('components', {}).get('city')
        ward = ward_service.assign_ward(
            result['latitude'],
            result['longitude'],
            city
        )
        
        if ward:
            result['ward'] = ward
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def reverse_geocode(request):
    """
    Convert coordinates to address with Plus Code
    
    POST /api/complaints/reverse-geocode/
    Body: {"latitude": 28.6315, "longitude": 77.2197}
    
    Returns:
        {
            "address": "Connaught Place, New Delhi, Delhi 110001",
            "formatted_address": "Connaught Place, New Delhi, Delhi 110001",
            "plus_code": "7JWWJ6J9+2V",
            "accuracy": "high",
            "components": {
                "street": "Connaught Place",
                "city": "New Delhi",
                "state": "Delhi",
                "postal_code": "110001",
                "country": "India"
            },
            "ward": {
                "ward_id": "Central",
                "ward_name": "Connaught Place",
                "city": "Delhi",
                "confidence": "high"
            }
        }
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    
    if latitude is None or longitude is None:
        return Response(
            {'error': 'Latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid latitude or longitude format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate coordinate ranges
    if not (-90 <= latitude <= 90):
        return Response(
            {'error': 'Latitude must be between -90 and 90'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (-180 <= longitude <= 180):
        return Response(
            {'error': 'Longitude must be between -180 and 180'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reverse geocode
    result = mapmyindia_service.reverse_geocode(latitude, longitude)
    
    if not result:
        # Fallback response with Plus Code
        result = {
            'address': f"Lat: {latitude:.6f}, Lng: {longitude:.6f}",
            'formatted_address': f"Coordinates: {latitude:.6f}, {longitude:.6f}",
            'plus_code': PlusCode.encode(latitude, longitude),
            'accuracy': 'low',
            'components': {}
        }
    
    # Assign ward
    city = result.get('components', {}).get('city')
    ward = ward_service.assign_ward(latitude, longitude, city)
    
    if ward:
        result['ward'] = ward
    
    return Response(result, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def search_places(request):
    """
    Search for places by name
    
    POST /api/complaints/search-places/
    Body: {
        "query": "hospitals near me",
        "latitude": 28.6315,  // Optional for proximity search
        "longitude": 77.2197,  // Optional for proximity search
        "radius": 5000  // Optional, in meters (default 5000)
    }
    
    Returns:
        {
            "results": [
                {
                    "name": "Max Hospital",
                    "address": "1, Institutional Area, Press Enclave Road, Saket",
                    "latitude": 28.5233,
                    "longitude": 77.2089,
                    "plus_code": "7JWWGWF5+QR",
                    "place_id": "abc123",
                    "types": ["hospital", "health"]
                },
                ...
            ],
            "count": 10
        }
    """
    query = request.data.get('query')
    
    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    radius = request.data.get('radius', 5000)
    
    location = None
    if latitude is not None and longitude is not None:
        try:
            location = (float(latitude), float(longitude))
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid latitude or longitude format'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Search places
    results = mapmyindia_service.search_places(query, location, radius)
    
    return Response({
        'results': results,
        'count': len(results)
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def generate_plus_code(request):
    """
    Generate Plus Code from coordinates
    
    POST /api/complaints/plus-code/generate/
    Body: {"latitude": 28.6315, "longitude": 77.2197, "code_length": 10}
    
    Returns:
        {
            "plus_code": "7JWWJ6J9+2V",
            "latitude": 28.6315,
            "longitude": 77.2197,
            "code_length": 10,
            "precision": "~14 meters"
        }
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    code_length = request.data.get('code_length', 10)
    
    if latitude is None or longitude is None:
        return Response(
            {'error': 'Latitude and longitude are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        code_length = int(code_length)
    except (ValueError, TypeError):
        return Response(
            {'error': 'Invalid input format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate inputs
    if not (-90 <= latitude <= 90):
        return Response(
            {'error': 'Latitude must be between -90 and 90'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (-180 <= longitude <= 180):
        return Response(
            {'error': 'Longitude must be between -180 and 180'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (2 <= code_length <= 15):
        code_length = 10
    
    # Generate Plus Code
    plus_code = PlusCode.encode(latitude, longitude, code_length)
    
    # Precision mapping
    precision_map = {
        2: "~2220 km",
        4: "~110 km",
        6: "~5.5 km",
        8: "~275 m",
        10: "~14 m",
        11: "~3.5 m",
        12: "~70 cm",
        13: "~18 cm",
        14: "~3.5 cm",
        15: "~9 mm"
    }
    
    return Response({
        'plus_code': plus_code,
        'latitude': latitude,
        'longitude': longitude,
        'code_length': code_length,
        'precision': precision_map.get(code_length, "~14 m")
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def decode_plus_code(request):
    """
    Decode Plus Code to coordinates
    
    POST /api/complaints/plus-code/decode/
    Body: {"plus_code": "7JWWJ6J9+2V"}
    
    Returns:
        {
            "latitude": 28.631250,
            "longitude": 77.219688,
            "latitude_hi": 28.631375,
            "longitude_hi": 77.219813,
            "code_length": 9,
            "is_valid": true,
            "precision": "~14 meters"
        }
    """
    plus_code = request.data.get('plus_code')
    
    if not plus_code:
        return Response(
            {'error': 'Plus Code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate Plus Code
    if not PlusCode.is_valid(plus_code):
        return Response(
            {'error': 'Invalid Plus Code format'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Decode Plus Code
        result = PlusCode.decode(plus_code)
        result['is_valid'] = True
        result['plus_code'] = plus_code
        
        # Add precision info
        precision_map = {
            2: "~2220 km",
            4: "~110 km",
            6: "~5.5 km",
            8: "~275 m",
            9: "~14 m",
            10: "~14 m",
            11: "~3.5 m"
        }
        result['precision'] = precision_map.get(result['code_length'], "~14 m")
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Plus Code decode error: {e}")
        return Response(
            {'error': 'Could not decode Plus Code'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def assign_ward(request):
    """
    Assign ward based on coordinates or address
    
    POST /api/complaints/assign-ward/
    Body: {
        "latitude": 28.6315,
        "longitude": 77.2197,
        "city": "Delhi"  // Optional, improves performance
    }
    OR
    Body: {
        "address_components": {
            "city": "Mumbai",
            "locality": "Colaba"
        }
    }
    
    Returns:
        {
            "ward_id": "Central",
            "ward_name": "Connaught Place",
            "city": "Delhi",
            "confidence": "high"
        }
    """
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')
    city = request.data.get('city')
    address_components = request.data.get('address_components')
    
    ward = None
    
    # Try coordinate-based assignment first
    if latitude is not None and longitude is not None:
        try:
            latitude = float(latitude)
            longitude = float(longitude)
            ward = ward_service.assign_ward(latitude, longitude, city)
        except (ValueError, TypeError):
            pass
    
    # Try address-based assignment if no ward found
    if not ward and address_components:
        ward = ward_service.get_ward_from_address(address_components)
    
    if ward:
        return Response(ward, status=status.HTTP_200_OK)
    else:
        return Response(
            {
                'error': 'Could not assign ward',
                'message': 'Location not found in ward boundaries or insufficient data'
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_supported_cities(request):
    """
    Get list of cities with ward boundary data
    
    GET /api/complaints/supported-cities/
    
    Returns:
        {
            "cities": [
                {
                    "name": "Mumbai",
                    "ward_count": 24,
                    "coverage": "complete"
                },
                ...
            ],
            "total_cities": 3
        }
    """
    cities_data = []
    
    for city_name, wards in ward_service.WARD_BOUNDARIES.items():
        cities_data.append({
            'name': city_name,
            'ward_count': len(wards),
            'coverage': 'partial' if len(wards) < 10 else 'complete'
        })
    
    return Response({
        'cities': cities_data,
        'total_cities': len(cities_data)
    }, status=status.HTTP_200_OK)
