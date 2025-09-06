"""
AgriSense AI - Platform Integration Manager
Centralized management for all messaging platform integrations
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class PlatformManager:
    """Manages all messaging platform integrations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_platforms = {}
        self.message_handlers = {}
        
        # Platform configurations
        self.platform_configs = {
            'whatsapp': {
                'enabled': os.getenv('ENABLE_WHATSAPP', 'false').lower() == 'true',
                'token': os.getenv('WHATSAPP_ACCESS_TOKEN'),
                'phone_number_id': os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
                'webhook_verify_token': os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
            },
            'telegram': {
                'enabled': os.getenv('ENABLE_TELEGRAM', 'false').lower() == 'true',
                'token': os.getenv('TELEGRAM_BOT_TOKEN')
            },
            'discord': {
                'enabled': os.getenv('ENABLE_DISCORD', 'false').lower() == 'true',
                'token': os.getenv('DISCORD_BOT_TOKEN')
            },
            'instagram': {
                'enabled': os.getenv('ENABLE_INSTAGRAM', 'false').lower() == 'true',
                'access_token': os.getenv('INSTAGRAM_ACCESS_TOKEN'),
                'page_id': os.getenv('INSTAGRAM_PAGE_ID')
            },
            'sms': {
                'enabled': os.getenv('ENABLE_SMS', 'false').lower() == 'true',
                'api_key': os.getenv('AT_API_KEY'),
                'username': os.getenv('AT_USERNAME')
            },
            'email': {
                'enabled': os.getenv('ENABLE_EMAIL', 'false').lower() == 'true',
                'smtp_server': os.getenv('SMTP_SERVER'),
                'smtp_port': os.getenv('SMTP_PORT'),
                'username': os.getenv('SMTP_USERNAME'),
                'password': os.getenv('SMTP_PASSWORD')
            }
        }
        
        # Message routing rules
        self.routing_rules = {
            'urgent_weather_alerts': ['sms', 'whatsapp', 'telegram'],
            'market_updates': ['whatsapp', 'telegram', 'discord'],
            'daily_tips': ['all'],
            'pest_alerts': ['whatsapp', 'sms'],
            'community_discussions': ['discord'],
            'personal_consultation': ['whatsapp', 'telegram']
        }
    
    async def initialize_platforms(self):
        """Initialize all enabled platforms"""
        self.logger.info("🚀 Initializing platform integrations...")
        
        for platform_name, config in self.platform_configs.items():
            if config['enabled']:
                try:
                    await self._initialize_platform(platform_name, config)
                    self.logger.info(f"✅ {platform_name.title()} integration initialized")
                except Exception as e:
                    self.logger.error(f"❌ Failed to initialize {platform_name}: {str(e)}")
        
        self.logger.info(f"🎉 Platform initialization complete. Active platforms: {list(self.active_platforms.keys())}")
    
    async def _initialize_platform(self, platform_name: str, config: Dict[str, Any]):
        """Initialize a specific platform"""
        if platform_name == 'whatsapp':
            from .whatsapp_integration import WhatsAppIntegration
            integration = WhatsAppIntegration(
                config['token'],
                config['phone_number_id'],
                config['webhook_verify_token']
            )
            self.active_platforms['whatsapp'] = integration
            
        elif platform_name == 'telegram':
            from .telegram_integration import TelegramIntegration
            integration = TelegramIntegration(config['token'])
            self.active_platforms['telegram'] = integration
            # Start telegram bot in background
            asyncio.create_task(integration.start_bot())
            
        elif platform_name == 'discord':
            from .discord_integration import DiscordIntegration
            integration = DiscordIntegration(config['token'])
            self.active_platforms['discord'] = integration
            # Start discord bot in background
            asyncio.create_task(integration.start_bot())
            
        elif platform_name == 'instagram':
            from .instagram_integration import InstagramIntegration
            integration = InstagramIntegration(
                config['access_token'],
                config['page_id']
            )
            self.active_platforms['instagram'] = integration
            
        elif platform_name == 'sms':
            from .sms_integration import SMSIntegration
            integration = SMSIntegration(
                config['api_key'],
                config['username']
            )
            self.active_platforms['sms'] = integration
            
        elif platform_name == 'email':
            from .email_integration import EmailIntegration
            integration = EmailIntegration(
                config['smtp_server'],
                config['smtp_port'],
                config['username'],
                config['password']
            )
            self.active_platforms['email'] = integration
    
    async def broadcast_message(self, message: str, message_type: str, target_platforms: Optional[List[str]] = None, **kwargs):
        """Broadcast message to multiple platforms"""
        try:
            # Determine target platforms
            if target_platforms is None:
                target_platforms = self.routing_rules.get(message_type, ['all'])
            
            if 'all' in target_platforms:
                target_platforms = list(self.active_platforms.keys())
            
            # Filter to only active platforms
            available_platforms = [p for p in target_platforms if p in self.active_platforms]
            
            if not available_platforms:
                self.logger.warning(f"No active platforms found for message type: {message_type}")
                return
            
            # Send to each platform
            results = {}
            for platform in available_platforms:
                try:
                    integration = self.active_platforms[platform]
                    result = await self._send_to_platform(integration, platform, message, message_type, **kwargs)
                    results[platform] = {'success': True, 'result': result}
                except Exception as e:
                    self.logger.error(f"Failed to send to {platform}: {str(e)}")
                    results[platform] = {'success': False, 'error': str(e)}
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error broadcasting message: {str(e)}")
            return {'error': str(e)}
    
    async def _send_to_platform(self, integration, platform: str, message: str, message_type: str, **kwargs):
        """Send message to a specific platform"""
        if platform == 'whatsapp':
            # Extract WhatsApp specific parameters
            phone_number = kwargs.get('phone_number')
            if phone_number:
                return await integration.send_message(phone_number, message)
            else:
                # Broadcast to all subscribers
                return await integration.broadcast_message(message)
                
        elif platform == 'telegram':
            # Telegram broadcast would go to all bot subscribers
            return await integration.broadcast_message(message)
            
        elif platform == 'discord':
            # Discord would post to configured channels
            return await integration.broadcast_message(message, message_type)
            
        elif platform == 'instagram':
            # Instagram story or direct messages
            return await integration.send_message(message, message_type)
            
        elif platform == 'sms':
            phone_numbers = kwargs.get('phone_numbers', [])
            if phone_numbers:
                return await integration.send_bulk_sms(phone_numbers, message)
            
        elif platform == 'email':
            email_addresses = kwargs.get('email_addresses', [])
            if email_addresses:
                return await integration.send_bulk_email(email_addresses, f"AgriSense AI - {message_type}", message)
        
        return None
    
    async def process_incoming_message(self, platform: str, message_data: Dict[str, Any]):
        """Process incoming message from any platform"""
        try:
            if platform not in self.active_platforms:
                self.logger.warning(f"Received message from inactive platform: {platform}")
                return
            
            integration = self.active_platforms[platform]
            
            # Extract common message components
            user_id = self._extract_user_id(platform, message_data)
            message_text = self._extract_message_text(platform, message_data)
            message_type = self._detect_message_type(message_text)
            
            # Process with AI
            from services.ai_service import AIService
            ai_service = AIService()
            
            response = await ai_service.process_message(
                message_text,
                user_id,
                platform=platform,
                context=message_data
            )
            
            # Send response back through the same platform
            await self._send_response(integration, platform, response, message_data)
            
            # Log interaction
            self._log_interaction(platform, user_id, message_text, response)
            
        except Exception as e:
            self.logger.error(f"Error processing incoming message from {platform}: {str(e)}")
    
    def _extract_user_id(self, platform: str, message_data: Dict[str, Any]) -> str:
        """Extract user ID from platform-specific message data"""
        if platform == 'whatsapp':
            return message_data.get('from', {}).get('id', 'unknown')
        elif platform == 'telegram':
            return str(message_data.get('from', {}).get('id', 'unknown'))
        elif platform == 'discord':
            return str(message_data.get('author', {}).get('id', 'unknown'))
        elif platform == 'instagram':
            return message_data.get('sender', {}).get('id', 'unknown')
        else:
            return 'unknown'
    
    def _extract_message_text(self, platform: str, message_data: Dict[str, Any]) -> str:
        """Extract message text from platform-specific message data"""
        if platform == 'whatsapp':
            return message_data.get('text', {}).get('body', '')
        elif platform == 'telegram':
            return message_data.get('text', '')
        elif platform == 'discord':
            return message_data.get('content', '')
        elif platform == 'instagram':
            return message_data.get('message', {}).get('text', '')
        else:
            return ''
    
    def _detect_message_type(self, message_text: str) -> str:
        """Detect the type of message for routing"""
        text_lower = message_text.lower()
        
        if any(word in text_lower for word in ['weather', 'rain', 'storm', 'forecast']):
            return 'weather_query'
        elif any(word in text_lower for word in ['price', 'market', 'sell', 'buy']):
            return 'market_query'
        elif any(word in text_lower for word in ['pest', 'disease', 'insect', 'bug']):
            return 'pest_query'
        elif any(word in text_lower for word in ['crop', 'plant', 'grow', 'harvest']):
            return 'crop_query'
        elif any(word in text_lower for word in ['help', 'assist', 'support']):
            return 'help_request'
        else:
            return 'general_query'
    
    async def _send_response(self, integration, platform: str, response: str, original_message: Dict[str, Any]):
        """Send response back to user through the platform"""
        try:
            if platform == 'whatsapp':
                phone_number = original_message.get('from', {}).get('id')
                if phone_number:
                    await integration.send_message(phone_number, response)
                    
            elif platform == 'telegram':
                chat_id = original_message.get('chat', {}).get('id')
                if chat_id:
                    await integration.send_message(chat_id, response)
                    
            elif platform == 'discord':
                # Discord responses would be handled differently
                pass
                
            elif platform == 'instagram':
                sender_id = original_message.get('sender', {}).get('id')
                if sender_id:
                    await integration.send_message(sender_id, response)
                    
        except Exception as e:
            self.logger.error(f"Error sending response via {platform}: {str(e)}")
    
    def _log_interaction(self, platform: str, user_id: str, message: str, response: str):
        """Log interaction for analytics"""
        try:
            interaction_data = {
                'timestamp': datetime.now().isoformat(),
                'platform': platform,
                'user_id': user_id,
                'message': message[:200],  # Truncate for storage
                'response': response[:200],
                'message_type': self._detect_message_type(message)
            }
            
            # Save to database or log file
            self.logger.info(f"Interaction logged: {platform} - {user_id}")
            
        except Exception as e:
            self.logger.error(f"Error logging interaction: {str(e)}")
    
    async def send_scheduled_alerts(self):
        """Send scheduled alerts (weather, market, tips)"""
        try:
            # This would be called by a scheduler
            
            # Send weather alerts
            weather_alert = await self._generate_weather_alert()
            if weather_alert:
                await self.broadcast_message(
                    weather_alert,
                    'urgent_weather_alerts'
                )
            
            # Send market updates
            market_update = await self._generate_market_update()
            if market_update:
                await self.broadcast_message(
                    market_update,
                    'market_updates'
                )
            
            # Send daily tips
            daily_tip = await self._generate_daily_tip()
            if daily_tip:
                await self.broadcast_message(
                    daily_tip,
                    'daily_tips'
                )
                
        except Exception as e:
            self.logger.error(f"Error sending scheduled alerts: {str(e)}")
    
    async def _generate_weather_alert(self) -> Optional[str]:
        """Generate weather alert if needed"""
        # This would integrate with weather service
        return None
    
    async def _generate_market_update(self) -> Optional[str]:
        """Generate market update"""
        # This would integrate with market data service
        return None
    
    async def _generate_daily_tip(self) -> Optional[str]:
        """Generate daily farming tip"""
        tips = [
            "🌱 **Soil Tip**: Test your soil pH regularly. Most crops prefer 6.0-7.0 pH for optimal nutrient uptake.",
            "💧 **Watering Tip**: Water plants early morning to reduce evaporation and prevent fungal diseases.",
            "🐛 **Pest Control**: Encourage beneficial insects by planting diverse flowering plants around your farm.",
            "🌾 **Crop Rotation**: Rotate your crops annually to prevent soil depletion and break pest cycles.",
            "📅 **Timing**: Plant according to local climate patterns for the best results.",
            "🌿 **Organic Matter**: Add compost regularly to improve soil fertility and water retention.",
            "📊 **Records**: Keep detailed planting and harvest records for better planning next season."
        ]
        
        import random
        return random.choice(tips)
    
    async def get_platform_status(self) -> Dict[str, Any]:
        """Get status of all platforms"""
        status = {
            'active_platforms': list(self.active_platforms.keys()),
            'total_platforms': len(self.platform_configs),
            'platform_details': {}
        }
        
        for platform_name, config in self.platform_configs.items():
            status['platform_details'][platform_name] = {
                'enabled': config['enabled'],
                'active': platform_name in self.active_platforms,
                'configured': self._is_platform_configured(platform_name, config)
            }
        
        return status
    
    def _is_platform_configured(self, platform_name: str, config: Dict[str, Any]) -> bool:
        """Check if platform is properly configured"""
        required_keys = {
            'whatsapp': ['token', 'phone_number_id'],
            'telegram': ['token'],
            'discord': ['token'],
            'instagram': ['access_token', 'page_id'],
            'sms': ['api_key', 'username'],
            'email': ['smtp_server', 'username', 'password']
        }
        
        if platform_name not in required_keys:
            return False
        
        return all(config.get(key) for key in required_keys[platform_name])
    
    async def shutdown(self):
        """Shutdown all platform integrations"""
        self.logger.info("🔴 Shutting down platform integrations...")
        
        for platform_name, integration in self.active_platforms.items():
            try:
                if hasattr(integration, 'stop_bot'):
                    await integration.stop_bot()
                self.logger.info(f"✅ {platform_name} integration stopped")
            except Exception as e:
                self.logger.error(f"Error stopping {platform_name}: {str(e)}")
        
        self.active_platforms.clear()
        self.logger.info("🔴 All platform integrations stopped")

# Global platform manager instance
platform_manager = PlatformManager()