#!/usr/bin/env python3
"""
AgriSense AI - Quick Start Script
Development server launcher with environment setup
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check Python version compatibility"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        logger.error("Python 3.11+ is required. Current version: {}.{}.{}".format(
            version.major, version.minor, version.micro
        ))
        return False
    
    logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_environment():
    """Check if .env file exists"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        if env_example.exists():
            logger.warning("⚠️  .env file not found. Please copy .env.example to .env and configure your API keys")
            logger.info("Run: cp .env.example .env")
        else:
            logger.error("❌ Neither .env nor .env.example found")
        return False
    
    logger.info("✅ Environment file found")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import openai
        import requests
        logger.info("✅ Core dependencies found")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependencies: {e}")
        logger.info("Run: pip install -r requirements.txt")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        logger.info("📦 Installing dependencies...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to install dependencies")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'uploads',
        'data',
        'data/vectordb',
        'logs',
        'static/uploads'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ Directories created")

def run_development_server():
    """Run the development server"""
    try:
        logger.info("🚀 Starting AgriSense AI development server...")
        logger.info("📱 Open http://localhost:5000 in your browser")
        logger.info("🔧 Press Ctrl+C to stop the server")
        
        # Set environment variables
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = 'True'
        
        from app import create_app
        app = create_app('development')
        
        with app.app_context():
            from models.database import init_db
            init_db()
        
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("Make sure all dependencies are installed")
        return False
    except Exception as e:
        logger.error(f"❌ Server error: {e}")
        return False

def main():
    """Main function"""
    print("""
    🌾 AgriSense AI - Smart Agricultural Intelligence System
    =====================================================
    Starting development environment setup...
    """)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        logger.info("Installing missing dependencies...")
        if not install_dependencies():
            sys.exit(1)
    
    # Check environment
    if not check_environment():
        print("""
        ⚠️  Environment Setup Required:
        
        1. Copy the example environment file:
           cp .env.example .env
        
        2. Edit .env file and add your API keys:
           - OpenAI API key (for AI features)
           - OpenWeatherMap API key (for weather data)
           - Africa's Talking API key (for SMS, optional)
           - WhatsApp Business API token (optional)
        
        3. For basic testing, you can run without API keys,
           but some features will be limited.
        """)
        
        response = input("Continue without full configuration? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Run server
    try:
        run_development_server()
    except KeyboardInterrupt:
        logger.info("\n👋 AgriSense AI server stopped. Thank you for using our platform!")
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()