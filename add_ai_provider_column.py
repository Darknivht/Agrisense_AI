#!/usr/bin/env python3
"""
Add AI provider column to user table
"""
import os
from flask import Flask
from models.database import db, User
from sqlalchemy import text

def add_ai_provider_column():
    """Add preferred_ai_provider column to users table"""
    
    # Create a minimal Flask app for database operations
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///agrisense.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        try:
            # Check if column already exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'preferred_ai_provider' in columns:
                print("✅ Column 'preferred_ai_provider' already exists")
                return
            
            # Add the column
            print("➕ Adding 'preferred_ai_provider' column...")
            db.engine.execute(text("ALTER TABLE users ADD COLUMN preferred_ai_provider VARCHAR(20) DEFAULT 'openai'"))
            
            print("✅ Column added successfully")
            
        except Exception as e:
            print(f"❌ Error adding column: {e}")

if __name__ == "__main__":
    add_ai_provider_column()