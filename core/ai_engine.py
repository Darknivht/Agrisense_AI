"""
AgriSense AI - Core AI Engine
Advanced Agricultural Intelligence with Multi-language Support
"""

import os
import json
import openai
from anthropic import Anthropic
import google.generativeai as genai
import requests
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

class AgriSenseAI:
    """Advanced AI engine for agricultural assistance"""
    
    def __init__(self):
        # Initialize AI clients
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY')) if os.getenv('OPENAI_API_KEY') else None
        self.anthropic_client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')) if os.getenv('ANTHROPIC_API_KEY') else None
        
        # Initialize Gemini
        if os.getenv('GEMINI_API_KEY'):
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
            
        # OpenRouter configuration
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        self.openrouter_base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        self.logger = logging.getLogger(__name__)
        
        # Default AI provider
        self.default_provider = os.getenv('DEFAULT_AI_PROVIDER', 'openai')
        
        # Agricultural knowledge base
        self.agricultural_knowledge = self._load_agricultural_knowledge()
        
        # Language-specific prompts
        self.system_prompts = {
            'en': self._get_english_system_prompt(),
            'ha': self._get_hausa_system_prompt(),
            'yo': self._get_yoruba_system_prompt(),
            'ig': self._get_igbo_system_prompt(),
            'ff': self._get_fulfulde_system_prompt()
        }
        
        # Available AI providers
        self.available_providers = self._get_available_providers()
    
    def _load_agricultural_knowledge(self) -> Dict[str, Any]:
        """Load comprehensive agricultural knowledge base"""
        return {
            'crops': {
                'rice': {
                    'planting_season': ['May', 'June', 'July'],
                    'harvest_time': '90-120 days',
                    'water_needs': 'High - 1000-1300mm annually',
                    'common_pests': ['Rice weevil', 'Stem borer', 'Blast disease'],
                    'fertilizer': 'NPK 15-15-15 at planting, Urea top-dressing',
                    'market_price_range': '₦25,000-₦35,000 per bag'
                },
                'maize': {
                    'planting_season': ['April', 'May', 'June'],
                    'harvest_time': '75-90 days',
                    'water_needs': 'Moderate - 500-800mm annually',
                    'common_pests': ['Fall armyworm', 'Stem borer', 'Ear rot'],
                    'fertilizer': 'NPK 20-10-10 at planting, Urea at 6 weeks',
                    'market_price_range': '₦20,000-₦28,000 per bag'
                },
                'tomato': {
                    'planting_season': ['October', 'November', 'February', 'March'],
                    'harvest_time': '60-80 days',
                    'water_needs': 'High - daily irrigation during dry season',
                    'common_pests': ['Whitefly', 'Aphids', 'Late blight'],
                    'fertilizer': 'NPK 15-15-15 weekly, Calcium foliar spray',
                    'market_price_range': '₦30,000-₦50,000 per ton'
                },
                'cassava': {
                    'planting_season': ['April', 'May', 'June'],
                    'harvest_time': '8-12 months',
                    'water_needs': 'Low-moderate - drought tolerant',
                    'common_pests': ['Cassava mosaic virus', 'Mealybug', 'Green mite'],
                    'fertilizer': 'NPK 12-12-17 at planting and 6 months',
                    'market_price_range': '₦15,000-₦25,000 per ton'
                }
            },
            'weather_advice': {
                'hot_weather': {
                    'en': 'Water crops early morning and evening. Use mulching to retain moisture.',
                    'ha': 'Shayar da shukoki da safe da maraice. Yi amfani da ciyawa don kiyaye danshi.',
                    'yo': 'Fi omi si eweko ni kutukutu ati alẹ. Lo korikori lati pa omi mọ.',
                    'ig': 'Gbanye ihe ọkụkụ n\'ụtụtụ na mgbede. Jiri ahịhịa chebe mmiri.',
                    'ff': 'Jiyitin naabaaji subaka e fiɗɗe. Huutoro reedu ngam mooftude ndiyam.'
                },
                'rainy_season': {
                    'en': 'Ensure proper drainage. Watch for fungal diseases. Apply fungicide if needed.',
                    'ha': 'Tabbatar da magudanar ruwa. Kula da cututtukan fungi. Yi amfani da maganin fungi idan akwai bukatu.',
                    'yo': 'Rii daju pe omi le jade. Wo arun elu. Lo egboogi ti o ba nilo.',
                    'ig': 'Hụ na mmiri na-asọ nke ọma. Lelee ọrịa fungal. Jiri ọgwụ fungal ma ọ bụrụ na ọ dị mkpa.',
                    'ff': 'Ƴeew no ngoppi ndiyam. Yiilo naange fungal. Huutoro ganndal fungi so haani.'
                }
            },
            'pest_management': {
                'organic_solutions': {
                    'neem_spray': 'Mix neem oil with liquid soap and water. Spray in evening.',
                    'garlic_spray': 'Blend garlic with water, strain and spray on affected plants.',
                    'companion_planting': 'Plant marigold, basil, and mint around crops to deter pests.'
                },
                'chemical_solutions': {
                    'aphids': 'Imidacloprid 200SL - 1ml per liter of water',
                    'caterpillars': 'Cypermethrin 25EC - 2ml per liter of water',
                    'fungal_diseases': 'Copper oxychloride 50WP - 3g per liter of water'
                }
            },
            'market_insights': {
                'price_factors': [
                    'Seasonal demand and supply',
                    'Weather conditions affecting harvest',
                    'Transportation costs',
                    'Storage and processing capacity',
                    'Export demand and government policies'
                ],
                'marketing_tips': [
                    'Form farmer cooperatives for better pricing',
                    'Direct sales to consumers through markets',
                    'Value addition through processing',
                    'Contract farming with reliable buyers'
                ]
            }
        }
    
    def _get_english_system_prompt(self) -> str:
        return """You are AgriSense AI, an advanced agricultural intelligence assistant specialized in Nigerian farming. 
        
        Your expertise includes:
        - Crop cultivation and management
        - Pest and disease identification and treatment
        - Weather-based farming advice
        - Market price analysis and trends
        - Sustainable farming practices
        - Soil health and fertilization
        - Water management and irrigation
        - Post-harvest handling and storage
        
        Provide practical, actionable advice based on:
        - Local Nigerian farming conditions
        - Seasonal patterns and weather
        - Available resources and budget constraints
        - Sustainable and eco-friendly practices
        
        Always be encouraging and supportive. Explain technical concepts in simple terms.
        Suggest both traditional and modern solutions when appropriate."""
    
    def _get_hausa_system_prompt(self) -> str:
        return """Kai AgriSense AI ne, mai taimako na aikin noma na Najeriya.
        
        Gwaninta ya hada da:
        - Noman amfanin gona da kula da su
        - Gane da magance kwari da cututtuka
        - Shawara dangane da yanayi
        - Nazarin farashin kasuwa
        - Hanyoyin noma masu dorewa
        - Lafiyar kasa da taki
        - Sarrafa ruwa da ban ruwa
        - Kula da amfanin gona bayan girbi
        
        Ka bayar da shawara mai amfani bisa ga:
        - Yanayin noma na Najeriya
        - Tsarin yanayi da lokaci
        - Kayan aiki da kudade
        - Hanyoyin da ba su lalata muhalli ba
        
        Kasance mai karfafawa koyaushe. Bayyana batutuwa masu wuyar fahimta a saukin harshe."""
    
    def _get_yoruba_system_prompt(self) -> str:
        return """Iwọ ni AgriSense AI, oluranlọwọ agbẹ to ni imọ jinlẹ nipa ise agbẹ ni Nigeria.
        
        Imọ rẹ ni:
        - Gbingbin ati itọju eweko
        - Dida kokoro ati aisan mo pelu itọju wọn
        - Imọran ti o da lori oju ojo
        - Itupalẹ owo oja
        - Awọn ọna agbẹ amunisin
        - Ilera ile ati ajile
        - Isakoso omi ati irrigation
        - Itọju lẹhin ikore
        
        Fun ni imọran to wulo ti o da lori:
        - Ipo agbẹ Nigeria
        - Awọn akoko ojo ati igba
        - Ohun elo to wa ati owo
        - Awọn ọna to dara fun ayika
        
        Ma gba ni niyanju nigbagbogbo. Ṣalaye awọn ọrọ to nira ni ọna ti o rọrun."""
    
    def _get_igbo_system_prompt(self) -> str:
        return """Ị bụ AgriSense AI, onyeinyeaka ọrụ ugbo nke nwere ọmụma miri emi banyere ọrụ ugbo na Naịjirịa.
        
        Nka gị gụnyere:
        - Ịkụ na ilekọta ihe ọkụkụ
        - Ịchọpụta na ọgwụgwọ ụmụ ahụhụ na ọrịa
        - Ndụmọdụ dabere na ihu igwe
        - Nyocha ọnụahịa ahịa
        - Ụzọ ọrụ ugbo na-adịgide adịgide
        - Ahụike ala na fatịlaịza
        - Njikwa mmiri na ogbugba mmiri
        - Nlekọta mgbe owuwe ihe ọkụkụ gasịrị
        
        Nye ndụmọdụ bara uru dabere na:
        - Ọnọdụ ọrụ ugbo Naịjirịa
        - Usoro oge na ihu igwe
        - Ihe ndị dị na ego
        - Ụzọ ndị na-emeghị ka gburugburu ebe obibi mebịa
        
        Gbalịa ime ka mmadụ nwee obi ụtọ mgbe niile. Kọwaa okwu ndị siri ike n'ụzọ dị mfe."""
    
    def _get_fulfulde_system_prompt(self) -> str:
        return """A ni AgriSense AI, wallitorde gooto ɗuuɗal wuurnde e Naajeeriya mo heewi fuu.
        
        Anndal maa ena ena:
        - Horiinde e ƴellitaade jiiwugol
        - Anndinde e cukkital marawle e nǧaange
        - Waɗaade e kawral jemma
        - Jokkondirgal keewɗe luumo
        - Jaŋde wuurnde ngannduɗe
        - Laabu leydi e takka
        - Lawal ndiyam e jarɗe
        - Teelal ɓannge hoore mbaɗi
        
        Hokku waɗaade moƴƴude e:
        - Ngonka wuurnde Naajeeriya
        - Jaŋde jemma e junngooji
        - Kuuɗe e jaawi
        - Laawol wasaa darnde kala
        
        Yiiltu heen jaaynde kaa e sahaa. Faamto konngol maɓɓe e laawol heɗo."""
    
    def _get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available AI providers with their status and models"""
        providers = []
        
        if self.openai_client:
            providers.append({
                'id': 'openai',
                'name': 'OpenAI',
                'status': 'available',
                'description': 'Advanced language models with excellent reasoning',
                'models': [
                    {'id': 'gpt-4', 'name': 'GPT-4', 'description': 'Most advanced model (Premium)', 'cost': 'High'},
                    {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'Faster GPT-4 variant', 'cost': 'High'},
                    {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Fast and efficient', 'cost': 'Low'}
                ],
                'default_model': 'gpt-4'
            })
            
        if self.anthropic_client:
            providers.append({
                'id': 'anthropic',
                'name': 'Anthropic',
                'status': 'available',
                'description': 'Helpful, harmless, and honest AI assistant',
                'models': [
                    {'id': 'claude-3-opus', 'name': 'Claude 3 Opus', 'description': 'Most powerful Claude model', 'cost': 'High'},
                    {'id': 'claude-3-sonnet', 'name': 'Claude 3 Sonnet', 'description': 'Balanced performance and speed', 'cost': 'Medium'},
                    {'id': 'claude-3-haiku', 'name': 'Claude 3 Haiku', 'description': 'Fast and efficient', 'cost': 'Low'}
                ],
                'default_model': 'claude-3-sonnet'
            })
            
        if self.openrouter_api_key:
            providers.append({
                'id': 'openrouter',
                'name': 'OpenRouter',
                'status': 'available',
                'description': 'Access to multiple AI models through OpenRouter',
                'models': [
                    # Free Models
                    {'id': 'openai/gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Fast OpenAI model', 'cost': 'Free', 'category': 'free'},
                    {'id': 'microsoft/wizardlm-2-8x22b', 'name': 'WizardLM 2 8x22B', 'description': 'Microsoft\'s advanced model', 'cost': 'Free', 'category': 'free'},
                    {'id': 'meta-llama/llama-3-8b-instruct', 'name': 'Llama 3 8B', 'description': 'Meta\'s efficient model', 'cost': 'Free', 'category': 'free'},
                    {'id': 'mistralai/mistral-7b-instruct', 'name': 'Mistral 7B', 'description': 'Fast and efficient', 'cost': 'Free', 'category': 'free'},
                    {'id': 'huggingface/zephyr-7b-beta', 'name': 'Zephyr 7B', 'description': 'Fine-tuned for chat', 'cost': 'Free', 'category': 'free'},
                    
                    # Premium Models
                    {'id': 'openai/gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'Advanced OpenAI model', 'cost': 'High', 'category': 'premium'},
                    {'id': 'anthropic/claude-3-opus', 'name': 'Claude 3 Opus', 'description': 'Anthropic\'s most powerful', 'cost': 'High', 'category': 'premium'},
                    {'id': 'google/gemini-pro', 'name': 'Gemini Pro', 'description': 'Google\'s advanced model', 'cost': 'Medium', 'category': 'premium'}
                ],
                'default_model': 'meta-llama/llama-3-8b-instruct'
            })
            
        if self.gemini_model:
            providers.append({
                'id': 'gemini',
                'name': 'Google Gemini',
                'status': 'available',
                'description': 'Google\'s multimodal AI with strong reasoning capabilities',
                'models': [
                    {'id': 'gemini-pro', 'name': 'Gemini Pro', 'description': 'Advanced multimodal model', 'cost': 'Medium'},
                    {'id': 'gemini-pro-vision', 'name': 'Gemini Pro Vision', 'description': 'Multimodal with vision', 'cost': 'Medium'}
                ],
                'default_model': 'gemini-pro'
            })
            
        if not providers:
            providers.append({
                'id': 'fallback',
                'name': 'Rule-based System',
                'status': 'available',
                'description': 'Basic agricultural knowledge system',
                'models': [
                    {'id': 'basic', 'name': 'Basic Rules', 'description': 'Simple agricultural knowledge', 'cost': 'Free'}
                ],
                'default_model': 'basic'
            })
            
        return providers
    
    def generate_response(
        self,
        message: str,
        user_context: Dict[str, Any],
        conversation_context: List[Dict[str, Any]] = None,
        rag_context: List[Dict[str, Any]] = None,
        weather_context: Dict[str, Any] = None,
        language: str = 'en',
        ai_provider: str = None,
        ai_model: str = None
    ) -> Dict[str, Any]:
        """Generate intelligent agricultural response"""
        
        try:
            # Prepare context
            context_parts = []
            
            # Add user context
            context_parts.append(f"User Profile: {user_context.get('name', 'Farmer')} from {user_context.get('location', 'Nigeria')}")
            if user_context.get('farming_interests'):
                context_parts.append(f"Farming interests: {', '.join(user_context['farming_interests'])}")
            
            # Add conversation history
            if conversation_context:
                context_parts.append("Recent conversation:")
                for conv in conversation_context[-3:]:  # Last 3 exchanges
                    context_parts.append(f"User: {conv['message']}")
                    context_parts.append(f"AI: {conv['response']}")
            
            # Add RAG context
            if rag_context:
                context_parts.append("Relevant documents:")
                for doc in rag_context:
                    context_parts.append(f"- {doc.get('content', '')[:200]}...")
            
            # Add weather context
            if weather_context:
                context_parts.append(f"Current weather in {user_context.get('location')}: {weather_context}")
            
            # Prepare messages
            system_prompt = self.system_prompts.get(language, self.system_prompts['en'])
            context_str = "\n".join(context_parts)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{context_str}\n\nUser question: {message}"}
            ]
            
            # Determine which AI provider and model to use
            provider = ai_provider or user_context.get('preferred_ai_provider', self.default_provider)
            model = ai_model or user_context.get('preferred_ai_model')
            
            # Generate response using selected AI service
            response_text = ""
            confidence = 0.8
            used_provider = provider
            used_model = model
            
            response_text, confidence, used_provider, used_model = self._generate_ai_response(messages, provider, model)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(message, language)
            
            return {
                'text': response_text,
                'confidence': confidence,
                'suggestions': suggestions,
                'language': language,
                'ai_provider': used_provider,
                'ai_model': used_model,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AI response generation error: {str(e)}")
            return {
                'text': self._get_error_message(language),
                'confidence': 0.3,
                'suggestions': [],
                'language': language,
                'ai_provider': 'error',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _generate_ai_response(self, messages: List[Dict[str, str]], provider: str, model: str = None) -> tuple[str, float, str, str]:
        """Generate AI response using the specified provider"""
        try:
            if provider == 'openai' and self.openai_client:
                # Use provided model or default
                openai_model = model or "gpt-4"
                
                response = self.openai_client.chat.completions.create(
                    model=openai_model,
                    messages=messages,
                    max_tokens=800,
                    temperature=0.7
                )
                return response.choices[0].message.content, 0.9, 'openai', openai_model
                
            elif provider == 'anthropic' and self.anthropic_client:
                # Use provided model or default
                anthropic_model = model or "claude-3-sonnet-20240229"
                
                response = self.anthropic_client.messages.create(
                    model=anthropic_model,
                    max_tokens=800,
                    messages=messages
                )
                return response.content[0].text, 0.9, 'anthropic', anthropic_model
                
            elif provider == 'openrouter' and self.openrouter_api_key:
                # Use provided model or default
                openrouter_model = model or "meta-llama/llama-3-8b-instruct"
                
                headers = {
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "model": openrouter_model,
                    "messages": messages,
                    "max_tokens": 800,
                    "temperature": 0.7
                }
                
                response = requests.post(self.openrouter_base_url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result['choices'][0]['message']['content'], 0.85, 'openrouter', openrouter_model
                
            elif provider == 'gemini' and self.gemini_model:
                # Use provided model or default
                gemini_model = model or "gemini-pro"
                
                # Convert messages to Gemini format
                prompt = f"{messages[0]['content']}\n\n{messages[1]['content']}"
                response = self.gemini_model.generate_content(prompt)
                return response.text, 0.85, 'gemini', gemini_model
                
            else:
                # Try fallback providers in order
                if self.openai_client:
                    return self._generate_ai_response(messages, 'openai', None)
                elif self.anthropic_client:
                    return self._generate_ai_response(messages, 'anthropic', None)
                elif self.gemini_model:
                    return self._generate_ai_response(messages, 'gemini', None)
                elif self.openrouter_api_key:
                    return self._generate_ai_response(messages, 'openrouter', None)
                else:
                    # Use rule-based fallback
                    return self._generate_fallback_response(messages[1]['content'], 'en', {}), 0.6, 'fallback', 'basic'
                    
        except Exception as e:
            self.logger.error(f"AI provider {provider} error: {str(e)}")
            # Try fallback provider
            if provider != 'fallback':
                return self._generate_ai_response(messages, 'fallback', None)
            else:
                return "Mo tọrọ gafara, ṣugbọn mo ni wahala lati ṣe ibeere rẹ ni bayi. Jọwọ gbiyanju lẹẹkansi.", 0.3, 'error', 'none'
    
    def _generate_fallback_response(self, message: str, language: str, user_context: Dict[str, Any]) -> str:
        """Generate rule-based fallback responses"""
        message_lower = message.lower()
        
        # Weather-related queries
        if any(word in message_lower for word in ['weather', 'rain', 'sun', 'temperature', 'yanayi', 'ruwan sama']):
            return self._get_weather_advice(language)
        
        # Crop-related queries
        for crop in self.agricultural_knowledge['crops'].keys():
            if crop in message_lower:
                return self._get_crop_advice(crop, language)
        
        # Pest-related queries
        if any(word in message_lower for word in ['pest', 'insect', 'disease', 'kwari', 'cuta']):
            return self._get_pest_advice(language)
        
        # Market-related queries
        if any(word in message_lower for word in ['price', 'market', 'sell', 'farashin', 'kasuwa']):
            return self._get_market_advice(language)
        
        # Default greeting
        return self._get_default_greeting(language, user_context.get('name', 'Farmer'))
    
    def _get_weather_advice(self, language: str) -> str:
        """Get weather-related advice"""
        advice = {
            'en': "Monitor weather conditions daily. Water crops early morning during hot weather. Ensure proper drainage during rainy season.",
            'ha': "Lura da yanayi kullum. Shayar da shuka da safe lokacin zafi. Tabbatar da magudanar ruwa a lokacin damina.",
            'yo': "Ṣe abojuto oju ojo lojoojumọ. Fi omi si eweko ni kutukutu nigba ooru. Rii daju pe omi le jade ni akoko ojo.",
            'ig': "Nyocha ọnọdụ ihu igwe kwa ụbọchị. Gbanye ihe ọkụkụ n'ụtụtụ n'oge okpomọkụ. Hụ na mmiri na-asọ nke ọma n'oge udu mmiri.",
            'ff': "Ƴeewto kawral jemma ñalawma. Jiyitin jiijal subaka e fiɗɗe mba njaawo. Ƴeew ngoppi ndiyam mba daminiiji."
        }
        return advice.get(language, advice['en'])
    
    def _get_crop_advice(self, crop: str, language: str) -> str:
        """Get crop-specific advice"""
        crop_data = self.agricultural_knowledge['crops'].get(crop, {})
        
        advice_templates = {
            'en': f"For {crop}: Plant during {crop_data.get('planting_season', 'appropriate season')}. "
                  f"Harvest in {crop_data.get('harvest_time', '3-4 months')}. "
                  f"Water needs: {crop_data.get('water_needs', 'Regular watering')}.",
            'ha': f"Don {crop}: Dasa a lokacin {crop_data.get('planting_season', 'lokaci mai dacewa')}. "
                  f"Girbi a cikin {crop_data.get('harvest_time', 'watanni 3-4')}. "
                  f"Bukatar ruwa: {crop_data.get('water_needs', 'Ban ruwa akai-akai')}.",
            'yo': f"Fun {crop}: Gbin lakoko {crop_data.get('planting_season', 'akoko to ye')}. "
                  f"Kore ni {crop_data.get('harvest_time', 'osu 3-4')}. "
                  f"Iwulo omi: {crop_data.get('water_needs', 'Fifi omi si deede')}.",
            'ig': f"Maka {crop}: Kụọ n'oge {crop_data.get('planting_season', 'oge kwesịrị ekwesị')}. "
                  f"Wee ghọrọ na {crop_data.get('harvest_time', 'ọnwa 3-4')}. "
                  f"Mkpa mmiri: {crop_data.get('water_needs', 'Igbanye mmiri mgbe niile')}.",
            'ff': f"Ngam {crop}: Hoor e sahaa {crop_data.get('planting_season', 'sahaa moƴƴude')}. "
                  f"Mbaɗ e {crop_data.get('harvest_time', 'lewdi 3-4')}. "
                  f"Sokla ndiyam: {crop_data.get('water_needs', 'Jiyinde ndiyam sahaa kala')}."
        }
        
        return advice_templates.get(language, advice_templates['en'])
    
    def _get_pest_advice(self, language: str) -> str:
        """Get pest management advice"""
        advice = {
            'en': "For pest control: Use neem oil spray in the evening. Practice crop rotation. Remove infected plants immediately. Consider biological control methods.",
            'ha': "Don karbe kwari: Yi amfani da man neem da maraice. Yi juyawa na shuke-shuke. Cire shuke masu cuta nan take. Duba hanyoyin kare ta dabi'a.",
            'yo': "Fun ijakadi kokoro: Lo omi epo neem ni alẹ. Ṣe iyipada gbigbin. Yọ eweko ti aisan ba kuro ni kiakia. Gbero awọn ọna ijakadi adayeba.",
            'ig': "Maka nchịkwa ụmụ ahụhụ: Jiri mmiri mmanụ neem fesa na mgbede. Mee mgbanwe ịkụ ihe. Wepụ osisi ndị rịara ọrịa ozugbo. Tụlee ụzọ nchịkwa ndụ.",
            'ff': "Ngam teeyagol marawle: Huutoro ooyel neem hiirto kuuɗe. Heɓ juwagol horiinde. Momtu jimɗe naange fof. Ƴeewto laawol teeyagol darnde."
        }
        return advice.get(language, advice['en'])
    
    def _get_market_advice(self, language: str) -> str:
        """Get market and pricing advice"""
        advice = {
            'en': "Market tips: Form cooperatives for better prices. Sell directly to consumers when possible. Add value through processing. Monitor seasonal price trends.",
            'ha': "Shawarwarin kasuwa: Kafa ƙungiyar manoma don kyakkyawan farashi. Sayar kai tsaye ga masu siye idan mai yiwuwa. Kara darajar ta hanyar sarrafa. Lura da canjin farashin yanayi.",
            'yo': "Imọran oja: Ṣe agbajo fun owo ti o dara ju. Ta taara si awọn alabara nigba ti o ṣee ṣe. Fi kun iye nipasẹ ṣiṣe. Ṣe abojuto awọn iyipada owo akoko.",
            'ig': "Ndụmọdụ ahịa: Mee nkwekọrịta maka ọnụahịa ka mma. Ree ozugbo ndị ahịa mgbe o kwere omume. Tinye uru site na nhazi. Nyochaa mgbanwe ọnụahịa oge.",
            'ff': "Waɗaade luumo: Mahir fedde ngam faama keewɗe. Jaar taral e jamaaɓe so wawni. Ɓeydu keera huutoraade. Ƴeewto waylude keewɗe sahaa-sahaa."
        }
        return advice.get(language, advice['en'])
    
    def _get_default_greeting(self, language: str, name: str) -> str:
        """Get default greeting message"""
        greetings = {
            'en': f"Hello {name}! I'm AgriSense AI, your agricultural assistant. Ask me about crops, weather, pests, or market prices. How can I help you today?",
            'ha': f"Sannu {name}! Ni AgriSense AI ne, mai taimako na aikin noma. Tambaye ni game da shuke-shuke, yanayi, kwari, ko farashin kasuwa. Ta yaya zan iya taimaka maka yau?",
            'yo': f"Bawo ni {name}! Emi ni AgriSense AI, oluranlọwọ rẹ fun ise agbẹ. Beere lọwọ mi nipa eweko, oju ojo, kokoro, tabi owo oja. Bawo ni mo le ran ọ lọwọ loni?",
            'ig': f"Ndewo {name}! Abụ m AgriSense AI, onye inyeaka gị maka ọrụ ugbo. Jụọ m ajụjụ banyere ihe ọkụkụ, ihu igwe, ụmụ ahụhụ, ma ọ bụ ọnụahịa ahịa. Kedu ka m ga-esi nyere gị aka taa?",
            'ff': f"Jam weli {name}! Mi AgriSense AI, walliitorde ma e golle wuurnde. Naamno e jiiwugol, jemma, marawle, kam keewɗe luumo. Hol no wallitaama hanne?"
        }
        return greetings.get(language, greetings['en'])
    
    def _get_error_message(self, language: str) -> str:
        """Get error message in user's language"""
        messages = {
            'en': "I apologize, but I'm having trouble processing your request right now. Please try again or rephrase your question.",
            'ha': "Na yi hakuri, amma ina da matsala wajen sarrafa bukatarku a yanzu. Ka sake gwadawa ko sake fasalin tambayarku.",
            'yo': "Mo tọrọ gafara, ṣugbọn mo ni wahala lati ṣe ibeere rẹ ni bayi. Jọwọ gbiyanju tabi tun ko ibeere rẹ.",
            'ig': "Ewela iwe, mana enwere m nsogbu ịhazi arịrịọ gị ugbu a. Biko nwaa ọzọ ma ọ bụ kwugharia ajụjụ gị.",
            'ff': "Miɗan hakke, kono mi heewaani namnde naamnirde maa jooni. Tiiɗno fuɗɗito kam fahamdito naamnade maa humpito."
        }
        return messages.get(language, messages['en'])
    
    def _generate_suggestions(self, message: str, language: str) -> List[str]:
        """Generate helpful suggestions based on the message"""
        suggestions_map = {
            'en': [
                "Ask about weather forecast for your area",
                "Get pest identification help",
                "Check current market prices",
                "Learn about crop rotation",
                "Get fertilizer recommendations"
            ],
            'ha': [
                "Tambaya game da hasashen yanayi na yankinku",
                "Neman taimako wajen gane kwari",
                "Duba farashin kasuwa na yanzu",
                "Koyi game da juyar da amfanin gona",
                "Neman shawarar taki"
            ],
            'yo': [
                "Beere nipa asọtẹlẹ oju ojo fun agbegbe rẹ",
                "Gba iranlọwọ idamo kokoro",
                "Ṣayẹwo owo oja lọwọlọwọ",
                "Kọ nipa iyipada gbigbin",
                "Gba iṣeduro ajile"
            ],
            'ig': [
                "Jụọ maka amụma ihu igwe maka mpaghara gị",
                "Nweta enyemaka nchọpụta ụmụ ahụhụ",
                "Lelee ọnụahịa ahịa ugbu a",
                "Mụta banyere mgbanwe ịkụ ihe",
                "Nweta ntụziaka fatịlaịza"
            ],
            'ff': [
                "Naamnin hasale jemma e diwal maa",
                "Heɓde wallitaare anndinde marawle",
                "Ƴeewto keewɗe luumo gonaaɗo",
                "Jannga e juwde horiinde",
                "Heɓde waɗaade takka"
            ]
        }
        
        return suggestions_map.get(language, suggestions_map['en'])
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """Get list of available AI providers for frontend"""
        return self.available_providers
    
    def set_user_ai_preference(self, user_id: int, provider: str) -> bool:
        """Set user's preferred AI provider (this would typically save to database)"""
        # This is a placeholder - in a real implementation, you'd save to database
        return provider in [p['id'] for p in self.available_providers]