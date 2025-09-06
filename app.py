"""
AgriSense AI - Smart Agricultural Intelligence System
Main Application Entry Point
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler

from config import config
from core.ai_engine import AgriSenseAI
from core.rag_system import RAGSystem
from core.weather_service import WeatherService
from integrations.whatsapp_integration import WhatsAppIntegration
from integrations.instagram_integration import InstagramIntegration
from integrations.sms_integration import SMSIntegration
from models.database import init_db, db, User, Conversation, Document
from utils.language_detector import LanguageDetector
from utils.validators import validate_phone, validate_location

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    CORS(app)
    
    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    # Initialize core services
    ai_engine = AgriSenseAI()
    rag_system = RAGSystem(app.config['VECTORDB_PATH']) if app.config['ENABLE_RAG'] else None
    weather_service = WeatherService(app.config['OPENWEATHER_API_KEY']) if app.config['ENABLE_WEATHER'] else None
    language_detector = LanguageDetector()
    
    # Initialize integrations
    whatsapp = WhatsAppIntegration(app.config['WHATSAPP_ACCESS_TOKEN']) if app.config['ENABLE_WHATSAPP'] else None
    instagram = InstagramIntegration(app.config['INSTAGRAM_ACCESS_TOKEN']) if app.config['ENABLE_INSTAGRAM'] else None
    sms = SMSIntegration(app.config['AFRICA_TALKING_API_KEY']) if app.config['ENABLE_SMS'] else None
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/agrisense.log', maxBytes=10240000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('AgriSense AI startup')
    
    # Helper function for web authentication
    def get_user_from_token():
        """Get user from token in request headers or return None"""
        try:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                from flask_jwt_extended import decode_token
                decoded_token = decode_token(token)
                user_id = decoded_token['sub']
                return User.query.get(user_id)
        except:
            pass
        return None

    # Validation functions
    def validate_phone(phone):
        """Basic phone number validation"""
        if not phone:
            return False
        # Remove common prefixes and spaces
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        # Check if it's numeric and reasonable length
        return phone.isdigit() and 10 <= len(phone) <= 15

    def validate_location(location):
        """Basic location validation"""
        return location and len(location.strip()) >= 3

    # Routes
    @app.route('/')
    def index():
        """Landing page - redirect to dashboard if authenticated"""
        # Check if user has token in localStorage (handled by frontend)
        return render_template('landing.html')
    
    @app.route('/dashboard')
    def dashboard():
        """User dashboard - handles authentication via JavaScript"""
        return render_template('dashboard.html')
    
    @app.route('/login')
    def login_page():
        """Login page"""
        return render_template('login.html')
    
    @app.route('/register')
    def register_page():
        """Registration page"""
        return render_template('register.html')
    
    @app.route('/chat')
    def chat_page():
        """Chat interface - handles authentication via JavaScript"""
        return render_template('chat.html')
    
    @app.route('/settings')
    def settings_page():
        """Settings page - handles authentication via JavaScript"""
        return render_template('settings.html')
    
    @app.route('/api/verify-token', methods=['POST'])
    def verify_token():
        """Verify JWT token and return user data"""
        try:
            data = request.get_json()
            token = data.get('token')
            
            if not token:
                return jsonify({'error': 'Token required'}), 400
            
            from flask_jwt_extended import decode_token
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'valid': True,
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401

    @app.route('/api/user/stats', methods=['GET'])
    @jwt_required()
    def get_user_stats():
        """Get user statistics for dashboard"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Count conversations (safe)
            conversations_count = 0
            try:
                conversations_count = Conversation.query.filter_by(user_id=user_id).count()
            except:
                pass
            
            # Count documents (safe)
            documents_count = 0
            try:
                if hasattr(user, 'documents') and user.documents:
                    documents_count = len(user.documents)
            except:
                pass
            
            # Count active weather subscriptions (safe)
            active_alerts = 0
            try:
                if hasattr(user, 'weather_subscriptions') and user.weather_subscriptions:
                    active_alerts = user.weather_subscriptions.filter_by(is_active=True).count()
            except:
                pass
            
            return jsonify({
                'conversations': conversations_count,
                'documents': documents_count,
                'active_alerts': active_alerts
            }), 200
            
        except Exception as e:
            app.logger.error(f"Stats error: {str(e)}")
            # Return default stats instead of error
            return jsonify({
                'conversations': 0,
                'documents': 0,
                'active_alerts': 0
            }), 200
    
    @app.route('/api/register', methods=['POST'])
    @limiter.limit("5 per minute")
    def register():
        """User registration"""
        try:
            data = request.get_json()
            
            # Validate input
            if not validate_phone(data.get('phone')):
                return jsonify({'error': 'Invalid phone number format'}), 400
            
            if not validate_location(data.get('location')):
                return jsonify({'error': 'Invalid location'}), 400
            
            # Check if user exists
            existing_user = User.query.filter_by(phone=data['phone']).first()
            if existing_user:
                return jsonify({'error': 'User already exists'}), 409
            
            # Create new user
            user = User(
                name=data['name'],
                phone=data['phone'],
                location=data['location'],
                preferred_language=data.get('language', 'en'),
                farming_interests=data.get('farming_interests', [])
            )
            db.session.add(user)
            db.session.commit()
            
            # Generate JWT token
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
            
            return jsonify({
                'message': 'Registration successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 201
            
        except Exception as e:
            app.logger.error(f"Registration error: {str(e)}")
            return jsonify({'error': 'Registration failed'}), 500
    
    @app.route('/api/login', methods=['POST'])
    @limiter.limit("10 per minute")
    def login():
        """User authentication"""
        try:
            data = request.get_json()
            phone = data.get('phone')
            
            user = User.query.filter_by(phone=phone).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Update last login
            user.last_active = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(identity=user.id, expires_delta=timedelta(days=30))
            
            return jsonify({
                'message': 'Login successful',
                'access_token': access_token,
                'user': user.to_dict()
            }), 200
            
        except Exception as e:
            app.logger.error(f"Login error: {str(e)}")
            return jsonify({'error': 'Login failed'}), 500
    
    @app.route('/api/chat', methods=['POST'])
    @jwt_required()
    @limiter.limit("30 per minute")
    def chat():
        """AI chat interface with RAG"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            data = request.get_json()
            message = data.get('message', '').strip()
            
            if not message:
                return jsonify({'error': 'Message cannot be empty'}), 400
            
            # Detect language
            detected_lang = language_detector.detect(message)
            
            # Get conversation context
            recent_conversations = Conversation.query.filter_by(user_id=user_id)\
                .order_by(Conversation.created_at.desc()).limit(10).all()
            context = [conv.to_dict() for conv in recent_conversations]
            
            # Get RAG context if enabled
            rag_context = None
            if rag_system and app.config['ENABLE_RAG']:
                rag_context = rag_system.search(message, k=5)
            
            # Get weather context if relevant
            weather_context = None
            if weather_service and any(word in message.lower() for word in ['weather', 'rain', 'temperature', 'yanayi']):
                weather_context = weather_service.get_weather(user.location)
            
            # Generate AI response
            response = ai_engine.generate_response(
                message=message,
                user_context=user.to_dict(),
                conversation_context=context,
                rag_context=rag_context,
                weather_context=weather_context,
                language=detected_lang,
                ai_provider=user.preferred_ai_provider,
                ai_model=user.preferred_ai_model
            )
            
            # Save conversation
            conversation = Conversation(
                user_id=user_id,
                message=message,
                response=response['text'],
                language=detected_lang,
                ai_metadata={
                    'rag_sources': rag_context[:3] if rag_context else None,
                    'weather_data': weather_context,
                    'confidence': response.get('confidence', 0.8)
                }
            )
            db.session.add(conversation)
            
            # Update user activity
            user.last_active = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'response': response['text'],
                'language': detected_lang,
                'ai_provider': response.get('ai_provider', 'unknown'),
                'sources': rag_context[:3] if rag_context else None,
                'weather': weather_context,
                'suggestions': response.get('suggestions', [])
            }), 200
            
        except Exception as e:
            app.logger.error(f"Chat error: {str(e)}")
            return jsonify({'error': 'Failed to process message'}), 500
    
    @app.route('/api/upload-document', methods=['POST'])
    @jwt_required()
    @limiter.limit("10 per hour")
    def upload_document():
        """Upload PDF documents for RAG processing"""
        try:
            if not rag_system:
                return jsonify({'error': 'Document upload not enabled'}), 400
            
            user_id = get_jwt_identity()
            
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400
            
            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400
            
            if not file.filename.lower().endswith('.pdf'):
                return jsonify({'error': 'Only PDF files are supported'}), 400
            
            # Save and process document
            filename = rag_system.process_document(file, user_id)
            
            # Save document record
            document = Document(
                user_id=user_id,
                filename=filename,
                original_name=file.filename,
                file_type='pdf'
            )
            db.session.add(document)
            db.session.commit()
            
            return jsonify({
                'message': 'Document uploaded and processed successfully',
                'document_id': document.id,
                'filename': filename
            }), 200
            
        except Exception as e:
            app.logger.error(f"Document upload error: {str(e)}")
            return jsonify({'error': 'Failed to upload document'}), 500
    
    @app.route('/api/weather/<location>')
    @jwt_required()
    def get_weather(location):
        """Get weather information"""
        try:
            if not weather_service:
                return jsonify({'error': 'Weather service not available'}), 400
            
            weather_data = weather_service.get_weather(location)
            return jsonify(weather_data), 200
            
        except Exception as e:
            app.logger.error(f"Weather error: {str(e)}")
            return jsonify({'error': 'Failed to fetch weather data'}), 500
    
    @app.route('/webhook/whatsapp', methods=['GET', 'POST'])
    def whatsapp_webhook():
        """WhatsApp webhook handler"""
        try:
            if not whatsapp:
                return jsonify({'error': 'WhatsApp integration not enabled'}), 400
            
            if request.method == 'GET':
                # Webhook verification
                return whatsapp.verify_webhook(request)
            
            # Handle incoming messages
            return whatsapp.handle_message(request.get_json())
            
        except Exception as e:
            app.logger.error(f"WhatsApp webhook error: {str(e)}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    @app.route('/webhook/instagram', methods=['POST'])
    def instagram_webhook():
        """Instagram webhook handler"""
        try:
            if not instagram:
                return jsonify({'error': 'Instagram integration not enabled'}), 400
            
            return instagram.handle_message(request.get_json())
            
        except Exception as e:
            app.logger.error(f"Instagram webhook error: {str(e)}")
            return jsonify({'error': 'Webhook processing failed'}), 500
    
    @app.route('/api/ai/providers', methods=['GET'])
    @jwt_required()
    def get_ai_providers():
        """Get available AI providers"""
        try:
            providers = ai_engine.get_available_providers()
            return jsonify({
                'providers': providers,
                'current': os.getenv('DEFAULT_AI_PROVIDER', 'openai')
            }), 200
        except Exception as e:
            app.logger.error(f"AI providers error: {str(e)}")
            return jsonify({'error': 'Failed to get AI providers'}), 500
    
    @app.route('/api/user/ai-provider', methods=['PUT'])
    @jwt_required()
    def update_user_ai_provider():
        """Update user's preferred AI provider and model"""
        try:
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            data = request.get_json()
            provider = data.get('provider')
            model = data.get('model')  # Optional model selection
            
            if not provider:
                return jsonify({'error': 'Provider not specified'}), 400
            
            # Validate provider
            available_providers = ai_engine.get_available_providers()
            valid_providers = [p['id'] for p in available_providers]
            
            if provider not in valid_providers:
                return jsonify({'error': 'Invalid AI provider'}), 400
            
            # Validate model if provided
            if model:
                provider_data = next((p for p in available_providers if p['id'] == provider), None)
                if provider_data:
                    valid_models = [m['id'] for m in provider_data.get('models', [])]
                    if model not in valid_models:
                        return jsonify({'error': 'Invalid model for selected provider'}), 400
                    user.preferred_ai_model = model
                else:
                    # If no model specified, use default
                    user.preferred_ai_model = provider_data.get('default_model') if provider_data else None
            
            # Update user preferences
            user.preferred_ai_provider = provider
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'AI provider updated successfully',
                'provider': provider,
                'model': user.preferred_ai_model
            }), 200
            
        except Exception as e:
            app.logger.error(f"Update AI provider error: {str(e)}")
            return jsonify({'error': 'Failed to update AI provider'}), 500
    
    @app.route('/api/health')
    def health_check():
        """System health check"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': {
                'database': db.engine.dialect.name,
                'rag_system': rag_system is not None,
                'weather_service': weather_service is not None,
                'whatsapp': whatsapp is not None,
                'instagram': instagram is not None,
                'sms': sms is not None
            }
        }), 200
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500
    
    return app

def main():
    """Main entry point"""
    app = create_app(os.getenv('FLASK_CONFIG', 'default'))
    
    with app.app_context():
        init_db()
    
    # Start the application
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '127.0.0.1')
    
    print(f"""
    [AgriSense AI] Smart Agricultural Intelligence System
    [SERVER] Starting at http://{host}:{port}
    [FEATURES] AI Chat, RAG System, Multi-platform Integration
    [LANGUAGES] English, Hausa, Yoruba, Igbo, Fulfulde
    """)
    
    app.run(host=host, port=port, debug=app.config.get('DEBUG', False))

# WSGI entry point for production deployment
app = create_app(os.getenv('FLASK_CONFIG', 'production'))

if __name__ == '__main__':
    main()