#!/usr/bin/env python3
"""
Add preferred_ai_provider column to users table
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    """Add preferred_ai_provider column to users table"""
    
    # Parse DATABASE_URL
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment")
        return
    
    print(f"🔌 Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='preferred_ai_provider';
        """)
        
        if cursor.fetchone():
            print("✅ Column 'preferred_ai_provider' already exists")
            conn.close()
            return
        
        # Add the column
        print("➕ Adding 'preferred_ai_provider' column...")
        cursor.execute("""
            ALTER TABLE users 
            ADD COLUMN preferred_ai_provider VARCHAR(20) DEFAULT 'openai';
        """)
        
        # Commit the changes
        conn.commit()
        print("✅ Column added successfully")
        
        # Verify the column was added
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' AND column_name='preferred_ai_provider';
        """)
        
        if cursor.fetchone():
            print("✅ Column verified in database")
        else:
            print("❌ Column verification failed")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database migration error: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_database()