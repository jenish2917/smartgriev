"""
MapMyIndia Location Service
Provides geocoding, reverse geocoding, place search, Plus Codes, and ward assignment
"""
import requests
import logging
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PlusCode:
    """
    Simplified Plus Code (Open Location Code) implementation
    Compatible with Google's Plus Codes
    """
    
    # Code alphabet (excludes ambiguous characters)
    CODE_ALPHABET = "23456789CFGHJMPQRVWX"
    ENCODING_BASE = 20
    SEPARATOR = '+'
    SEPARATOR_POSITION = 8
    PAIR_CODE_LENGTH = 10
    
    @classmethod
    def encode(cls, latitude: float, longitude: float, code_length: int = 10) -> str:
        """
        Encode latitude and longitude into a Plus Code
        
        Simplified implementation for demonstration
        """
        # Normalize
        lat = max(-90, min(90, latitude))
        lng = ((longitude + 180) % 360) - 180
        
        # Shift to positive
        lat = lat + 90
        lng = lng + 180
        
        # Simple encoding (this is a simplified version)
        # For production, use: pip install openlocationcode
        code = ""
        
        # Encode in pairs
        for i in range(min(code_length // 2, 4)):
            lat_digit = int((lat * cls.ENCODING_BASE**(i+1)) / 180) % cls.ENCODING_BASE
            lng_digit = int((lng * cls.ENCODING_BASE**(i+1)) / 360) % cls.ENCODING_BASE
            
            code += cls.CODE_ALPHABET[lng_digit]
            code += cls.CODE_ALPHABET[lat_digit]
            
            if i == 3:  # Add separator after 4 pairs
                code += cls.SEPARATOR
        
        # Add remaining digits
        for i in range(code_length - 8):
            lat_digit = int((lat * cls.ENCODING_BASE**(i+5)) / 180) % cls.ENCODING_BASE
            code += cls.CODE_ALPHABET[lat_digit]
        
        return code if cls.SEPARATOR in code else code[:8] + cls.SEPARATOR + code[8:]
    
    @classmethod
    def decode(cls, code: str) -> Dict[str, float]:
        """
        Decode a Plus Code back to coordinates
        
        Simplified implementation
        """
        code = code.upper().replace(cls.SEPARATOR, '')
        
        lat = 0.0
        lng = 0.0
        
        # Decode pairs
        for i in range(0, min(len(code), 8), 2):
            lng_val = cls.CODE_ALPHABET.index(code[i])
            lat_val = cls.CODE_ALPHABET.index(code[i + 1])
            
            lat += lat_val / (cls.ENCODING_BASE ** (i//2 + 1)) * 180
            lng += lng_val / (cls.ENCODING_BASE ** (i//2 + 1)) * 360
        
        # Convert back
        latitude = lat - 90
        longitude = lng - 180
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'latitude_hi': latitude + 0.000125,  # Approximate precision
            'longitude_hi': longitude + 0.000125,
            'code_length': len(code)
        }
    
    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Check if a Plus Code is valid"""
        try:
            code = code.upper()
            if cls.SEPARATOR not in code:
                return False
            
            parts = code.split(cls.SEPARATOR)
            if len(parts) != 2:
                return False
            
            # Check first part is even length
            if len(parts[0]) % 2 != 0:
                return False
            
            # Check characters
            for char in code.replace(cls.SEPARATOR, ''):
                if char not in cls.CODE_ALPHABET:
                    return False
            
            return True
        except:
            return False


class MapMyIndiaService:
    """
    MapMyIndia API Service for location operations
    Uses REST API Key for authentication (no OAuth needed for basic APIs)
    """
    
    def __init__(self):
        self.api_key = settings.MAPMYINDIA_CONFIG.get('API_KEY')
        # MapMyIndia uses different base URLs for different APIs
        self.base_url = 'https://apis.mapmyindia.com/advancedmaps/v1'
        self.session = requests.Session()
        # MapMyIndia REST API uses API key in URL parameters, not headers
        self.session.headers.update({
            'Content-Type': 'application/json'
        })
    
    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Convert address to coordinates using MapMyIndia Geocoding API
        
        Args:
            address: Address string to geocode
            
        Returns:
            Dict with latitude, longitude, formatted_address, plus_code, and components
        """
        cache_key = f'geocode_{address}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # MapMyIndia Geocoding API endpoint
            url = f"{self.base_url}/{self.api_key}/geo_code"
            params = {
                'addr': address
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # MapMyIndia response format
            if data.get('copResults') and len(data['copResults']) > 0:
                result = data['copResults'][0]
                
                latitude = float(result.get('latitude', result.get('lat', 0)))
                longitude = float(result.get('longitude', result.get('lng', 0)))
                
                # Generate Plus Code
                plus_code = PlusCode.encode(latitude, longitude)
                
                geocode_result = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'formatted_address': result.get('formatted_address', address),
                    'plus_code': plus_code,
                    'accuracy': 'high' if result.get('geocodeLevel') in ['HOUSE_NUMBER', 'PREMISE'] else 'medium',
                    'components': {
                        'street': result.get('street'),
                        'city': result.get('city') or result.get('district'),
                        'state': result.get('state'),
                        'postal_code': result.get('pincode'),
                        'country': 'India'
                    }
                }
                
                # Cache for 24 hours
                cache.set(cache_key, geocode_result, 86400)
                
                return geocode_result
            
            logger.warning(f"No geocoding results for address: {address}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MapMyIndia geocoding error: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Convert coordinates to address using MapMyIndia Reverse Geocoding API
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dict with address, formatted_address, plus_code, and components
        """
        cache_key = f'reverse_geocode_{latitude}_{longitude}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # MapMyIndia Reverse Geocoding API endpoint
            url = f"{self.base_url}/{self.api_key}/rev_geocode"
            params = {
                'lat': latitude,
                'lng': longitude
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # MapMyIndia response format
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                
                # Generate Plus Code
                plus_code = PlusCode.encode(latitude, longitude)
                
                reverse_geocode_result = {
                    'address': result.get('formatted_address', f"Lat: {latitude}, Lng: {longitude}"),
                    'formatted_address': result.get('formatted_address'),
                    'plus_code': plus_code,
                    'accuracy': 'high',
                    'components': {
                        'street': result.get('street'),
                        'city': result.get('city') or result.get('district'),
                        'state': result.get('state'),
                        'postal_code': result.get('pincode'),
                        'country': 'India'
                    }
                }
                
                # Cache for 24 hours
                cache.set(cache_key, reverse_geocode_result, 86400)
                
                return reverse_geocode_result
            
            logger.warning(f"No reverse geocoding results for coordinates: {latitude}, {longitude}")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MapMyIndia reverse geocoding error: {e}")
            return None
    
    def search_places(self, query: str, location: Optional[Tuple[float, float]] = None, 
                     radius: int = 5000) -> List[Dict[str, Any]]:
        """
        Search for places by name using MapMyIndia Place Search API
        
        Args:
            query: Search query string
            location: Optional (latitude, longitude) tuple for proximity search
            radius: Search radius in meters (default 5000m = 5km)
            
        Returns:
            List of place results with name, address, coordinates, and plus_code
        """
        cache_key = f'search_{query}_{location}_{radius}'
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        try:
            # MapMyIndia Place Search (Atlas API)
            url = f"{self.base_url}/{self.api_key}/place_search/json"
            params = {
                'query': query
            }
            
            if location:
                params['location'] = f"{location[0]},{location[1]}"
                params['radius'] = radius
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            places = []
            if data.get('suggestedLocations'):
                for result in data['suggestedLocations'][:10]:  # Limit to 10 results
                    lat = float(result.get('latitude', result.get('lat', 0)))
                    lng = float(result.get('longitude', result.get('lng', 0)))
                    
                    place = {
                        'name': result.get('placeName', result.get('name')),
                        'address': result.get('placeAddress', result.get('address')),
                        'latitude': lat,
                        'longitude': lng,
                        'plus_code': PlusCode.encode(lat, lng),
                        'place_id': result.get('eLoc'),  # MapMyIndia's unique location code
                        'types': [result.get('type', 'place')]
                    }
                    places.append(place)
            
            # Cache for 1 hour
            cache.set(cache_key, places, 3600)
            
            return places
            
        except requests.exceptions.RequestException as e:
            logger.error(f"MapMyIndia place search error: {e}")
            return []


class WardAssignmentService:
    """
    Service to automatically assign complaints to wards based on location
    """
    
    # Ward boundaries for major Indian cities (example data)
    # In production, this should be loaded from a PostGIS database
    WARD_BOUNDARIES = {
        'Mumbai': [
            {'ward_id': 'A', 'name': 'Colaba', 'bounds': {'min_lat': 18.88, 'max_lat': 18.95, 'min_lng': 72.81, 'max_lng': 72.84}},
            {'ward_id': 'B', 'name': 'Mazgaon', 'bounds': {'min_lat': 18.95, 'max_lat': 19.00, 'min_lng': 72.83, 'max_lng': 72.86}},
            {'ward_id': 'C', 'name': 'Byculla', 'bounds': {'min_lat': 18.97, 'max_lat': 19.02, 'min_lng': 72.83, 'max_lng': 72.85}},
        ],
        'Delhi': [
            {'ward_id': 'Central', 'name': 'Connaught Place', 'bounds': {'min_lat': 28.61, 'max_lat': 28.65, 'min_lng': 77.20, 'max_lng': 77.23}},
            {'ward_id': 'South', 'name': 'Greater Kailash', 'bounds': {'min_lat': 28.52, 'max_lat': 28.55, 'min_lng': 77.23, 'max_lng': 77.26}},
        ],
        'Bangalore': [
            {'ward_id': 'East', 'name': 'Whitefield', 'bounds': {'min_lat': 12.96, 'max_lat': 12.98, 'min_lng': 77.72, 'max_lng': 77.75}},
            {'ward_id': 'Central', 'name': 'MG Road', 'bounds': {'min_lat': 12.97, 'max_lat': 12.98, 'min_lng': 77.59, 'max_lng': 77.61}},
        ]
    }
    
    @classmethod
    def assign_ward(cls, latitude: float, longitude: float, city: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Assign ward based on coordinates
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            city: Optional city name (improves performance)
            
        Returns:
            Dict with ward_id, ward_name, city, or None if no match
        """
        # If city is specified, check only that city's wards
        cities_to_check = [city] if city and city in cls.WARD_BOUNDARIES else cls.WARD_BOUNDARIES.keys()
        
        for city_name in cities_to_check:
            for ward in cls.WARD_BOUNDARIES.get(city_name, []):
                bounds = ward['bounds']
                
                if (bounds['min_lat'] <= latitude <= bounds['max_lat'] and 
                    bounds['min_lng'] <= longitude <= bounds['max_lng']):
                    return {
                        'ward_id': ward['ward_id'],
                        'ward_name': ward['name'],
                        'city': city_name,
                        'confidence': 'high'
                    }
        
        return None
    
    @classmethod
    def get_ward_from_address(cls, address_components: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Extract ward information from address components
        
        Args:
            address_components: Dict with city, state, locality, etc.
            
        Returns:
            Ward information or None
        """
        city = address_components.get('city')
        locality = address_components.get('locality') or address_components.get('street')
        
        if not city:
            return None
        
        # Search ward by locality name
        for city_name, wards in cls.WARD_BOUNDARIES.items():
            if city_name.lower() in city.lower():
                for ward in wards:
                    if locality and ward['name'].lower() in locality.lower():
                        return {
                            'ward_id': ward['ward_id'],
                            'ward_name': ward['name'],
                            'city': city_name,
                            'confidence': 'medium'
                        }
        
        return None


# Singleton instances
mapmyindia_service = MapMyIndiaService()
ward_service = WardAssignmentService()
