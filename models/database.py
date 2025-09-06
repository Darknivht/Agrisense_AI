"""
AgriSense AI - Database Models
Comprehensive data models for agricultural intelligence system
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey, text
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    """User model for farmers and agricultural professionals"""
    
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=True)
    location = Column(String(100), nullable=False)
    coordinates = Column(String(50), nullable=True)  # lat,lng format
    
    # User preferences
    preferred_language = Column(String(5), default='en')  # en, ha, yo, ig, ff
    preferred_ai_provider = Column(String(20), default='openai')  # openai, anthropic, openrouter, gemini
    preferred_ai_model = Column(String(50), nullable=True)  # Model ID for the selected provider
    farming_interests = Column(JSONB, default=list)  # crops, livestock, etc.
    farm_size = Column(Float, nullable=True)  # in hectares
    farming_experience = Column(Integer, nullable=True)  # years
    
    # Profile information
    profile_picture = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    conversations = relationship('Conversation', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    documents = relationship('Document', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    weather_subscriptions = relationship('WeatherSubscription', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    market_alerts = relationship('MarketAlert', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'location': self.location,
            'coordinates': self.coordinates,
            'preferred_language': self.preferred_language,
            'preferred_ai_provider': self.preferred_ai_provider,
            'preferred_ai_model': self.preferred_ai_model,
            'farming_interests': self.farming_interests or [],
            'farm_size': self.farm_size,
            'farming_experience': self.farming_experience,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_active': self.last_active.isoformat() if self.last_active else None
        }
    
    def update_activity(self):
        self.last_active = datetime.now(timezone.utc)
        db.session.commit()

class Conversation(db.Model):
    """Conversation history between users and AI"""
    
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    session_id = Column(String(36), nullable=True, index=True)
    
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    language = Column(String(5), nullable=False, default='en')
    
    confidence_score = Column(Float, nullable=True)
    processing_time = Column(Float, nullable=True)
    model_used = Column(String(50), nullable=True)
    
    rag_sources = Column(JSONB, nullable=True)
    weather_context = Column(JSONB, nullable=True)
    ai_metadata = Column(JSONB, nullable=True)
    
    user_rating = Column(Integer, nullable=True)
    user_feedback = Column(Text, nullable=True)
    
    platform = Column(String(20), default='web')
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f'<Conversation {self.id} for User {self.user_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'message': self.message,
            'response': self.response,
            'language': self.language,
            'confidence_score': self.confidence_score,
            'processing_time': self.processing_time,
            'model_used': self.model_used,
            'rag_sources': self.rag_sources,
            'weather_context': self.weather_context,
            'ai_metadata': self.ai_metadata,
            'user_rating': self.user_rating,
            'user_feedback': self.user_feedback,
            'platform': self.platform,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Document(db.Model):
    """Uploaded documents for RAG processing"""
    
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)
    
    status = Column(String(20), default='pending')
    processing_error = Column(Text, nullable=True)
    chunks_count = Column(Integer, nullable=True)
    
    agricultural_score = Column(Float, nullable=True)
    language_detected = Column(String(5), nullable=True)
    keywords = Column(JSONB, nullable=True)
    
    is_public = Column(Boolean, default=False)
    shared_with = Column(JSONB, nullable=True)
    
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Document {self.original_name} by User {self.user_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'status': self.status,
            'chunks_count': self.chunks_count,
            'agricultural_score': self.agricultural_score,
            'language_detected': self.language_detected,
            'keywords': self.keywords,
            'is_public': self.is_public,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }

class WeatherSubscription(db.Model):
    """Weather alert subscriptions for users"""
    
    __tablename__ = 'weather_subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    location = Column(String(100), nullable=False)
    coordinates = Column(String(50), nullable=True)
    alert_types = Column(JSONB, nullable=False)
    
    notify_whatsapp = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=False)
    
    alert_frequency = Column(String(20), default='daily')
    preferred_time = Column(String(5), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_alert_sent = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<WeatherSubscription for User {self.user_id} in {self.location}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'location': self.location,
            'coordinates': self.coordinates,
            'alert_types': self.alert_types or [],
            'notify_whatsapp': self.notify_whatsapp,
            'notify_sms': self.notify_sms,
            'notify_email': self.notify_email,
            'alert_frequency': self.alert_frequency,
            'preferred_time': self.preferred_time,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_alert_sent': self.last_alert_sent.isoformat() if self.last_alert_sent else None
        }

class MarketAlert(db.Model):
    """Market price alerts for specific crops"""
    
    __tablename__ = 'market_alerts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    crop_name = Column(String(50), nullable=False)
    market_location = Column(String(100), nullable=False)
    price_threshold = Column(Float, nullable=True)
    threshold_type = Column(String(10), default='above')
    
    notify_whatsapp = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_triggered = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f'<MarketAlert for {self.crop_name} by User {self.user_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'crop_name': self.crop_name,
            'market_location': self.market_location,
            'price_threshold': self.price_threshold,
            'threshold_type': self.threshold_type,
            'notify_whatsapp': self.notify_whatsapp,
            'notify_sms': self.notify_sms,
            'notify_email': self.notify_email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None
        }

class CropCalendar(db.Model):
    """Crop planting and harvesting calendar"""
    
    __tablename__ = 'crop_calendar'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    crop_name = Column(String(50), nullable=False)
    variety = Column(String(50), nullable=True)
    field_location = Column(String(100), nullable=False)
    field_size = Column(Float, nullable=True)
    
    planting_date = Column(DateTime, nullable=False)
    expected_harvest_date = Column(DateTime, nullable=False)
    actual_harvest_date = Column(DateTime, nullable=True)
    
    current_stage = Column(String(30), nullable=False, default='planted')
    stage_history = Column(JSONB, nullable=True)
    
    total_investment = Column(Float, nullable=True)
    expected_yield = Column(Float, nullable=True)
    actual_yield = Column(Float, nullable=True)
    
    notes = Column(Text, nullable=True)
    photos = Column(JSONB, nullable=True)
    
    status = Column(String(20), default='active')
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<CropCalendar {self.crop_name} by User {self.user_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'crop_name': self.crop_name,
            'variety': self.variety,
            'field_location': self.field_location,
            'field_size': self.field_size,
            'planting_date': self.planting_date.isoformat() if self.planting_date else None,
            'expected_harvest_date': self.expected_harvest_date.isoformat() if self.expected_harvest_date else None,
            'actual_harvest_date': self.actual_harvest_date.isoformat() if self.actual_harvest_date else None,
            'current_stage': self.current_stage,
            'stage_history': self.stage_history or [],
            'total_investment': self.total_investment,
            'expected_yield': self.expected_yield,
            'actual_yield': self.actual_yield,
            'notes': self.notes,
            'photos': self.photos or [],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemMetrics(db.Model):
    """System usage and performance metrics"""
    
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    
    metric_name = Column(String(50), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20), nullable=True)
    
    user_id = Column(Integer, nullable=True)
    session_id = Column(String(36), nullable=True)
    platform = Column(String(20), nullable=True)
    
    metric_metadata = Column(JSONB, nullable=True)
    
    recorded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    def __repr__(self):
        return f'<SystemMetrics {self.metric_name}: {self.metric_value}>'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'platform': self.platform,
            'metric_metadata': self.metric_metadata,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }

def init_db():
    """Initialize database tables"""
    db.create_all()
    
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);",
        "CREATE INDEX IF NOT EXISTS idx_users_location ON users(location);",
        "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);",
        "CREATE INDEX IF NOT EXISTS idx_weather_subscriptions_active ON weather_subscriptions(is_active);",
        "CREATE INDEX IF NOT EXISTS idx_market_alerts_active ON market_alerts(is_active);"
    ]
    
    with db.engine.connect() as conn:
        for stmt in index_statements:
            conn.execute(text(stmt))
        conn.commit()
    
    print("[SUCCESS] Database tables created successfully")

def seed_sample_data():
    """Seed database with sample data for development"""
    try:
        sample_users = [
            {
                'name': 'Malam Ibrahim',
                'phone': '+2348012345678',
                'email': 'ibrahim@example.com',
                'location': 'Kano, Nigeria',
                'preferred_language': 'ha',
                'farming_interests': ['rice', 'maize', 'tomato'],
                'farm_size': 5.5,
                'farming_experience': 15
            },
            {
                'name': 'Mrs. Aisha Mohammed',
                'phone': '+2348098765432',
                'email': 'aisha@example.com',
                'location': 'Kaduna, Nigeria',
                'preferred_language': 'ha',
                'farming_interests': ['cassava', 'yam', 'pepper'],
                'farm_size': 3.2,
                'farming_experience': 8
            },
            {
                'name': 'Mr. John Okafor',
                'phone': '+2348187654321',
                'email': 'john@example.com',
                'location': 'Enugu, Nigeria',
                'preferred_language': 'ig',
                'farming_interests': ['cassava', 'cocoyam', 'plantain'],
                'farm_size': 2.8,
                'farming_experience': 12
            }
        ]
        
        for user_data in sample_users:
            existing_user = User.query.filter_by(phone=user_data['phone']).first()
            if not existing_user:
                user = User(**user_data)
                db.session.add(user)
        
        db.session.commit()
        print("✅ Sample data seeded successfully")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding sample data: {str(e)}")

def cleanup_old_data(days: int = 90):
    """Clean up old conversation data"""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        old_conversations = Conversation.query.filter(Conversation.created_at < cutoff_date).delete()
        old_metrics = SystemMetrics.query.filter(SystemMetrics.recorded_at < cutoff_date).delete()
        
        db.session.commit()
        print(f"✅ Cleaned up {old_conversations} old conversations and {old_metrics} old metrics")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error cleaning up old data: {str(e)}")
