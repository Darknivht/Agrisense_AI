#!/usr/bin/env python3
"""
Create a test user for testing AI provider switching
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from flask import Flask
from models.database import db, User
from flask_jwt_extended import create_access_token, JWTManager
from dotenv import load_dotenv

load_dotenv()

def create_test_user():
    """Create a test user for API testing"""
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///agrisense.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-jwt-secret')
    
    db.init_app(app)
    jwt = JWTManager(app)
    
    with app.app_context():
        try:
            # Check if test user already exists
            existing_user = User.query.filter_by(phone='+234901111111').first()
            if existing_user:
                print("✅ Test user already exists")
                user = existing_user
            else:
                # Create test user
                user = User(
                    name="Test AI User",
                    phone="+234901111111",
                    location="Lagos, Nigeria",
                    preferred_language="en",
                    preferred_ai_provider="openai",  # Set default
                    farming_interests=["rice", "maize"],
                    farm_size=5.0,
                    farming_experience=3,
                    created_at=datetime.utcnow(),
                    last_active=datetime.utcnow()
                )
                
                db.session.add(user)
                db.session.commit()
                print("✅ Test user created successfully")
            
            # Generate JWT token
            access_token = create_access_token(identity=user.id)
            
            print(f"📱 User ID: {user.id}")
            print(f"🔑 JWT Token: {access_token}")
            print(f"🌾 Current AI Provider: {getattr(user, 'preferred_ai_provider', 'openai')}")
            
            # Save token to file for easy access
            with open('test_token.txt', 'w') as f:
                f.write(access_token)
            
            print("💾 Token saved to test_token.txt")
            
            return access_token, user.id
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            import traceback
            traceback.print_exc()
            return None, None

if __name__ == "__main__":
    create_test_user()