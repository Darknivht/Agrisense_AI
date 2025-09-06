"""
AgriSense AI - WhatsApp Business API Integration
Advanced WhatsApp messaging for farmer communication
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class WhatsAppIntegration:
    """WhatsApp Business API integration for farmer communication"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        self.phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
        self.webhook_verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
        self.logger = logging.getLogger(__name__)
        
        # Message templates for different languages
        self.message_templates = {
            'welcome': {
                'en': "Welcome to AgriSense AI! 🌾 I'm here to help with your farming questions. Ask me about crops, weather, pests, or market prices.",
                'ha': "Barka da zuwa AgriSense AI! 🌾 Ina nan don taimaka muku game da tambayoyin noma. Tambayeni game da shuke-shuke, yanayi, kwari, ko farashin kasuwa.",
                'yo': "Kaabo si AgriSense AI! 🌾 Mo wa nibi lati ran yin lowo pelu awon ibeere agbe yin. Beere lowo mi nipa eweko, oju ojo, kokoro, tabi owo oja.",
                'ig': "Nnọọ na AgriSense AI! 🌾 Anọ m ebe a inyere gị aka na ajụjụ ọrụ ugbo gị. Jụọ m ajụjụ gbasara ihe ọkụkụ, ihu igwe, ụmụ ahụhụ, ma ọ bụ ọnụahịa ahịa.",
                'ff': "Hunyaawa e AgriSense AI! 🌾 Mi ti jooni ngam wallit-aada e naamne wuurnde maa. Naamnir-mi e jiiwugol, jemma, marawle, kam keewɗe luumo."
            },
            'weather_alert': {
                'en': "🌡️ Weather Alert: {message}",
                'ha': "🌡️ Gargadin Yanayi: {message}",
                'yo': "🌡️ Ikilọ Oju Ojo: {message}",
                'ig': "🌡️ Ọkwa Ihu Igwe: {message}",
                'ff': "🌡️ Haɓɓindol Jemma: {message}"
            },
            'pest_alert': {
                'en': "🐛 Pest Alert: {message}",
                'ha': "🐛 Gargadin Kwari: {message}",
                'yo': "🐛 Ikilọ Kokoro: {message}",
                'ig': "🐛 Ọkwa Ụmụ Ahụhụ: {message}",
                'ff': "🐛 Haɓɓindol Marawle: {message}"
            },
            'market_update': {
                'en': "💰 Market Update: {message}",
                'ha': "💰 Sabuntawar Kasuwa: {message}",
                'yo': "💰 Imudojuiwon Oja: {message}",
                'ig': "💰 Mmelite Ahịa: {message}",
                'ff': "💰 Kecce Luumo: {message}"
            }
        }
    
    def verify_webhook(self, request) -> str:
        """Verify webhook for WhatsApp Business API"""
        try:
            mode = request.args.get('hub.mode')
            token = request.args.get('hub.verify_token')
            challenge = request.args.get('hub.challenge')
            
            if mode == 'subscribe' and token == self.webhook_verify_token:
                self.logger.info("WhatsApp webhook verified successfully")
                return challenge
            else:
                self.logger.warning("WhatsApp webhook verification failed")
                return "Verification failed", 403
                
        except Exception as e:
            self.logger.error(f"Error verifying WhatsApp webhook: {str(e)}")
            return "Verification error", 500
    
    def handle_message(self, webhook_data: Dict[str, Any]) -> Dict[str, str]:
        """Handle incoming WhatsApp messages"""
        try:
            if not webhook_data.get('entry'):
                return {'status': 'no_entry'}
            
            for entry in webhook_data['entry']:
                if not entry.get('changes'):
                    continue
                
                for change in entry['changes']:
                    if change.get('field') != 'messages':
                        continue
                    
                    value = change.get('value', {})
                    messages = value.get('messages', [])
                    
                    for message in messages:
                        self._process_incoming_message(message, value)
            
            return {'status': 'processed'}
            
        except Exception as e:
            self.logger.error(f"Error handling WhatsApp message: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def _process_incoming_message(self, message: Dict[str, Any], value: Dict[str, Any]):
        """Process individual incoming message"""
        try:
            # Extract message details
            from_number = message.get('from')
            message_id = message.get('id')
            timestamp = message.get('timestamp')
            
            # Get user profile if available
            contacts = value.get('contacts', [])
            user_profile = contacts[0] if contacts else {}
            user_name = user_profile.get('profile', {}).get('name', 'Farmer')
            
            # Handle different message types
            if message.get('type') == 'text':
                text_content = message.get('text', {}).get('body', '')
                self._handle_text_message(from_number, text_content, user_name)
            
            elif message.get('type') == 'button':
                button_payload = message.get('button', {}).get('payload', '')
                self._handle_button_response(from_number, button_payload, user_name)
            
            elif message.get('type') == 'interactive':
                interactive_data = message.get('interactive', {})
                self._handle_interactive_response(from_number, interactive_data, user_name)
            
            elif message.get('type') == 'location':
                location_data = message.get('location', {})
                self._handle_location_message(from_number, location_data, user_name)
            
            # Mark message as read
            self._mark_message_read(message_id)
            
        except Exception as e:
            self.logger.error(f"Error processing incoming message: {str(e)}")
    
    def _handle_text_message(self, from_number: str, text: str, user_name: str):
        """Handle text messages"""
        try:
            # Detect language (simplified)
            language = self._detect_language(text)
            
            # Check for specific commands
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['hello', 'hi', 'start', 'sannu', 'bawo', 'ndewo']):
                self._send_welcome_message(from_number, language, user_name)
            
            elif any(word in text_lower for word in ['weather', 'yanayi', 'oju ojo', 'ihu igwe', 'jemma']):
                self._send_weather_menu(from_number, language)
            
            elif any(word in text_lower for word in ['market', 'price', 'kasuwa', 'farashi', 'oja', 'owo', 'luumo']):
                self._send_market_menu(from_number, language)
            
            elif any(word in text_lower for word in ['pest', 'disease', 'kwari', 'cuta', 'kokoro', 'aisan', 'marawle']):
                self._send_pest_menu(from_number, language)
            
            else:
                # Send to AI for processing (integrate with main AI engine)
                self._process_with_ai(from_number, text, language, user_name)
            
        except Exception as e:
            self.logger.error(f"Error handling text message: {str(e)}")
    
    def _send_welcome_message(self, to_number: str, language: str, user_name: str):
        """Send welcome message with menu options"""
        try:
            welcome_text = self.message_templates['welcome'][language].format(name=user_name)
            
            # Create interactive buttons
            interactive_message = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "header": {
                        "type": "text",
                        "text": "AgriSense AI 🌾"
                    },
                    "body": {
                        "text": welcome_text
                    },
                    "action": {
                        "buttons": [
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "weather_info",
                                    "title": "Weather 🌤️" if language == 'en' else "Yanayi 🌤️"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "crop_advice",
                                    "title": "Crop Tips 🌱" if language == 'en' else "Shawara 🌱"
                                }
                            },
                            {
                                "type": "reply",
                                "reply": {
                                    "id": "market_prices",
                                    "title": "Market 💰" if language == 'en' else "Kasuwa 💰"
                                }
                            }
                        ]
                    }
                }
            }
            
            self._send_message(interactive_message)
            
        except Exception as e:
            self.logger.error(f"Error sending welcome message: {str(e)}")
    
    def _send_weather_menu(self, to_number: str, language: str):
        """Send weather-related menu options"""
        try:
            weather_options = {
                'en': {
                    'title': 'Weather Information 🌤️',
                    'body': 'Choose what weather information you need:',
                    'options': [
                        {'id': 'current_weather', 'title': 'Current Weather'},
                        {'id': 'forecast', 'title': '5-Day Forecast'},
                        {'id': 'weather_alerts', 'title': 'Weather Alerts'},
                        {'id': 'irrigation_advice', 'title': 'Irrigation Advice'}
                    ]
                },
                'ha': {
                    'title': 'Bayanan Yanayi 🌤️',
                    'body': 'Zaɓi irin bayanan yanayi da kuke bukata:',
                    'options': [
                        {'id': 'current_weather', 'title': 'Yanayin Yanzu'},
                        {'id': 'forecast', 'title': 'Hasashen Kwanaki 5'},
                        {'id': 'weather_alerts', 'title': 'Gargadin Yanayi'},
                        {'id': 'irrigation_advice', 'title': 'Shawarar Ban Ruwa'}
                    ]
                }
            }
            
            options = weather_options.get(language, weather_options['en'])
            
            list_message = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "list",
                    "header": {
                        "type": "text",
                        "text": options['title']
                    },
                    "body": {
                        "text": options['body']
                    },
                    "action": {
                        "button": "Select Option" if language == 'en' else "Zaɓi",
                        "sections": [
                            {
                                "title": "Weather Options" if language == 'en' else "Zaɓuɓɓukan Yanayi",
                                "rows": [
                                    {
                                        "id": opt['id'],
                                        "title": opt['title']
                                    } for opt in options['options']
                                ]
                            }
                        ]
                    }
                }
            }
            
            self._send_message(list_message)
            
        except Exception as e:
            self.logger.error(f"Error sending weather menu: {str(e)}")
    
    def send_weather_alert(self, phone_numbers: List[str], weather_data: Dict[str, Any], language: str = 'en'):
        """Send weather alerts to farmers"""
        try:
            alert_message = self._format_weather_alert(weather_data, language)
            
            for phone_number in phone_numbers:
                message = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": alert_message
                    }
                }
                
                self._send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error sending weather alerts: {str(e)}")
    
    def send_market_update(self, phone_numbers: List[str], market_data: Dict[str, Any], language: str = 'en'):
        """Send market price updates to farmers"""
        try:
            market_message = self._format_market_update(market_data, language)
            
            for phone_number in phone_numbers:
                message = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": market_message
                    }
                }
                
                self._send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error sending market updates: {str(e)}")
    
    def send_pest_alert(self, phone_numbers: List[str], pest_data: Dict[str, Any], language: str = 'en'):
        """Send pest and disease alerts to farmers"""
        try:
            pest_message = self._format_pest_alert(pest_data, language)
            
            for phone_number in phone_numbers:
                message = {
                    "messaging_product": "whatsapp",
                    "to": phone_number,
                    "type": "text",
                    "text": {
                        "body": pest_message
                    }
                }
                
                self._send_message(message)
                
        except Exception as e:
            self.logger.error(f"Error sending pest alerts: {str(e)}")
    
    def _send_message(self, message_data: Dict[str, Any]) -> bool:
        """Send message via WhatsApp Business API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(url, headers=headers, json=message_data, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"WhatsApp message sent successfully to {message_data.get('to')}")
            return True
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending WhatsApp message: {str(e)}")
            return False
    
    def _mark_message_read(self, message_id: str):
        """Mark message as read"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            data = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            requests.post(url, headers=headers, json=data, timeout=10)
            
        except Exception as e:
            self.logger.error(f"Error marking message as read: {str(e)}")
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on keywords"""
        text_lower = text.lower()
        
        # Hausa keywords
        hausa_keywords = ['sannu', 'yaya', 'nawa', 'ina', 'yanayi', 'shuke', 'kwari', 'kasuwa']
        if any(keyword in text_lower for keyword in hausa_keywords):
            return 'ha'
        
        # Yoruba keywords
        yoruba_keywords = ['bawo', 'elo', 'nibi', 'oju ojo', 'eweko', 'kokoro', 'oja']
        if any(keyword in text_lower for keyword in yoruba_keywords):
            return 'yo'
        
        # Igbo keywords
        igbo_keywords = ['ndewo', 'kedu', 'ebe', 'ihu igwe', 'ihe okuku', 'umu ahuhu', 'ahia']
        if any(keyword in text_lower for keyword in igbo_keywords):
            return 'ig'
        
        # Default to English
        return 'en'
    
    def _format_weather_alert(self, weather_data: Dict[str, Any], language: str) -> str:
        """Format weather alert message"""
        try:
            temp = weather_data.get('temperature', {}).get('current', 'N/A')
            condition = weather_data.get('weather', {}).get('description', 'Unknown')
            location = weather_data.get('location', 'your area')
            
            templates = {
                'en': f"🌡️ Weather Alert for {location}:\\n\\nTemperature: {temp}°C\\nCondition: {condition}\\n\\nStay safe and protect your crops!",
                'ha': f"🌡️ Gargadin Yanayi don {location}:\\n\\nZafin jiki: {temp}°C\\nYanayi: {condition}\\n\\nKu kiyaye kanku da shuke-shukenku!",
                'yo': f"🌡️ Ikilọ Oju Ojo fun {location}:\\n\\nIgbona: {temp}°C\\nIpo: {condition}\\n\\nE daabobo ara yin ati awon eweko yin!",
                'ig': f"🌡️ Ọkwa Ihu Igwe maka {location}:\\n\\nOkpomoku: {temp}°C\\nỌnọdụ: {condition}\\n\\nChebenu onwe unu na ihe ọkụkụ unu!"
            }
            
            return templates.get(language, templates['en'])
            
        except Exception as e:
            self.logger.error(f"Error formatting weather alert: {str(e)}")
            return "Weather alert formatting error"
    
    def _format_market_update(self, market_data: Dict[str, Any], language: str) -> str:
        """Format market update message"""
        try:
            updates = []
            for crop, price in market_data.items():
                updates.append(f"{crop}: ₦{price:,}")
            
            price_list = "\\n".join(updates)
            
            templates = {
                'en': f"💰 Today's Market Prices:\\n\\n{price_list}\\n\\nPrices may vary by location. Contact your local market for exact rates.",
                'ha': f"💰 Farashin Kasuwa na Yau:\\n\\n{price_list}\\n\\nFarashi na iya bambanta bisa ga wuri. Tuntuɓi kasuwarka don farashi na ainihi.",
                'yo': f"💰 Awon Owo Oja Oni:\\n\\n{price_list}\\n\\nAwon owo le yato si ipọsi. Kan si oja agbegbe rẹ fun awon owo gangan.",
                'ig': f"💰 Ọnụahịa Ahịa Taa:\\n\\n{price_list}\\n\\nỌnụahịa nwere ike ịdị iche site na ebe. Kpọtụrụ ahịa gị maka ọnụahịa ziri ezi."
            }
            
            return templates.get(language, templates['en'])
            
        except Exception as e:
            self.logger.error(f"Error formatting market update: {str(e)}")
            return "Market update formatting error"
    
    def _format_pest_alert(self, pest_data: Dict[str, Any], language: str) -> str:
        """Format pest alert message"""
        try:
            pest_name = pest_data.get('name', 'Unknown pest')
            crop_affected = pest_data.get('crop', 'crops')
            treatment = pest_data.get('treatment', 'Contact extension officer')
            
            templates = {
                'en': f"🐛 Pest Alert: {pest_name}\\n\\nAffected crop: {crop_affected}\\nRecommended treatment: {treatment}\\n\\nAct quickly to prevent spread!",
                'ha': f"🐛 Gargadin Kwari: {pest_name}\\n\\nShukan da abin ya shafa: {crop_affected}\\nMaganin da aka ba da shawara: {treatment}\\n\\nKu yi sauri don hana yaduwa!",
                'yo': f"🐛 Ikilọ Kokoro: {pest_name}\\n\\nEweko ti o kan: {crop_affected}\\nItọju ti a gba niyanju: {treatment}\\n\\nYara lati fi dena kaakiri!",
                'ig': f"🐛 Ọkwa Ụmụ Ahụhụ: {pest_name}\\n\\nIhe ọkụkụ emetụtara: {crop_affected}\\nỌgwụgwọ a tụrụ aro: {treatment}\\n\\nMee ngwa ngwa iji gbochie mgbasa!"
            }
            
            return templates.get(language, templates['en'])
            
        except Exception as e:
            self.logger.error(f"Error formatting pest alert: {str(e)}")
            return "Pest alert formatting error"
    
    def _process_with_ai(self, from_number: str, text: str, language: str, user_name: str):
        """Process message with AI engine (placeholder for integration)"""
        try:
            # This would integrate with the main AI engine
            # For now, send a simple response
            response_text = {
                'en': "Thank you for your message. Our AI is processing your request...",
                'ha': "Na gode da saƙonku. AI ɗinmu yana sarrafa bukatarku...",
                'yo': "O se fun ifiranṣẹ rẹ. AI wa n ṣe ibeere rẹ...",
                'ig': "Daalụ maka ozi gị. AI anyị na-ahazi arịrịọ gị...",
                'ff': "A jaraama e ɓatakuuje maa. AI amen ena huutora naamnade maa..."
            }
            
            message = {
                "messaging_product": "whatsapp",
                "to": from_number,
                "type": "text",
                "text": {
                    "body": response_text.get(language, response_text['en'])
                }
            }
            
            self._send_message(message)
            
        except Exception as e:
            self.logger.error(f"Error processing with AI: {str(e)}")
    
    def get_user_profile(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Get user profile information"""
        try:
            url = f"{self.base_url}/{phone_number}"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user profile: {str(e)}")
            return None