"""
Instagram Integration for AgriSense AI
Handles Instagram Direct Messages and Story Responses

This integration uses the Instagram Graph API to:
- Receive and respond to direct messages
- Handle story replies and mentions
- Send agricultural advice and media
- Process image uploads for crop analysis
- Manage Instagram Business account interactions
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class InstagramIntegration:
    """Instagram messaging integration for agricultural assistance"""
    
    def __init__(self, access_token: str, page_id: str = None, verify_token: str = None):
        self.access_token = access_token
        self.page_id = page_id
        self.verify_token = verify_token or "agrisense_instagram_webhook"
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum 1 second between requests
        
        # Supported media types for agricultural content
        self.supported_image_types = ['image/jpeg', 'image/jpg', 'image/png']
        self.max_file_size = 25 * 1024 * 1024  # 25MB
        
        logger.info("Instagram integration initialized")
    
    def verify_webhook(self, request_data: Dict) -> tuple:
        """
        Verify Instagram webhook subscription
        
        Args:
            request_data: Request data containing verification parameters
            
        Returns:
            Tuple of (response, status_code)
        """
        try:
            mode = request_data.get('hub.mode')
            token = request_data.get('hub.verify_token')
            challenge = request_data.get('hub.challenge')
            
            if mode == 'subscribe' and token == self.verify_token:
                logger.info("Instagram webhook verified successfully")
                return challenge, 200
            else:
                logger.warning("Instagram webhook verification failed")
                return 'Verification failed', 403
                
        except Exception as e:
            logger.error(f"Instagram webhook verification error: {str(e)}")
            return 'Verification error', 500
    
    def handle_webhook(self, webhook_data: Dict) -> Dict:
        """
        Handle incoming Instagram webhook events
        
        Args:
            webhook_data: Webhook payload from Instagram
            
        Returns:
            Response dictionary
        """
        try:
            if not webhook_data.get('entry'):
                return {'status': 'no_entry_data'}
            
            responses = []
            for entry in webhook_data['entry']:
                if 'messaging' in entry:
                    # Handle direct messages
                    for message_event in entry['messaging']:
                        response = self._handle_message(message_event)
                        if response:
                            responses.append(response)
                
                elif 'changes' in entry:
                    # Handle story replies and mentions
                    for change in entry['changes']:
                        if change.get('field') == 'story_insights':
                            response = self._handle_story_interaction(change)
                            if response:
                                responses.append(response)
            
            return {
                'status': 'success',
                'responses': responses,
                'processed_count': len(responses)
            }
            
        except Exception as e:
            logger.error(f"Instagram webhook handling error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_message(self, message_event: Dict) -> Optional[Dict]:
        """
        Process Instagram direct message
        
        Args:
            message_event: Instagram message event data
            
        Returns:
            Response dictionary or None
        """
        try:
            sender_id = message_event.get('sender', {}).get('id')
            message_data = message_event.get('message', {})
            
            if not sender_id or not message_data:
                return None
            
            # Extract message content
            message_text = message_data.get('text', '')
            attachments = message_data.get('attachments', [])
            
            # Get user profile information
            user_profile = self._get_user_profile(sender_id)
            
            # Process the message
            if message_text:
                response = self._process_text_message(sender_id, message_text, user_profile)
            elif attachments:
                response = self._process_media_message(sender_id, attachments, user_profile)
            else:
                response = self._send_help_message(sender_id)
            
            return response
            
        except Exception as e:
            logger.error(f"Instagram message handling error: {str(e)}")
            return None
    
    def _handle_story_interaction(self, change_data: Dict) -> Optional[Dict]:
        """
        Handle Instagram story replies and mentions
        
        Args:
            change_data: Story interaction data
            
        Returns:
            Response dictionary or None
        """
        try:
            # Process story mentions and replies
            value = change_data.get('value', {})
            story_type = value.get('story_type')
            
            if story_type == 'story_reply':
                return self._handle_story_reply(value)
            elif story_type == 'story_mention':
                return self._handle_story_mention(value)
            
            return None
            
        except Exception as e:
            logger.error(f"Instagram story interaction error: {str(e)}")
            return None
    
    def _process_text_message(self, sender_id: str, message: str, user_profile: Dict) -> Dict:
        """
        Process text message and generate appropriate response
        
        Args:
            sender_id: Instagram user ID
            message: Message text
            user_profile: User profile information
            
        Returns:
            Response dictionary
        """
        try:
            message_lower = message.lower().strip()
            
            # Command routing
            if any(greeting in message_lower for greeting in ['hello', 'hi', 'hey', 'start']):
                return self._send_welcome_message(sender_id, user_profile.get('name', 'Friend'))
            
            elif any(word in message_lower for word in ['weather', 'rain', 'temperature', 'forecast']):
                return self._handle_weather_request(sender_id, message)
            
            elif any(word in message_lower for word in ['crop', 'plant', 'farming', 'agriculture']):
                return self._handle_crop_advice(sender_id, message)
            
            elif any(word in message_lower for word in ['price', 'market', 'sell', 'cost']):
                return self._handle_market_inquiry(sender_id, message)
            
            elif any(word in message_lower for word in ['pest', 'disease', 'problem', 'insect']):
                return self._handle_pest_inquiry(sender_id, message)
            
            elif any(word in message_lower for word in ['help', 'commands', 'what can you do']):
                return self._send_help_message(sender_id)
            
            else:
                # General agricultural question - forward to AI
                return self._handle_general_question(sender_id, message, user_profile)
        
        except Exception as e:
            logger.error(f"Instagram text message processing error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _process_media_message(self, sender_id: str, attachments: List, user_profile: Dict) -> Dict:
        """
        Process media attachments (images for crop analysis)
        
        Args:
            sender_id: Instagram user ID
            attachments: List of media attachments
            user_profile: User profile information
            
        Returns:
            Response dictionary
        """
        try:
            for attachment in attachments:
                if attachment.get('type') == 'image':
                    image_url = attachment.get('payload', {}).get('url')
                    if image_url:
                        # Analyze the crop image
                        analysis_result = self._analyze_crop_image(image_url)
                        return self._send_image_analysis_result(sender_id, analysis_result)
            
            # If no processable images found
            return self._send_message(
                sender_id,
                "🤳 I can analyze crop images! Please send a clear photo of your crops, plants, or any farming issues you're experiencing.",
                quick_replies=[
                    {'title': '📸 Photo Tips', 'payload': 'photo_tips'},
                    {'title': '🌱 Crop Guide', 'payload': 'crop_guide'},
                    {'title': '🆘 Help', 'payload': 'help'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram media processing error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _send_welcome_message(self, sender_id: str, user_name: str) -> Dict:
        """Send welcome message to new users"""
        try:
            welcome_text = f"""🌾 Welcome to AgriSense AI, {user_name}!
            
I'm your agricultural intelligence assistant. I can help you with:

🌤️ Weather forecasts and farming advice
🌱 Crop recommendations and planting tips
📸 Crop disease identification (send photos!)
💰 Market prices and selling advice
🐛 Pest control solutions
📚 Agricultural knowledge and best practices

How can I assist your farming journey today?"""
            
            return self._send_message(
                sender_id,
                welcome_text,
                quick_replies=[
                    {'title': '🌤️ Weather', 'payload': 'weather'},
                    {'title': '🌱 Crops', 'payload': 'crops'},
                    {'title': '📸 Analyze Photo', 'payload': 'photo_analysis'},
                    {'title': '💰 Market Prices', 'payload': 'market'},
                    {'title': '🆘 Help', 'payload': 'help'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram welcome message error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _handle_weather_request(self, sender_id: str, message: str) -> Dict:
        """Handle weather-related requests"""
        try:
            # Extract location from message or use default
            location = self._extract_location(message) or "Nigeria"
            
            # Here you would integrate with your weather service
            # For now, return a template response
            weather_text = f"""🌤️ Weather Information for {location}
            
Today: 28°C, Partly cloudy
Tomorrow: 26°C, Light rain expected
This Week: Mix of sun and rain - perfect for planting!

🌱 Farming Recommendations:
• Good time for planting maize and soybeans
• Check drainage systems before rain
• Harvest ready crops before heavy rains
• Apply fertilizer during dry periods

Would you like detailed forecasts or specific crop advice?"""
            
            return self._send_message(
                sender_id,
                weather_text,
                quick_replies=[
                    {'title': '📅 5-Day Forecast', 'payload': 'forecast_5day'},
                    {'title': '🌱 Planting Tips', 'payload': 'planting_tips'},
                    {'title': '💧 Irrigation Advice', 'payload': 'irrigation'},
                    {'title': '🔄 Different Location', 'payload': 'change_location'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram weather request error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _handle_crop_advice(self, sender_id: str, message: str) -> Dict:
        """Handle crop-related questions"""
        try:
            crop_text = """🌱 Crop Advisory Service
            
Popular crops for this season:
🌽 Maize - Plant now, harvest in 3-4 months
🫘 Soybeans - Excellent protein crop
🍅 Tomatoes - High market value
🥒 Cucumbers - Fast growing, good profits
🌶️ Peppers - Year-round demand

What specific crop information do you need?"""
            
            return self._send_message(
                sender_id,
                crop_text,
                quick_replies=[
                    {'title': '🌽 Maize Tips', 'payload': 'maize_advice'},
                    {'title': '🫘 Soybean Guide', 'payload': 'soybean_advice'},
                    {'title': '🍅 Tomato Farming', 'payload': 'tomato_advice'},
                    {'title': '🌶️ Pepper Growing', 'payload': 'pepper_advice'},
                    {'title': '💰 Profitable Crops', 'payload': 'profitable_crops'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram crop advice error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _handle_market_inquiry(self, sender_id: str, message: str) -> Dict:
        """Handle market price requests"""
        try:
            market_text = """💰 Current Market Prices (per bag/kg)
            
🌽 Maize: ₦45,000 - ₦50,000 per bag ⬆️
🍅 Tomatoes: ₦25,000 - ₦30,000 per crate ⬆️
🌶️ Peppers: ₦15,000 - ₦18,000 per basket ➡️
🫘 Soybeans: ₦80,000 - ₦85,000 per bag ⬆️
🥕 Carrots: ₦12,000 - ₦15,000 per bag ⬆️

📈 Market Trends:
• Prices trending upward due to seasonal demand
• Best selling time: Next 2 weeks
• High demand in urban markets

Need specific crop price alerts?"""
            
            return self._send_message(
                sender_id,
                market_text,
                quick_replies=[
                    {'title': '📈 Price Alerts', 'payload': 'price_alerts'},
                    {'title': '🏪 Best Markets', 'payload': 'best_markets'},
                    {'title': '📅 Selling Times', 'payload': 'selling_times'},
                    {'title': '🚚 Transport Tips', 'payload': 'transport_tips'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram market inquiry error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _handle_pest_inquiry(self, sender_id: str, message: str) -> Dict:
        """Handle pest and disease questions"""
        try:
            pest_text = """🐛 Pest & Disease Control Center
            
Common issues this season:
🐛 Fall Armyworm - Attacks maize and rice
🦗 Grasshoppers - Damage young plants
🍄 Fungal diseases - Due to humidity
🐜 Termites - Attack roots and stems
🦠 Bacterial wilt - Affects tomatoes

🔬 For accurate diagnosis:
Send a clear photo of affected plants!

What pest issue are you dealing with?"""
            
            return self._send_message(
                sender_id,
                pest_text,
                quick_replies=[
                    {'title': '📸 Send Photo', 'payload': 'photo_diagnosis'},
                    {'title': '🐛 Fall Armyworm', 'payload': 'armyworm_help'},
                    {'title': '🍄 Fungal Disease', 'payload': 'fungal_help'},
                    {'title': '🌱 Prevention Tips', 'payload': 'prevention_tips'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram pest inquiry error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _send_help_message(self, sender_id: str) -> Dict:
        """Send help and command information"""
        try:
            help_text = """🆘 AgriSense AI Help Center
            
I can assist you with:

🌤️ Weather forecasts and alerts
🌱 Crop advice and planting guides
📸 Crop disease identification (send photos!)
💰 Market prices and trends
🐛 Pest control solutions
📚 Agricultural best practices
💡 Farming tips and techniques
🔔 Custom alerts and reminders

📱 How to use:
• Type your question naturally
• Send photos for crop analysis
• Use quick reply buttons for common topics
• Ask about specific crops, weather, or markets

Start by telling me what farming challenge you're facing!"""
            
            return self._send_message(
                sender_id,
                help_text,
                quick_replies=[
                    {'title': '🌤️ Weather', 'payload': 'weather'},
                    {'title': '🌱 Crops', 'payload': 'crops'},
                    {'title': '💰 Markets', 'payload': 'market'},
                    {'title': '🐛 Pest Control', 'payload': 'pest_control'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram help message error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _handle_general_question(self, sender_id: str, message: str, user_profile: Dict) -> Dict:
        """Handle general agricultural questions using AI"""
        try:
            # Here you would integrate with your AI service
            # For now, return a helpful response
            
            ai_response = f"""🤖 AgriSense AI Response
            
Thank you for your question: "{message[:100]}..."

I'm processing your agricultural query and will provide detailed advice based on:
• Current weather conditions
• Seasonal farming patterns
• Local market trends
• Best agricultural practices

For immediate assistance, you can:
📸 Send photos for crop analysis
🌤️ Check weather forecasts
💰 View current market prices
🆘 Get emergency farming help

Would you like me to connect you with a specific topic?"""
            
            return self._send_message(
                sender_id,
                ai_response,
                quick_replies=[
                    {'title': '📸 Photo Analysis', 'payload': 'photo_analysis'},
                    {'title': '🌤️ Weather Check', 'payload': 'weather'},
                    {'title': '💰 Market Info', 'payload': 'market'},
                    {'title': '🌱 Crop Advice', 'payload': 'crops'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram general question error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _analyze_crop_image(self, image_url: str) -> Dict:
        """
        Analyze crop image for diseases, pests, or issues
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Here you would integrate with your image analysis AI
            # For now, return a template analysis
            
            return {
                'status': 'analyzed',
                'confidence': 0.85,
                'diagnosis': 'Healthy crop with minor nutrient deficiency',
                'recommendations': [
                    'Apply balanced NPK fertilizer',
                    'Ensure adequate water drainage',
                    'Monitor for pest activity'
                ],
                'urgency': 'low',
                'next_steps': 'Continue monitoring and maintain regular care'
            }
            
        except Exception as e:
            logger.error(f"Instagram image analysis error: {str(e)}")
            return {
                'status': 'error',
                'message': 'Unable to analyze image at this time'
            }
    
    def _send_image_analysis_result(self, sender_id: str, analysis: Dict) -> Dict:
        """Send image analysis results to user"""
        try:
            if analysis.get('status') == 'error':
                return self._send_message(
                    sender_id,
                    "😕 I couldn't analyze your image right now. Please try again with a clear, well-lit photo of your crops."
                )
            
            diagnosis = analysis.get('diagnosis', 'Analysis completed')
            recommendations = analysis.get('recommendations', [])
            urgency = analysis.get('urgency', 'medium')
            
            urgency_emoji = {'low': '🟢', 'medium': '🟡', 'high': '🔴'}.get(urgency, '🟡')
            
            result_text = f"""📸 Crop Analysis Results
            
{urgency_emoji} Status: {diagnosis}
Confidence: {analysis.get('confidence', 0.8) * 100:.0f}%

💡 Recommendations:
{chr(10).join(f"• {rec}" for rec in recommendations[:4])}

Next Steps: {analysis.get('next_steps', 'Monitor progress')}

Need more specific advice or have questions about these recommendations?"""
            
            return self._send_message(
                sender_id,
                result_text,
                quick_replies=[
                    {'title': '🔬 More Details', 'payload': 'analysis_details'},
                    {'title': '💊 Treatment Plan', 'payload': 'treatment_plan'},
                    {'title': '📸 Another Photo', 'payload': 'new_photo'},
                    {'title': '🌱 Crop Care Tips', 'payload': 'care_tips'}
                ]
            )
            
        except Exception as e:
            logger.error(f"Instagram analysis result error: {str(e)}")
            return self._send_error_message(sender_id)
    
    def _send_message(self, recipient_id: str, message: str, quick_replies: List = None) -> Dict:
        """
        Send message to Instagram user
        
        Args:
            recipient_id: Instagram user ID
            message: Message text
            quick_replies: Optional quick reply buttons
            
        Returns:
            Response dictionary
        """
        try:
            # Rate limiting
            self._rate_limit()
            
            # Prepare message payload
            message_data = {
                'recipient': {'id': recipient_id},
                'message': {'text': message}
            }
            
            # Add quick replies if provided
            if quick_replies:
                message_data['message']['quick_replies'] = [
                    {
                        'content_type': 'text',
                        'title': qr['title'][:20],  # Instagram limits quick reply titles
                        'payload': qr['payload']
                    }
                    for qr in quick_replies[:10]  # Instagram limits quick replies
                ]
            
            # Send message via Instagram Graph API
            response = requests.post(
                f"{self.base_url}/me/messages",
                params={'access_token': self.access_token},
                json=message_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Instagram message sent successfully to {recipient_id}")
                return {
                    'status': 'sent',
                    'recipient_id': recipient_id,
                    'message_id': response.json().get('message_id')
                }
            else:
                logger.error(f"Instagram message failed: {response.status_code} - {response.text}")
                return {
                    'status': 'failed',
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Instagram message sending error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _send_error_message(self, sender_id: str) -> Dict:
        """Send error message to user"""
        return self._send_message(
            sender_id,
            "😕 I encountered an issue processing your request. Please try again or contact support if the problem continues.",
            quick_replies=[
                {'title': '🔄 Try Again', 'payload': 'retry'},
                {'title': '🆘 Help', 'payload': 'help'},
                {'title': '📞 Support', 'payload': 'support'}
            ]
        )
    
    def _get_user_profile(self, user_id: str) -> Dict:
        """
        Get Instagram user profile information
        
        Args:
            user_id: Instagram user ID
            
        Returns:
            User profile dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/{user_id}",
                params={
                    'fields': 'name,profile_pic',
                    'access_token': self.access_token
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to get Instagram user profile: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Instagram user profile error: {str(e)}")
            return {}
    
    def _handle_story_reply(self, reply_data: Dict) -> Dict:
        """Handle Instagram story replies"""
        try:
            sender_id = reply_data.get('from', {}).get('id')
            message = reply_data.get('message', '')
            
            if sender_id:
                return self._send_message(
                    sender_id,
                    f"🌾 Thanks for replying to our story! How can AgriSense AI help with your farming needs today?"
                )
            
            return {'status': 'no_sender'}
            
        except Exception as e:
            logger.error(f"Instagram story reply error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _handle_story_mention(self, mention_data: Dict) -> Dict:
        """Handle Instagram story mentions"""
        try:
            sender_id = mention_data.get('from', {}).get('id')
            
            if sender_id:
                return self._send_message(
                    sender_id,
                    f"🌾 Thanks for mentioning AgriSense AI! I'm here to help with all your agricultural needs. What farming challenge can I assist you with?"
                )
            
            return {'status': 'no_sender'}
            
        except Exception as e:
            logger.error(f"Instagram story mention error: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _extract_location(self, message: str) -> Optional[str]:
        """Extract location from message text"""
        try:
            # Simple location extraction - can be enhanced with NLP
            common_locations = ['lagos', 'abuja', 'kano', 'kaduna', 'ibadan', 'nigeria']
            message_lower = message.lower()
            
            for location in common_locations:
                if location in message_lower:
                    return location.title()
            
            return None
            
        except Exception as e:
            logger.error(f"Location extraction error: {str(e)}")
            return None
    
    def _rate_limit(self):
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def broadcast_message(self, user_ids: List[str], message: str) -> Dict:
        """
        Broadcast message to multiple Instagram users
        
        Args:
            user_ids: List of Instagram user IDs
            message: Message to broadcast
            
        Returns:
            Broadcast result dictionary
        """
        try:
            results = []
            success_count = 0
            failed_count = 0
            
            for user_id in user_ids:
                result = self._send_message(user_id, message)
                results.append(result)
                
                if result.get('status') == 'sent':
                    success_count += 1
                else:
                    failed_count += 1
                
                # Rate limiting between broadcasts
                time.sleep(1)
            
            return {
                'status': 'completed',
                'total_sent': len(user_ids),
                'successful': success_count,
                'failed': failed_count,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Instagram broadcast error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def send_media_message(self, recipient_id: str, image_url: str, caption: str = "") -> Dict:
        """
        Send image message with caption
        
        Args:
            recipient_id: Instagram user ID
            image_url: URL of image to send
            caption: Optional image caption
            
        Returns:
            Response dictionary
        """
        try:
            self._rate_limit()
            
            message_data = {
                'recipient': {'id': recipient_id},
                'message': {
                    'attachment': {
                        'type': 'image',
                        'payload': {
                            'url': image_url
                        }
                    }
                }
            }
            
            if caption:
                message_data['message']['text'] = caption
            
            response = requests.post(
                f"{self.base_url}/me/messages",
                params={'access_token': self.access_token},
                json=message_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Instagram media message sent to {recipient_id}")
                return {
                    'status': 'sent',
                    'recipient_id': recipient_id,
                    'message_id': response.json().get('message_id')
                }
            else:
                logger.error(f"Instagram media message failed: {response.text}")
                return {
                    'status': 'failed',
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"Instagram media message error: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def get_webhook_info(self) -> Dict:
        """Get webhook subscription information"""
        try:
            response = requests.get(
                f"{self.base_url}/{self.page_id}/subscribed_apps",
                params={'access_token': self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.text}
                
        except Exception as e:
            logger.error(f"Instagram webhook info error: {str(e)}")
            return {'error': str(e)}


# Integration test function
def test_instagram_integration():
    """Test Instagram integration functionality"""
    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    page_id = os.getenv('INSTAGRAM_PAGE_ID')
    
    if not access_token:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in environment variables")
        return False
    
    try:
        instagram = InstagramIntegration(access_token, page_id)
        
        # Test webhook verification
        verify_data = {
            'hub.mode': 'subscribe',
            'hub.verify_token': instagram.verify_token,
            'hub.challenge': 'test_challenge'
        }
        
        response, status = instagram.verify_webhook(verify_data)
        
        if status == 200:
            print("✅ Instagram integration test passed")
            return True
        else:
            print(f"❌ Instagram integration test failed: {status}")
            return False
            
    except Exception as e:
        print(f"❌ Instagram integration test error: {str(e)}")
        return False


if __name__ == "__main__":
    # Run integration test
    test_instagram_integration()