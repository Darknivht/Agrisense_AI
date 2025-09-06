# 🌾 AgriSense AI - Smart Agricultural Intelligence System

> **Revolutionizing Agriculture with AI-Powered Multi-Platform Intelligence**

AgriSense AI is a comprehensive, scalable agricultural intelligence platform that combines cutting-edge AI technology with multi-platform accessibility to empower farmers worldwide. Our system provides real-time insights, weather intelligence, market analysis, and personalized recommendations through a beautiful, modern interface and multiple communication channels.

![AgriSense AI Dashboard](https://via.placeholder.com/800x400/4CAF50/FFFFFF?text=AgriSense+AI+Dashboard)

## 🌟 Key Features

### 🧠 Advanced AI Engine
- **Multi-Model AI Integration**: OpenAI GPT-4 + Anthropic Claude for superior responses
- **RAG (Retrieval Augmented Generation)**: Upload agricultural PDFs for instant insights
- **Document Intelligence**: Vector database-powered knowledge extraction
- **5-Language Support**: English, Hausa, Yoruba, Igbo, Fulfulde
- **Intelligent Language Detection**: Automatic language identification

### 🌐 Multi-Platform Integration
- **WhatsApp Business API**: Direct messaging with farmers
- **Telegram Bot**: Advanced bot with inline keyboards and commands
- **Discord Bot**: Community server management with roles and channels
- **Instagram Messaging**: Reach younger farmers on social media
- **SMS Integration**: Africa's Talking API for SMS alerts
- **Email Newsletters**: Rich HTML email templates for updates
- **Modern Web App**: Responsive PWA with glassmorphism design

### 📚 Document Intelligence (RAG System)
- **PDF Upload & Analysis**: Extract insights from agricultural documents
- **Vector Database**: ChromaDB for semantic search capabilities
- **Smart Summarization**: AI-powered document summarization
- **Context-Aware Q&A**: Ask specific questions about uploaded documents
- **Multi-Format Support**: PDF, DOCX, images with OCR

### 🌤️ Weather Intelligence
- **Real-Time Weather Data**: OpenWeatherMap integration
- **5-Day Forecasts**: Detailed agricultural weather predictions
- **Smart Alerts**: Location-based weather notifications
- **Irrigation Recommendations**: AI-powered watering advice
- **Seasonal Planning**: Long-term weather trend analysis

### 💰 Market Intelligence
- **Real-Time Crop Prices**: Live market data integration
- **Price Trend Analysis**: Historical and predictive analytics
- **Best Selling Times**: AI-optimized selling recommendations
- **Market Alerts**: Price threshold notifications
- **Regional Price Variations**: Location-specific market data

### 🎨 Modern Animated Frontend
- **Glass Morphism Design**: Beautiful, modern UI with animated glass effects
- **Particle Backgrounds**: Dynamic animated particle systems
- **Smooth Animations**: CSS animations with slide-ups, fades, and transforms
- **Liquid Buttons**: Interactive button animations with ripple effects
- **3D Effects**: Card hover effects and floating elements
- **Cyber Themes**: Multiple animated background themes
- **Mobile-First Responsive**: Optimized for all devices with touch animations
- **Progressive Web App**: Install-able web application
- **Real-Time Chat**: WebSocket-powered live conversations
- **Dark/Light Themes**: User preference support
- **Accessibility**: WCAG 2.1 compliant interface

## 🏗️ System Architecture

```
AgriSense AI System Architecture

┌─────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
├─────────────────────────────────────────────────────────────┤
│  Web App (React/Vue) │ Mobile PWA │ Admin Dashboard         │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   API Gateway                               │
├─────────────────────────────────────────────────────────────┤
│  Flask REST API │ WebSocket │ Webhook Handlers              │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic                             │
├─────────────────────────────────────────────────────────────┤
│ AI Service │ Weather Service │ Market Service │ Auth Service │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│               Platform Integrations                         │
├─────────────────────────────────────────────────────────────┤
│ WhatsApp │ Telegram │ Discord │ Instagram │ SMS │ Email      │
└─────────────────────────────────────────────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│ PostgreSQL │ Redis Cache │ Vector DB │ File Storage          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 13+
- Redis Server
- Node.js 16+ (for frontend development)

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/agrisense-ai.git
cd agrisense-ai
```

2. **Set Up Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys and configuration
nano .env
```

3. **Install Dependencies**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

4. **Database Setup**
```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. **Quick Start (Development)**
```bash
# Run the quick start script
python run.py
```

Or manually:
```bash
# Start the Flask application
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

6. **Access the Application**
- Web App: http://localhost:5000
- Admin Dashboard: http://localhost:5000/admin
- API Documentation: http://localhost:5000/api/docs

## 🚀 Production Deployment

### Deploy to Render (Recommended)

AgriSense AI is ready for production deployment on Render with zero Docker configuration.

1. **Push to GitHub**
```bash
git add .
git commit -m "Deploy AgriSense AI"
git push origin main
```

2. **Deploy to Render**
- Connect your GitHub repository to [Render](https://render.com)
- Render will automatically use the included `render.yaml` configuration
- Add your environment variables in Render dashboard
- Your app will be live with automatic HTTPS and scaling

3. **One-Click Deploy** [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Features Ready for Production
✅ **Glass morphism UI** with beautiful animations  
✅ **Multi-AI provider** support with fallbacks  
✅ **PostgreSQL** database with migrations  
✅ **Redis** caching for performance  
✅ **Gunicorn** WSGI server configuration  
✅ **Environment-based** configuration  
✅ **Security** with JWT and rate limiting  
✅ **Monitoring** with logging and error tracking  

## 🛠️ Configuration

### Environment Variables

```bash
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://username:password@localhost:5432/agrisense_ai

# AI Services
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key

# Weather Service
OPENWEATHER_API_KEY=your-openweathermap-api-key

# Communication Platforms
WHATSAPP_ACCESS_TOKEN=your-whatsapp-token
WHATSAPP_PHONE_NUMBER_ID=your-phone-number-id
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DISCORD_BOT_TOKEN=your-discord-bot-token
AT_API_KEY=your-africas-talking-api-key

# Email Service
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-email-password

# Feature Flags
ENABLE_RAG=True
ENABLE_VOICE=True
ENABLE_SMS=True
ENABLE_WHATSAPP=True
ENABLE_TELEGRAM=True
ENABLE_DISCORD=True
ENABLE_WEATHER=True
```

### Platform Setup

#### WhatsApp Business API
1. Sign up for WhatsApp Business API
2. Get your access token and phone number ID
3. Set up webhook URL: `https://yourdomain.com/webhook/whatsapp`

#### Telegram Bot
1. Message @BotFather on Telegram
2. Create a new bot: `/newbot`
3. Get your bot token
4. Set webhook: `https://yourdomain.com/webhook/telegram`

#### Discord Bot
1. Go to Discord Developer Portal
2. Create new application and bot
3. Get bot token
4. Invite bot to your server with appropriate permissions

## 📱 Platform Features

### WhatsApp Integration
- **Business API Integration**: Professional messaging
- **Rich Media Support**: Images, documents, voice messages
- **Template Messages**: Pre-approved message templates
- **Broadcast Lists**: Send updates to subscriber lists
- **Interactive Buttons**: Quick action buttons
- **Status Updates**: Delivery and read receipts

### Telegram Bot
- **Advanced Commands**: Comprehensive command system
- **Inline Keyboards**: Interactive button menus
- **File Uploads**: PDF document analysis
- **Multi-language Support**: Language selection interface
- **Group Chat Support**: Community discussions
- **Bot Analytics**: Usage statistics and metrics

### Discord Bot
- **Server Management**: Auto-setup farming communities
- **Role Assignment**: Farmer role selection system
- **Channel Creation**: Specialized farming channels
- **Slash Commands**: Modern Discord command interface
- **Embed Messages**: Rich formatted responses
- **Community Features**: Farming discussion channels

### Instagram Integration
- **Direct Messaging**: Personal farmer consultations
- **Story Responses**: Automated story reply handling
- **Business Account**: Professional presence
- **Media Analysis**: Image-based pest identification

## 🤖 AI Capabilities

### Natural Language Processing
- **Multi-Language Understanding**: 5 Nigerian languages + English
- **Context Awareness**: Remembers conversation history
- **Intent Recognition**: Understands farmer questions
- **Sentiment Analysis**: Detects farmer emotions and urgency

### RAG (Retrieval Augmented Generation)
- **Document Upload**: PDF, DOCX, images with OCR
- **Vector Search**: Semantic similarity matching
- **Context Injection**: Relevant information retrieval
- **Source Attribution**: References to original documents
- **Multi-Document Synthesis**: Combine information from multiple sources

### Specialized Agricultural AI
- **Crop Identification**: Image-based crop recognition
- **Pest Detection**: Disease and pest identification from photos
- **Weather Correlation**: Connect weather data with farming advice
- **Market Prediction**: Price trend analysis and forecasting
- **Personalized Recommendations**: Based on location and crop type

## 📊 Dashboard Features

### Farmer Dashboard
- **Personal Profile**: Farming interests and location
- **Conversation History**: All AI interactions
- **Document Library**: Uploaded PDFs and analysis results
- **Weather Alerts**: Customized weather notifications
- **Market Watchlist**: Tracked crop prices
- **Analytics**: Personal farming insights

### Admin Dashboard
- **User Management**: Farmer profiles and permissions
- **Platform Analytics**: Usage across all platforms
- **Content Management**: FAQ, tips, and guides
- **Alert System**: Broadcast weather and market alerts
- **Document Management**: Approve and categorize documents
- **AI Training**: Fine-tune responses and add knowledge

## 🌍 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t agrisense-ai .
docker run -p 5000:5000 agrisense-ai
```

### Production Deployment (Ubuntu)
```bash
# Install system dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql redis-server nginx

# Set up application
git clone https://github.com/yourusername/agrisense-ai.git
cd agrisense-ai
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure database
sudo -u postgres createdb agrisense_ai
flask db upgrade

# Set up systemd service
sudo cp agrisense.service /etc/systemd/system/
sudo systemctl enable agrisense
sudo systemctl start agrisense

# Configure Nginx
sudo cp nginx.conf /etc/nginx/sites-available/agrisense
sudo ln -s /etc/nginx/sites-available/agrisense /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Cloud Deployment
- **AWS**: Elastic Beanstalk or ECS
- **Google Cloud**: Cloud Run or Compute Engine
- **Azure**: App Service or Container Instances
- **Heroku**: Direct deployment with Procfile
- **DigitalOcean**: App Platform or Droplets

## 📈 Monitoring & Analytics

### Application Monitoring
- **Health Checks**: Automated system health monitoring
- **Performance Metrics**: Response times and throughput
- **Error Tracking**: Sentry integration for error monitoring
- **Uptime Monitoring**: 24/7 availability tracking

### Business Analytics
- **User Engagement**: Platform usage statistics
- **AI Interaction Analytics**: Conversation patterns and topics
- **Geographic Distribution**: Farmer locations and regional usage
- **Feature Adoption**: Most used features and platforms
- **Market Trends**: Popular crops and farming questions

### Logs and Debugging
- **Structured Logging**: JSON-formatted application logs
- **Log Aggregation**: Centralized log collection
- **Real-time Monitoring**: Live system monitoring dashboards
- **Alert System**: Automated issue notifications

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/

# Run with coverage
pytest --cov=app --cov-report=html
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **E2E Tests**: Full workflow testing
- **Platform Tests**: Messaging platform integrations
- **AI Tests**: Model response quality testing

## 🔒 Security

### Security Features
- **JWT Authentication**: Secure user authentication
- **API Rate Limiting**: Prevent abuse and spam
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Prevention**: Content sanitization
- **HTTPS Enforcement**: Secure communication
- **CORS Configuration**: Cross-origin request security

### Privacy & Compliance
- **Data Encryption**: At rest and in transit
- **GDPR Compliance**: User data protection
- **User Consent**: Explicit permission for data usage
- **Data Retention**: Configurable data retention policies
- **Audit Logs**: Complete action tracking

## 🤝 Contributing

We welcome contributions from the agricultural technology community!

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/agrisense-ai.git
cd agrisense-ai

# Create feature branch
git checkout -b feature/your-feature-name

# Set up development environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run pre-commit hooks
pre-commit install
```

### Contribution Guidelines
1. **Code Quality**: Follow PEP 8 and use Black formatter
2. **Testing**: Add tests for new features
3. **Documentation**: Update documentation for changes
4. **Commit Messages**: Use conventional commit format
5. **Pull Requests**: Provide detailed PR descriptions

### Areas for Contribution
- **Language Support**: Add new African languages
- **Platform Integration**: New messaging platforms
- **AI Models**: Improve agricultural AI capabilities
- **Mobile Apps**: Native mobile applications
- **Data Sources**: Additional weather and market APIs
- **UI/UX**: Frontend improvements and accessibility

## 📚 API Documentation

### Authentication
```bash
# Get access token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Use token in requests
curl -X GET http://localhost:5000/api/user/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Key Endpoints

#### User Management
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update profile

#### AI Chat
- `POST /api/chat` - Send message to AI
- `GET /api/chat/history` - Get conversation history
- `POST /api/chat/voice` - Voice message processing

#### Document Management
- `POST /api/documents/upload` - Upload document
- `GET /api/documents` - List user documents
- `POST /api/documents/query` - Query document content

#### Weather & Market
- `GET /api/weather/{location}` - Get weather data
- `GET /api/market/prices` - Get market prices
- `POST /api/alerts/subscribe` - Subscribe to alerts

## 📞 Support

### Community Support
- **Discord Server**: Join our farming community
- **Telegram Group**: @AgriSenseSupport
- **GitHub Issues**: Bug reports and feature requests

### Professional Support
- **Email**: support@agrisense.ai
- **Documentation**: https://docs.agrisense.ai
- **Status Page**: https://status.agrisense.ai

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- **Farmers**: The heart of our agricultural communities
- **Open Source Community**: For the amazing tools and libraries
- **AI Research Community**: For advancing agricultural AI
- **African Tech Ecosystem**: For inspiring local solutions

## 🔮 Roadmap

### Q1 2024
- [ ] Voice AI integration with local languages
- [ ] Mobile native apps (iOS/Android)
- [ ] Blockchain integration for supply chain tracking
- [ ] Advanced market prediction models

### Q2 2024
- [ ] IoT sensor integration for real-time farm monitoring
- [ ] Satellite imagery analysis for crop health monitoring
- [ ] Financial services integration for farming loans
- [ ] Peer-to-peer farmer marketplace

### Q3 2024
- [ ] Machine learning model for yield prediction
- [ ] Climate change adaptation recommendations
- [ ] Carbon credit tracking and trading
- [ ] Advanced analytics dashboard

### Q4 2024
- [ ] Multi-country expansion (Kenya, Ghana, Tanzania)
- [ ] Advanced AI tutoring for farming techniques
- [ ] Integration with government agricultural systems
- [ ] Sustainable farming certification platform

---

**Built with ❤️ for farmers everywhere by the AgriSense AI team**

*Empowering agriculture through artificial intelligence*