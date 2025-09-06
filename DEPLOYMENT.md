# AgriSense AI - Render Deployment Guide

## 🚀 Deploy to Render

This guide will help you deploy AgriSense AI to Render for production use.

### Prerequisites

1. A GitHub account
2. A Render account (free tier available)
3. API keys for the services you want to use

### Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Push your code to the repository:

```bash
git init
git add .
git commit -m "Initial commit - AgriSense AI"
git branch -M main
git remote add origin https://github.com/yourusername/agrisense-ai.git
git push -u origin main
```

### Step 2: Configure Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

#### Basic Configuration
- **Name**: `agrisense-ai`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Instance Type**: Free tier (or higher for production)

#### Environment Variables

Add these environment variables in Render:

**Required Variables:**
```
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://... (will be auto-populated when you add PostgreSQL)
```

**API Keys (add as needed):**
```
OPENAI_API_KEY=your-openai-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
OPENWEATHER_API_KEY=your-weather-api-key
```

**Optional Variables:**
```
DEFAULT_AI_PROVIDER=openrouter
ENABLE_RAG=True
ENABLE_VOICE=True
ENABLE_SMS=False
ENABLE_WHATSAPP=False
ENABLE_WEATHER=True
LOG_LEVEL=INFO
```

### Step 3: Add Database

1. From Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `agrisense-db`
   - **Region**: Same as your web service
   - **Plan**: Free tier
3. After creation, connect it to your web service

### Step 4: Add Redis (Optional)

For enhanced performance:
1. Click "New +" → "Redis"
2. Configure:
   - **Name**: `agrisense-redis`
   - **Plan**: Free tier
3. Connect to your web service

### Step 5: Deploy

1. Click "Create Web Service"
2. Render will automatically build and deploy your application
3. Monitor the build logs for any issues

### Step 6: Custom Domain (Optional)

1. Go to your service settings
2. Add your custom domain
3. Configure your DNS to point to Render

## 🔧 Configuration Guide

### Essential API Keys

**OpenRouter (Recommended):**
- Get your API key from [OpenRouter](https://openrouter.ai)
- Supports multiple AI models
- Cost-effective for production

**OpenWeatherMap:**
- Get your API key from [OpenWeatherMap](https://openweathermap.org/api)
- Required for weather features

**Africa's Talking (SMS):**
- Get your API key from [Africa's Talking](https://africastalking.com)
- Required for SMS functionality

### Optional Integrations

**WhatsApp Business API:**
- Set up through Meta Business
- More complex setup, enterprise feature

**Twilio:**
- Alternative SMS provider
- Get credentials from [Twilio](https://twilio.com)

## 🎨 Features Included

✅ **Beautiful Animated UI**
- Glass morphism design
- Particle backgrounds
- Smooth animations
- Responsive design

✅ **AI-Powered Chat**
- Multiple AI providers
- Multilingual support (EN, HA, YO, IG, FF)
- Agricultural expertise

✅ **Weather Integration**
- Real-time weather data
- Location-based alerts
- Farming recommendations

✅ **Multi-Platform Support**
- SMS integration
- WhatsApp Business API
- Web interface

## 🛠 Troubleshooting

### Common Issues

**Build Failures:**
- Check that all dependencies are in `requirements.txt`
- Verify Python version compatibility
- Check for missing environment variables

**Database Connection:**
- Ensure `DATABASE_URL` is set correctly
- Check PostgreSQL service status
- Verify database permissions

**API Errors:**
- Validate API keys are correct
- Check rate limits
- Verify service endpoints

### Performance Optimization

**For Production:**
1. Use Redis for caching
2. Enable database connection pooling
3. Set appropriate rate limits
4. Monitor with Sentry (optional)

### Logs and Monitoring

Access logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. Monitor for errors and performance

## 📞 Support

For issues with deployment:
1. Check Render documentation
2. Review application logs
3. Verify environment variables
4. Test API connections

## 🌟 Features Overview

This AgriSense AI deployment includes:

- **Modern UI**: Glass morphism design with animations
- **AI Chat**: Multilingual agricultural assistant
- **Weather**: Real-time weather integration
- **SMS**: Africa's Talking SMS support
- **WhatsApp**: Business API integration
- **Voice**: Text-to-speech capabilities
- **Document**: PDF processing and RAG
- **Security**: JWT authentication, rate limiting
- **Monitoring**: Logging and error tracking

Ready for production use! 🚀