"""
AgriSense AI - Input Validation Utilities
Comprehensive validation for user inputs and data
"""

import re
import phonenumbers
from typing import Dict, Any, List, Optional, Tuple
import logging
from email_validator import validate_email, EmailNotValidError

class ValidationError(Exception):
    """Custom validation error"""
    pass

def validate_phone(phone: str, country_code: str = "NG") -> bool:
    """
    Validate phone number format
    
    Args:
        phone (str): Phone number to validate
        country_code (str): Country code (default: Nigeria)
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not phone:
            return False
        
        # Parse phone number
        parsed_number = phonenumbers.parse(phone, country_code)
        
        # Check if valid
        return phonenumbers.is_valid_number(parsed_number)
        
    except phonenumbers.NumberParseException:
        return False

def format_phone(phone: str, country_code: str = "NG") -> str:
    """
    Format phone number to international format
    
    Args:
        phone (str): Phone number to format
        country_code (str): Country code
        
    Returns:
        str: Formatted phone number
        
    Raises:
        ValidationError: If phone number is invalid
    """
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError("Invalid phone number format")
        
        return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        
    except phonenumbers.NumberParseException as e:
        raise ValidationError(f"Phone number parsing error: {str(e)}")

def validate_email_address(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not email:
            return False
        
        validate_email(email)
        return True
        
    except EmailNotValidError:
        return False

def validate_location(location: str) -> bool:
    """
    Validate location string
    
    Args:
        location (str): Location to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not location or len(location.strip()) < 2:
        return False
    
    # Check for basic location format
    location = location.strip()
    
    # Should contain only letters, spaces, commas, and common punctuation
    if not re.match(r'^[a-zA-Z\s,.-]+$', location):
        return False
    
    # Check length
    if len(location) > 100:
        return False
    
    # Nigerian states and common locations
    nigerian_locations = [
        'abia', 'adamawa', 'akwa ibom', 'anambra', 'bauchi', 'bayelsa', 'benue',
        'borno', 'cross river', 'delta', 'ebonyi', 'edo', 'ekiti', 'enugu',
        'gombe', 'imo', 'jigawa', 'kaduna', 'kano', 'katsina', 'kebbi', 'kogi',
        'kwara', 'lagos', 'nasarawa', 'niger', 'ogun', 'ondo', 'osun', 'oyo',
        'plateau', 'rivers', 'sokoto', 'taraba', 'yobe', 'zamfara', 'abuja',
        'nigeria', 'ng'
    ]
    
    location_lower = location.lower()
    
    # Check if location contains any Nigerian reference
    if any(place in location_lower for place in nigerian_locations):
        return True
    
    # Allow other locations but with stricter validation
    words = location_lower.split()
    if len(words) >= 1 and all(len(word) >= 2 for word in words):
        return True
    
    return False

def validate_name(name: str) -> bool:
    """
    Validate person's name
    
    Args:
        name (str): Name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not name or len(name.strip()) < 2:
        return False
    
    name = name.strip()
    
    # Check length
    if len(name) > 100:
        return False
    
    # Should contain only letters, spaces, apostrophes, and hyphens
    if not re.match(r"^[a-zA-Z\s'-]+$", name):
        return False
    
    # Should have at least one letter
    if not re.search(r'[a-zA-Z]', name):
        return False
    
    return True

def validate_language_code(language_code: str) -> bool:
    """
    Validate language code
    
    Args:
        language_code (str): Language code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    supported_languages = ['en', 'ha', 'yo', 'ig', 'ff']
    return language_code in supported_languages

def validate_crop_name(crop: str) -> bool:
    """
    Validate crop name
    
    Args:
        crop (str): Crop name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not crop or len(crop.strip()) < 2:
        return False
    
    crop = crop.strip()
    
    # Check length
    if len(crop) > 50:
        return False
    
    # Should contain only letters, spaces, and common punctuation
    if not re.match(r'^[a-zA-Z\s-]+$', crop):
        return False
    
    # Common crops
    common_crops = [
        'rice', 'maize', 'corn', 'tomato', 'pepper', 'onion', 'cassava', 'yam',
        'plantain', 'banana', 'beans', 'groundnut', 'peanut', 'soybean', 'millet',
        'sorghum', 'wheat', 'barley', 'cocoa', 'coffee', 'cotton', 'sugarcane',
        'okra', 'spinach', 'lettuce', 'cabbage', 'carrot', 'cucumber', 'watermelon',
        'melon', 'pumpkin', 'ginger', 'garlic', 'potato', 'sweet potato'
    ]
    
    crop_lower = crop.lower()
    
    # Check if it's a known crop
    if any(known_crop in crop_lower for known_crop in common_crops):
        return True
    
    # Allow other crop names but ensure they look reasonable
    words = crop_lower.split()
    if len(words) <= 3 and all(len(word) >= 2 for word in words):
        return True
    
    return False

def validate_farm_size(size: float) -> bool:
    """
    Validate farm size in hectares
    
    Args:
        size (float): Farm size to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if size is None:
        return True  # Optional field
    
    # Must be positive and reasonable
    return 0.01 <= size <= 10000  # 0.01 hectares to 10,000 hectares

def validate_farming_experience(years: int) -> bool:
    """
    Validate farming experience in years
    
    Args:
        years (int): Years of experience to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if years is None:
        return True  # Optional field
    
    # Must be non-negative and reasonable
    return 0 <= years <= 80

def validate_password(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength
    
    Args:
        password (str): Password to validate
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if not password:
        errors.append("Password is required")
        return False, errors
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if len(password) > 128:
        errors.append("Password must be less than 128 characters")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    # Check for common weak passwords
    weak_patterns = [
        r'12345', r'password', r'qwerty', r'abc', r'admin', r'user'
    ]
    
    password_lower = password.lower()
    for pattern in weak_patterns:
        if pattern in password_lower:
            errors.append("Password contains common weak patterns")
            break
    
    return len(errors) == 0, errors

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographical coordinates
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if latitude is None or longitude is None:
        return False
    
    # Valid latitude range: -90 to 90
    # Valid longitude range: -180 to 180
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def validate_file_upload(file_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate file upload data
    
    Args:
        file_data (dict): File upload data containing filename, size, type
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    filename = file_data.get('filename', '')
    file_size = file_data.get('size', 0)
    file_type = file_data.get('type', '')
    
    # Validate filename
    if not filename:
        errors.append("Filename is required")
    elif len(filename) > 255:
        errors.append("Filename is too long")
    elif not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        errors.append("Filename contains invalid characters")
    
    # Validate file type
    allowed_types = ['pdf', 'doc', 'docx', 'txt']
    file_extension = filename.split('.')[-1].lower() if '.' in filename else ''
    
    if file_extension not in allowed_types:
        errors.append(f"File type '{file_extension}' is not supported. Allowed types: {', '.join(allowed_types)}")
    
    # Validate file size (16MB max)
    max_size = 16 * 1024 * 1024  # 16MB in bytes
    if file_size > max_size:
        errors.append(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size (16MB)")
    
    if file_size <= 0:
        errors.append("File appears to be empty")
    
    return len(errors) == 0, errors

def validate_json_data(data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate JSON data against required fields
    
    Args:
        data (dict): Data to validate
        required_fields (list): List of required field names
        
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Data must be a valid JSON object")
        return False, errors
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            errors.append(f"Required field '{field}' is missing")
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            errors.append(f"Field '{field}' cannot be empty")
    
    return len(errors) == 0, errors

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text input by removing potentially harmful content
    
    Args:
        text (str): Text to sanitize
        max_length (int): Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script content
    text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove style content
    text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length].strip()
    
    return text

def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format
    
    Args:
        api_key (str): API key to validate
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not api_key:
        return False
    
    # Should be alphanumeric with some special characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', api_key):
        return False
    
    # Reasonable length range
    if not (10 <= len(api_key) <= 100):
        return False
    
    return True

def validate_session_data(session_data: Dict[str, Any]) -> bool:
    """
    Validate session data integrity
    
    Args:
        session_data (dict): Session data to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['user_id', 'created_at']
    
    for field in required_fields:
        if field not in session_data:
            return False
    
    # Validate user_id is a positive integer
    try:
        user_id = int(session_data['user_id'])
        if user_id <= 0:
            return False
    except (ValueError, TypeError):
        return False
    
    return True

class InputValidator:
    """Comprehensive input validator class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_user_registration(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate user registration data
        
        Args:
            data (dict): Registration data
            
        Returns:
            Tuple[bool, Dict[str, str]]: (is_valid, field_errors)
        """
        errors = {}
        
        # Validate name
        name = data.get('name', '').strip()
        if not validate_name(name):
            errors['name'] = 'Please enter a valid name (2-100 characters, letters only)'
        
        # Validate phone
        phone = data.get('phone', '').strip()
        if not validate_phone(phone):
            errors['phone'] = 'Please enter a valid Nigerian phone number'
        
        # Validate email (optional)
        email = data.get('email', '').strip()
        if email and not validate_email_address(email):
            errors['email'] = 'Please enter a valid email address'
        
        # Validate location
        location = data.get('location', '').strip()
        if not validate_location(location):
            errors['location'] = 'Please enter a valid location'
        
        # Validate language
        language = data.get('language', '').strip()
        if not validate_language_code(language):
            errors['language'] = 'Please select a supported language'
        
        # Validate farming interests (optional)
        farming_interests = data.get('farming_interests', [])
        if farming_interests:
            if not isinstance(farming_interests, list):
                errors['farming_interests'] = 'Farming interests must be a list'
            else:
                for crop in farming_interests:
                    if not validate_crop_name(crop):
                        errors['farming_interests'] = f'Invalid crop name: {crop}'
                        break
        
        # Validate farm size (optional)
        farm_size = data.get('farm_size')
        if farm_size is not None:
            try:
                farm_size = float(farm_size)
                if not validate_farm_size(farm_size):
                    errors['farm_size'] = 'Farm size must be between 0.01 and 10,000 hectares'
            except (ValueError, TypeError):
                errors['farm_size'] = 'Farm size must be a valid number'
        
        # Validate farming experience (optional)
        farming_experience = data.get('farming_experience')
        if farming_experience is not None:
            try:
                farming_experience = int(farming_experience)
                if not validate_farming_experience(farming_experience):
                    errors['farming_experience'] = 'Farming experience must be between 0 and 80 years'
            except (ValueError, TypeError):
                errors['farming_experience'] = 'Farming experience must be a valid number'
        
        return len(errors) == 0, errors
    
    def validate_chat_message(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, str]]:
        """
        Validate chat message data
        
        Args:
            data (dict): Chat message data
            
        Returns:
            Tuple[bool, Dict[str, str]]: (is_valid, field_errors)
        """
        errors = {}
        
        # Validate message
        message = data.get('message', '').strip()
        if not message:
            errors['message'] = 'Message cannot be empty'
        elif len(message) > 2000:
            errors['message'] = 'Message is too long (maximum 2000 characters)'
        
        # Validate language (optional)
        language = data.get('language', 'en')
        if not validate_language_code(language):
            errors['language'] = 'Invalid language code'
        
        # Sanitize message content
        if message:
            data['message'] = sanitize_input(message, 2000)
        
        return len(errors) == 0, errors