"""
AgriSense AI - Configuration Management
Smart Agricultural Intelligence System
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'agrisense-ai-2024-secure-key')
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///agrisense.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    AFRICA_TALKING_API_KEY = os.getenv('AT_API_KEY')
    AFRICA_TALKING_USERNAME = os.getenv('AT_USERNAME', 'sandbox')
    OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    
    # WhatsApp Business API
    WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
    WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    WHATSAPP_WEBHOOK_VERIFY_TOKEN = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
    
    # Instagram API
    INSTAGRAM_ACCESS_TOKEN = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    INSTAGRAM_PAGE_ID = os.getenv('INSTAGRAM_PAGE_ID')
    
    # RAG Configuration
    VECTORDB_PATH = os.getenv('VECTORDB_PATH', './data/vectordb')
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # AI Configuration
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-4-turbo')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-large')
    
    # Multi-language Support
    SUPPORTED_LANGUAGES = ['en', 'ha', 'yo', 'ig', 'ff']  # English, Hausa, Yoruba, Igbo, Fulfulde
    DEFAULT_LANGUAGE = 'en'
    
    # Feature Flags
    ENABLE_RAG = os.getenv('ENABLE_RAG', 'True').lower() == 'true'
    ENABLE_VOICE = os.getenv('ENABLE_VOICE', 'True').lower() == 'true'
    ENABLE_SMS = os.getenv('ENABLE_SMS', 'True').lower() == 'true'
    ENABLE_WHATSAPP = os.getenv('ENABLE_WHATSAPP', 'True').lower() == 'true'
    ENABLE_INSTAGRAM = os.getenv('ENABLE_INSTAGRAM', 'False').lower() == 'true'
    ENABLE_WEATHER = os.getenv('ENABLE_WEATHER', 'True').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Enhanced security for production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}