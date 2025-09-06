"""
AgriSense AI - SMS Integration
Advanced SMS messaging for farmer communication via Africa's Talking
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import africastalking

class SMSIntegration:
    """SMS integration using Africa's Talking API"""
    
    def __init__(self, api_key: str, username: str = 'sandbox'):
        self.api_key = api_key
        self.username = username
        self.logger = logging.getLogger(__name__)
        
        # Initialize Africa's Talking
        try:
            africastalking.initialize(username, api_key)
            self.sms_service = africastalking.SMS
            self.logger.info("Africa's Talking SMS service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Africa's Talking: {str(e)}")
            self.sms_service = None
        
        # SMS templates for different languages
        self.sms_templates = {
            'weather_alert': {
                'en': "🌤️ AgriSense Weather Alert for {location}:\nTemp: {temp}°C\nCondition: {condition}\nAdvice: {advice}",
                'ha': "🌤️ Gargadin Yanayi na AgriSense don {location}:\nZafin jiki: {temp}°C\nYanayi: {condition}\nShawara: {advice}",
                'yo': "🌤️ Ikilọ Oju Ojo AgriSense fun {location}:\nIgbona: {temp}°C\nIpo: {condition}\nImoran: {advice}",
                'ig': "🌤️ Ọkwa Ihu Igwe AgriSense maka {location}:\nOkpomoku: {temp}°C\nỌnọdụ: {condition}\nNdụmọdụ: {advice}"
            },
            'market_update': {
                'en': "💰 AgriSense Market Update:\n{crops}\nUpdated: {timestamp}\nFor more info, chat with us!",
                'ha': "💰 Sabuntawar Kasuwa na AgriSense:\n{crops}\nAn sabunta: {timestamp}\nDon ƙarin bayani, yi hira da mu!",
                'yo': "💰 Imudojuiwon Oja AgriSense:\n{crops}\nTi se imudojuiwon: {timestamp}\nFun alaye siwaju, ba wa sọrọ!",
                'ig': "💰 Mmelite Ahịa AgriSense:\n{crops}\nEmelitere: {timestamp}\nMaka ozi ndị ọzọ, kwurịta okwu na anyị!"
            },
            'pest_alert': {
                'en': "🐛 AgriSense Pest Alert:\nPest: {pest_name}\nCrop: {crop}\nTreatment: {treatment}\nAct fast to prevent spread!",
                'ha': "🐛 Gargadin Kwari na AgriSense:\nKwari: {pest_name}\nShuki: {crop}\nMagani: {treatment}\nKu yi sauri don hana yaduwa!",
                'yo': "🐛 Ikilọ Kokoro AgriSense:\nKokoro: {pest_name}\nEweko: {crop}\nItọju: {treatment}\nYara lati fi dena kaakiri!",
                'ig': "🐛 Ọkwa Ụmụ Ahụhụ AgriSense:\nỤmụ ahụhụ: {pest_name}\nIhe ọkụkụ: {crop}\nỌgwụgwọ: {treatment}\nMee ngwa ngwa iji gbochie mgbasa!"
            },
            'welcome': {
                'en': "Welcome to AgriSense AI! 🌾\nYour smart farming assistant is ready. Reply with questions about crops, weather, or markets. Start with 'HELP' for options.",
                'ha': "Barka da zuwa AgriSense AI! 🌾\nMai taimako na noma mai hankali yana shirye. Amsa da tambayoyi game da shuke-shuke, yanayi, ko kasuwanni. Fara da 'TAIMAKO' don zaɓuɓɓuka.",
                'yo': "Kaabo si AgriSense AI! 🌾\nOluranlọwọ agbẹ ọlọgbọn rẹ ti ṣetan. Dahun pẹlu awọn ibeere nipa eweko, oju ojo, tabi awọn oja. Bẹrẹ pẹlu 'IRANLỌWỌ' fun awọn aṣayan.",
                'ig': "Nnọọ na AgriSense AI! 🌾\nOnye inyeaka ọrụ ugbo amamihe gị adịla njikere. Zaghachi na ajụjụ gbasara ihe ọkụkụ, ihu igwe, ma ọ bụ ahịa. Malite na 'ENYEMAKA' maka nhọrọ."
            },
            'help_menu': {
                'en': "AgriSense AI Commands:\n1. WEATHER [location] - Get weather info\n2. CROP [crop name] - Crop advice\n3. MARKET [crop] - Current prices\n4. PEST [description] - Pest help\n5. CHAT - Start conversation\n\nReply with any command!",
                'ha': "Umarnin AgriSense AI:\n1. YANAYI [wuri] - Samun bayanan yanayi\n2. SHUKI [sunan shuki] - Shawarar shuki\n3. KASUWA [shuki] - Farashin yanzu\n4. KWARI [bayanin] - Taimakon kwari\n5. HIRA - Fara hira\n\nAmsa da kowane umarni!",
                'yo': "Awọn Aṣẹ AgriSense AI:\n1. OJU OJO [ipo] - Gba alaye oju ojo\n2. EWEKO [orukọ eweko] - Imọran eweko\n3. OJA [eweko] - Awọn idiyele lọwọlọwọ\n4. KOKORO [apejuwe] - Iranlọwọ kokoro\n5. IBARAẸNISỌRỌ - Bẹrẹ ibaraẹnisọrọ\n\nDahun pẹlu eyikeyi aṣẹ!",
                'ig': "Iwu AgriSense AI:\n1. IHU IGWE [ebe] - Nweta ozi ihu igwe\n2. IHE ỌKỤKỤ [aha ihe ọkụkụ] - Ndụmọdụ ihe ọkụkụ\n3. AHỊA [ihe ọkụkụ] - Ọnụahịa ugbu a\n4. ỤMỤ AHỤHỤ [nkọwa] - Enyemaka ụmụ ahụhụ\n5. MKPARỊTA UKA - Malite mkparịta uka\n\nZaghachi na iwu ọ bụla!"
            }
        }
        
        # Command handlers
        self.command_handlers = {
            'weather': self._handle_weather_command,
            'yanayi': self._handle_weather_command,
            'oju ojo': self._handle_weather_command,
            'ihu igwe': self._handle_weather_command,
            'crop': self._handle_crop_command,
            'shuki': self._handle_crop_command,
            'eweko': self._handle_crop_command,
            'ihe okuku': self._handle_crop_command,
            'market': self._handle_market_command,
            'kasuwa': self._handle_market_command,
            'oja': self._handle_market_command,
            'ahia': self._handle_market_command,
            'pest': self._handle_pest_command,
            'kwari': self._handle_pest_command,
            'kokoro': self._handle_pest_command,
            'umu ahuhu': self._handle_pest_command,
            'help': self._handle_help_command,
            'taimako': self._handle_help_command,
            'iranlowo': self._handle_help_command,
            'enyemaka': self._handle_help_command
        }
    
    def send_sms(self, phone_number: str, message: str, sender_id: str = "AgriSense") -> Dict[str, Any]:
        """Send SMS message to a phone number"""
        try:
            if not self.sms_service:
                return {'success': False, 'error': 'SMS service not initialized'}
            
            # Format phone number
            formatted_number = self._format_phone_number(phone_number)
            
            # Send SMS
            response = self.sms_service.send(message, [formatted_number], sender_id)
            
            # Parse response
            if response['SMSMessageData']['Recipients']:
                recipient = response['SMSMessageData']['Recipients'][0]
                if recipient['status'] == 'Success':
                    self.logger.info(f"SMS sent successfully to {phone_number}")
                    return {
                        'success': True,
                        'message_id': recipient.get('messageId'),
                        'cost': recipient.get('cost'),
                        'status': recipient['status']
                    }
                else:
                    self.logger.error(f"SMS failed to {phone_number}: {recipient['status']}")
                    return {
                        'success': False,
                        'error': recipient['status']
                    }
            else:
                return {'success': False, 'error': 'No recipients found in response'}
                
        except Exception as e:
            self.logger.error(f"Error sending SMS to {phone_number}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_bulk_sms(self, phone_numbers: List[str], message: str, sender_id: str = "AgriSense") -> Dict[str, Any]:
        """Send SMS to multiple phone numbers"""
        try:
            if not self.sms_service:
                return {'success': False, 'error': 'SMS service not initialized'}
            
            # Format phone numbers
            formatted_numbers = [self._format_phone_number(num) for num in phone_numbers]
            
            # Send bulk SMS
            response = self.sms_service.send(message, formatted_numbers, sender_id)
            
            # Parse response
            results = {
                'success': True,
                'total_sent': 0,
                'total_failed': 0,
                'results': []
            }
            
            if response['SMSMessageData']['Recipients']:
                for recipient in response['SMSMessageData']['Recipients']:
                    if recipient['status'] == 'Success':
                        results['total_sent'] += 1
                    else:
                        results['total_failed'] += 1
                    
                    results['results'].append({
                        'phone': recipient['number'],
                        'status': recipient['status'],
                        'message_id': recipient.get('messageId'),
                        'cost': recipient.get('cost')
                    })
            
            self.logger.info(f"Bulk SMS: {results['total_sent']} sent, {results['total_failed']} failed")
            return results
            
        except Exception as e:
            self.logger.error(f"Error sending bulk SMS: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_incoming_sms(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Handle incoming SMS messages"""
        try:
            # Detect language
            language = self._detect_language(message)
            
            # Parse command
            command, params = self._parse_command(message)
            
            # Handle command
            if command in self.command_handlers:
                response_message = self.command_handlers[command](params, language, phone_number)
            else:
                # Default to chat mode
                response_message = self._handle_chat_message(message, language, phone_number)
            
            # Send response
            result = self.send_sms(phone_number, response_message)
            
            return {
                'success': True,
                'command': command,
                'language': language,
                'response_sent': result['success']
            }
            
        except Exception as e:
            self.logger.error(f"Error handling incoming SMS from {phone_number}: {str(e)}")
            # Send error message
            error_msg = self._get_error_message(self._detect_language(message))
            self.send_sms(phone_number, error_msg)
            return {'success': False, 'error': str(e)}
    
    def send_weather_alert(self, phone_numbers: List[str], weather_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Send weather alert SMS"""
        try:
            template = self.sms_templates['weather_alert'][language]
            message = template.format(
                location=weather_data.get('location', 'your area'),
                temp=weather_data.get('temperature', {}).get('current', 'N/A'),
                condition=weather_data.get('weather', {}).get('description', 'Unknown'),
                advice=weather_data.get('advice', 'Monitor conditions')
            )
            
            return self.send_bulk_sms(phone_numbers, message)
            
        except Exception as e:
            self.logger.error(f"Error sending weather alerts: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_market_update(self, phone_numbers: List[str], market_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Send market price update SMS"""
        try:
            # Format crop prices
            crop_list = []
            for crop, price in market_data.items():
                crop_list.append(f"{crop}: ₦{price:,}")
            
            crops_text = "\n".join(crop_list)
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            template = self.sms_templates['market_update'][language]
            message = template.format(
                crops=crops_text,
                timestamp=timestamp
            )
            
            return self.send_bulk_sms(phone_numbers, message)
            
        except Exception as e:
            self.logger.error(f"Error sending market updates: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_pest_alert(self, phone_numbers: List[str], pest_data: Dict[str, Any], language: str = 'en') -> Dict[str, Any]:
        """Send pest alert SMS"""
        try:
            template = self.sms_templates['pest_alert'][language]
            message = template.format(
                pest_name=pest_data.get('name', 'Unknown pest'),
                crop=pest_data.get('crop', 'crops'),
                treatment=pest_data.get('treatment', 'Contact extension officer')
            )
            
            return self.send_bulk_sms(phone_numbers, message)
            
        except Exception as e:
            self.logger.error(f"Error sending pest alerts: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _format_phone_number(self, phone_number: str) -> str:
        """Format phone number for Africa's Talking"""
        # Remove any non-digit characters except +
        cleaned = ''.join(char for char in phone_number if char.isdigit() or char == '+')
        
        # Add country code if missing
        if not cleaned.startswith('+'):
            if cleaned.startswith('0'):
                cleaned = '+234' + cleaned[1:]
            elif not cleaned.startswith('234'):
                cleaned = '+234' + cleaned
            else:
                cleaned = '+' + cleaned
        
        return cleaned
    
    def _detect_language(self, text: str) -> str:
        """Simple language detection for SMS"""
        text_lower = text.lower()
        
        # Hausa indicators
        hausa_words = ['sannu', 'yanayi', 'shuki', 'kasuwa', 'kwari', 'taimako']
        if any(word in text_lower for word in hausa_words):
            return 'ha'
        
        # Yoruba indicators
        yoruba_words = ['bawo', 'oju ojo', 'eweko', 'oja', 'kokoro', 'iranlowo']
        if any(word in text_lower for word in yoruba_words):
            return 'yo'
        
        # Igbo indicators
        igbo_words = ['ndewo', 'ihu igwe', 'ihe okuku', 'ahia', 'umu ahuhu', 'enyemaka']
        if any(word in text_lower for word in igbo_words):
            return 'ig'
        
        # Default to English
        return 'en'
    
    def _parse_command(self, message: str) -> tuple:
        """Parse SMS command and parameters"""
        words = message.strip().split()
        if not words:
            return 'chat', []
        
        command = words[0].lower()
        params = words[1:] if len(words) > 1 else []
        
        return command, params
    
    def _handle_weather_command(self, params: List[str], language: str, phone_number: str) -> str:
        """Handle weather command"""
        location = ' '.join(params) if params else 'your location'
        
        responses = {
            'en': f"Weather info for {location}: Partly cloudy, 28°C. Good for farming activities. For detailed forecast, chat with us online!",
            'ha': f"Bayanan yanayi na {location}: Gizagizai kadan, 28°C. Yana da kyau don ayyukan noma. Don cikakkun bayanai, yi hira da mu ta yanar gizo!",
            'yo': f"Alaye oju ojo fun {location}: Awọsanma diẹ, 28°C. O dara fun awọn iṣẹ agbẹ. Fun asọtẹlẹ kikun, ba wa sọrọ lori ayelujara!",
            'ig': f"Ozi ihu igwe maka {location}: Igwe ojii ntakịrị, 28°C. Ọ dị mma maka ọrụ ugbo. Maka amụma zuru ezu, kwurịta okwu na anyị na ịntanetị!"
        }
        
        return responses.get(language, responses['en'])
    
    def _handle_crop_command(self, params: List[str], language: str, phone_number: str) -> str:
        """Handle crop advice command"""
        crop = ' '.join(params) if params else 'your crop'
        
        responses = {
            'en': f"For {crop}: Ensure good drainage, apply fertilizer as needed, monitor for pests. For detailed advice, visit our platform!",
            'ha': f"Don {crop}: Tabbatar da magudanar ruwa, yi amfani da taki idan akwai bukatu, lura da kwari. Don cikakken shawara, ziyarci dandalin mu!",
            'yo': f"Fun {crop}: Rii daju pe omi le jade, lo ajile bi o ṣe ye, ṣe abojuto kokoro. Fun imọran kikun, ṣabẹwo si ẹrọ wa!",
            'ig': f"Maka {crop}: Hụ na mmiri na-asọ nke ọma, tinye fatịlaịza dị ka ọ dị mkpa, nyochaa ụmụ ahụhụ. Maka ndụmọdụ zuru ezu, gaa na ikpo okwu anyị!"
        }
        
        return responses.get(language, responses['en'])
    
    def _handle_market_command(self, params: List[str], language: str, phone_number: str) -> str:
        """Handle market price command"""
        crop = ' '.join(params) if params else 'crops'
        
        responses = {
            'en': f"Current {crop} prices: Rice ₦30,000/bag, Maize ₦25,000/bag. Prices vary by location. For live updates, check our platform!",
            'ha': f"Farashin {crop} na yanzu: Shinkafa ₦30,000/buhun, Masara ₦25,000/buhun. Farashi ya bambanta bisa wuri. Don sabuntawa kai tsaye, duba dandalinmu!",
            'yo': f"Awọn idiyele {crop} lọwọlọwọ: Iresi ₦30,000/apo, Agbado ₦25,000/apo. Awọn idiyele yatọ nipasẹ ipo. Fun awọn imudojuiwon alààyè, ṣayẹwo ẹrọ wa!",
            'ig': f"Ọnụahịa {crop} ugbu a: Osikapa ₦30,000/akpa, Ọka ₦25,000/akpa. Ọnụahịa dị iche site na ebe. Maka mmelite ndụ, lelee ikpo okwu anyị!"
        }
        
        return responses.get(language, responses['en'])
    
    def _handle_pest_command(self, params: List[str], language: str, phone_number: str) -> str:
        """Handle pest control command"""
        pest_description = ' '.join(params) if params else 'pests'
        
        responses = {
            'en': f"For pest control ({pest_description}): Use neem oil spray, practice crop rotation, remove infected plants. For specific treatment, consult our AI!",
            'ha': f"Don shawo da kwari ({pest_description}): Yi amfani da man neem, yi juyawa na shuke-shuke, cire shuke masu cuta. Don takamaiman magani, tuntuɓi AI ɗinmu!",
            'yo': f"Fun ijakadi kokoro ({pest_description}): Lo omi epo neem, ṣe iyipada gbigbin, yọ awọn eweko ti aisan ba. Fun itọju pato, kan si AI wa!",
            'ig': f"Maka nchịkwa ụmụ ahụhụ ({pest_description}): Jiri mmiri mmanụ neem fesa, mee mgbanwe ịkụ ihe, wepụ osisi ndị rịara ọrịa. Maka ọgwụgwọ kpọmkwem, kpọtụrụ AI anyị!"
        }
        
        return responses.get(language, responses['en'])
    
    def _handle_help_command(self, params: List[str], language: str, phone_number: str) -> str:
        """Handle help command"""
        return self.sms_templates['help_menu'][language]
    
    def _handle_chat_message(self, message: str, language: str, phone_number: str) -> str:
        """Handle general chat message"""
        # This would typically integrate with the main AI engine
        responses = {
            'en': "Thanks for your message! For detailed farming advice, visit our platform or call +234-912-645-1938. Reply 'HELP' for commands.",
            'ha': "Na gode da saƙonku! Don cikakkun shawarwarin noma, ziyarci dandalinmu ko a kira +234-912-645-1938. Amsa 'TAIMAKO' don umarnin.",
            'yo': "O ṣe fun ifiranṣẹ rẹ! Fun imọran agbẹ kikun, ṣabẹwo si ẹrọ wa tabi pe +234-912-645-1938. Dahun 'IRANLỌWỌ' fun awọn aṣẹ.",
            'ig': "Daalụ maka ozi gị! Maka ndụmọdụ ọrụ ugbo zuru ezu, gaa na ikpo okwu anyị ma ọ bụ kpọọ +234-912-645-1938. Zaghachi 'ENYEMAKA' maka iwu."
        }
        
        return responses.get(language, responses['en'])
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in appropriate language"""
        messages = {
            'en': "Sorry, there was an error processing your request. Please try again or reply 'HELP' for assistance.",
            'ha': "Yi hakuri, an sami kuskure wajen sarrafa bukatarku. Ka sake gwadawa ko amsa 'TAIMAKO' don taimako.",
            'yo': "Ma binu, aṣiṣe kan wa nigba ṣiṣe ibeere rẹ. Jọwọ gbiyanju tabi dahun 'IRANLỌWỌ' fun iranlọwọ.",
            'ig': "Ndo, enwere mmejọ n'ịhazi arịrịọ gị. Biko nwaa ọzọ ma ọ bụ zaghachi 'ENYEMAKA' maka enyemaka."
        }
        
        return messages.get(language, messages['en'])
    
    def get_sms_status(self, message_id: str) -> Dict[str, Any]:
        """Get delivery status of an SMS"""
        try:
            # This would query Africa's Talking delivery reports API
            # For now, return a placeholder
            return {
                'message_id': message_id,
                'status': 'delivered',
                'delivered_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting SMS status: {str(e)}")
            return {'error': str(e)}
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Get SMS account balance"""
        try:
            if not self.sms_service:
                return {'error': 'SMS service not initialized'}
            
            # Get account balance (if available in Africa's Talking SDK)
            # For now, return placeholder
            return {
                'balance': 'USD 50.00',
                'currency': 'USD'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting account balance: {str(e)}")
            return {'error': str(e)}