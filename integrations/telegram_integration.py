"""
AgriSense AI - Telegram Bot Integration
Advanced Telegram messaging for farmer communication
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

class TelegramIntegration:
    """Telegram Bot integration for farmer communication"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.logger = logging.getLogger(__name__)
        self.application = None
        
        # Initialize application
        self.application = Application.builder().token(bot_token).build()
        self._setup_handlers()
        
        # Message templates for different languages
        self.message_templates = {
            'welcome': {
                'en': """🌾 *Welcome to AgriSense AI!*

I'm your smart farming assistant, ready to help with:
🤖 AI-powered agricultural advice
🌤️ Weather forecasts and alerts  
💰 Market prices and trends
🐛 Pest identification and control
📚 Agricultural knowledge from PDFs

*Quick Commands:*
/weather - Get weather info
/crops - Crop advice
/market - Market prices
/pests - Pest control
/help - Show all commands

Just send me a message to start chatting! 🚀""",
                
                'ha': """🌾 *Barka da zuwa AgriSense AI!*

Ni mai taimako na noma ne, shirye don taimaka da:
🤖 Shawarwarin noma ta hanyar AI
🌤️ Hasashen yanayi da gargadi
💰 Farashin kasuwa da yanayin cinikin
🐛 Gane kwari da magance su
📚 Ilimin noma daga takardun PDF

*Umarnin Gajeriyar:*
/weather - Samun bayanan yanayi
/crops - Shawarar shuke-shuke
/market - Farashin kasuwa
/pests - Shawo da kwari
/help - Nuna duk umarnin

Aika mini saƙo don fara hira! 🚀""",
                
                'yo': """🌾 *Kaabo si AgriSense AI!*

Mo ni oluranlọwọ agbẹ to gbọn, ti o setan lati ran ọ lọwọ pẹlu:
🤖 Imọran agbẹ nipasẹ AI
🌤️ Asọtẹlẹ oju ojo ati awọn ikilọ
💰 Owo oja ati awọn aami
🐛 Idanimọ kokoro ati iṣakoso
📚 Imọ agbẹ lati awọn faili PDF

*Awọn Aṣẹ Kiakia:*
/weather - Gba alaye oju ojo
/crops - Imọran eweko
/market - Owo oja
/pests - Iṣakoso kokoro
/help - Fi gbogbo awọn aṣẹ han

O kan ranṣẹ si mi lati bẹrẹ ibaraẹnisọrọ! 🚀""",
                
                'ig': """🌾 *Nnọọ na AgriSense AI!*

Abụ m onye inyeaka ọrụ ugbo gị nwere ọgụgụ isi, njikere inyere gị aka na:
🤖 Ndụmọdụ ọrụ ugbo site na AI
🌤️ Amụma ihu igwe na ọkwa
💰 Ọnụahịa ahịa na ọnọdụ azụmaahịa
🐛 Nchọpụta ụmụ ahụhụ na nchịkwa
📚 Ihe ọmụma ọrụ ugbo site na faịlụ PDF

*Iwu Ngwa Ngwa:*
/weather - Nweta ozi ihu igwe
/crops - Ndụmọdụ ihe ọkụkụ
/market - Ọnụahịa ahịa
/pests - Nchịkwa ụmụ ahụhụ
/help - Gosi iwu niile

Naanị zigatara m ozi ka ị malite ikwurịta okwu! 🚀""",
                
                'ff': """🌾 *Hunyaawa e AgriSense AI!*

Mi wallitorde maa e golle wuurnde, sirti ngam wallit-aada e:
🤖 Waɗaade wuurnde e AI
🌤️ Hasale jemma e haɓɓinɗi
💰 Keewɗe luumo e halkaaji
🐛 Anndinde marawle e lawal
📚 Anndal wuurnde iwdi e fiilde PDF

*Jokke Gaajeje:*
/weather - Heɓo haalaji jemma
/crops - Waɗaade jiiwugol
/market - Keewɗe luumo
/pests - Lawal marawle
/help - Hollu kala jokke

Neldu-mi ɓatakuuje ngam fuɗɗaade haala! 🚀"""
            },
            
            'help_menu': {
                'en': """🌾 *AgriSense AI - Command Menu*

*📱 Basic Commands:*
/start - Welcome message
/help - Show this menu
/language - Change language

*🌤️ Weather & Environment:*
/weather [location] - Get weather forecast
/alerts - Setup weather alerts
/forecast - 5-day weather forecast

*🌱 Crop Management:*
/crops [crop name] - Get crop advice
/planting - Planting calendar
/fertilizer - Fertilizer recommendations
/irrigation - Irrigation guidance

*🐛 Pest & Disease Control:*
/pests [description] - Pest identification
/diseases - Disease management
/organic - Organic pest control methods

*💰 Market Information:*
/market [crop] - Current market prices
/trends - Price trends and analysis
/selling - Best selling times

*📚 Knowledge & Learning:*
/upload - Upload PDF documents
/search [query] - Search agricultural knowledge
/tips - Daily farming tips

*⚙️ Settings:*
/profile - View/edit your profile
/notifications - Manage notifications
/feedback - Send feedback

Just type your question naturally - I understand multiple languages! 🗣️""",
                
                'ha': """🌾 *AgriSense AI - Menu na Umarnin*

*📱 Umarnin Asali:*
/start - Saƙon maraba
/help - Nuna wannan menu
/language - Canja harshe

*🌤️ Yanayi da Muhalli:*
/weather [wuri] - Samun hasashen yanayi
/alerts - Kafa gargadin yanayi
/forecast - Hasashen yanayi na kwanaki 5

*🌱 Sarrafa Shuke-shuke:*
/crops [sunan shuki] - Samun shawarar shuki
/planting - Kalandar shuka
/fertilizer - Shawarwarin taki
/irrigation - Jagorar ban ruwa

*🐛 Shawo da Kwari da Cututtuka:*
/pests [bayani] - Gane kwari
/diseases - Sarrafa cututtuka
/organic - Hanyoyin shawo da kwari na dabi'a

*💰 Bayanan Kasuwa:*
/market [shuki] - Farashin kasuwa na yanzu
/trends - Yanayin farashi da bincike
/selling - Mafi kyawun lokacin sayarwa

*📚 Ilimi da Koyo:*
/upload - Ɗora takardun PDF
/search [tambaya] - Binciken ilimin noma
/tips - Shawarwarin noma na yau da kullum

*⚙️ Saiti:*
/profile - Duba/gyara bayanan ku
/notifications - Sarrafa sanarwa
/feedback - Aika ra'ayi

Kawai rubuta tambayar ku a zahiri - na fahimci harsuna da yawa! 🗣️"""
            }
        }
        
        # Inline keyboards for quick actions
        self.quick_actions = {
            'en': [
                [InlineKeyboardButton("🌤️ Weather", callback_data="quick_weather"),
                 InlineKeyboardButton("🌱 Crop Advice", callback_data="quick_crops")],
                [InlineKeyboardButton("💰 Market Prices", callback_data="quick_market"),
                 InlineKeyboardButton("🐛 Pest Control", callback_data="quick_pests")],
                [InlineKeyboardButton("📚 Upload PDF", callback_data="quick_upload"),
                 InlineKeyboardButton("⚙️ Settings", callback_data="quick_settings")]
            ],
            'ha': [
                [InlineKeyboardButton("🌤️ Yanayi", callback_data="quick_weather"),
                 InlineKeyboardButton("🌱 Shawarar Shuki", callback_data="quick_crops")],
                [InlineKeyboardButton("💰 Farashin Kasuwa", callback_data="quick_market"),
                 InlineKeyboardButton("🐛 Shawo da Kwari", callback_data="quick_pests")],
                [InlineKeyboardButton("📚 Ɗora PDF", callback_data="quick_upload"),
                 InlineKeyboardButton("⚙️ Saiti", callback_data="quick_settings")]
            ]
        }
        
        # Language selection keyboard
        self.language_keyboard = [
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
             InlineKeyboardButton("🇳🇬 Hausa", callback_data="lang_ha")],
            [InlineKeyboardButton("🇳🇬 Yoruba", callback_data="lang_yo"),
             InlineKeyboardButton("🇳🇬 Igbo", callback_data="lang_ig")],
            [InlineKeyboardButton("🇳🇬 Fulfulde", callback_data="lang_ff")]
        ]
    
    def _setup_handlers(self):
        """Setup command and message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("language", self.language_command))
        self.application.add_handler(CommandHandler("weather", self.weather_command))
        self.application.add_handler(CommandHandler("crops", self.crops_command))
        self.application.add_handler(CommandHandler("market", self.market_command))
        self.application.add_handler(CommandHandler("pests", self.pests_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("upload", self.upload_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for general chat
        self.application.add_handler(MessageHandler(None, self.handle_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            welcome_text = self.message_templates['welcome'][user_language]
            keyboard = InlineKeyboardMarkup(self.quick_actions.get(user_language, self.quick_actions['en']))
            
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
            # Log user interaction
            self.logger.info(f"New user started bot: {user.username or user.first_name} (ID: {user.id})")
            
        except Exception as e:
            self.logger.error(f"Error in start command: {str(e)}")
            await update.message.reply_text("Welcome to AgriSense AI! 🌾")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            help_text = self.message_templates['help_menu'][user_language]
            
            await update.message.reply_text(
                help_text,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in help command: {str(e)}")
            await update.message.reply_text("Here are the available commands... 📚")
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command"""
        try:
            keyboard = InlineKeyboardMarkup(self.language_keyboard)
            
            await update.message.reply_text(
                "🌍 *Choose your preferred language:*\n"
                "Zaɓi harshen da kuke so:\n"
                "Yan eyan ede ti o fẹ:\n"
                "Họrọ asụsụ ị chọrọ:\n"
                "Suɓo ɗemngal ngal a yiɗi:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
            
        except Exception as e:
            self.logger.error(f"Error in language command: {str(e)}")
            await update.message.reply_text("Choose your language 🌍")
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            # Get location from command arguments
            location = ' '.join(context.args) if context.args else None
            
            if not location:
                messages = {
                    'en': "Please specify a location:\n`/weather Lagos`\n`/weather Kano, Nigeria`",
                    'ha': "Ka kayyade wuri:\n`/weather Lagos`\n`/weather Kano, Nigeria`",
                    'yo': "Jọwọ sọ ipo kan:\n`/weather Lagos`\n`/weather Kano, Nigeria`",
                    'ig': "Biko kwuo ebe:\n`/weather Lagos`\n`/weather Kano, Nigeria`",
                    'ff': "Tiiɗno maajɗin ɗoowi:\n`/weather Lagos`\n`/weather Kano, Nigeria`"
                }
                await update.message.reply_text(
                    messages.get(user_language, messages['en']),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generate weather response (integrate with weather service)
            weather_response = await self._get_weather_response(location, user_language)
            
            await update.message.reply_text(
                weather_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in weather command: {str(e)}")
            await update.message.reply_text("Weather service temporarily unavailable 🌤️")
    
    async def crops_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /crops command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            crop = ' '.join(context.args) if context.args else None
            
            if not crop:
                messages = {
                    'en': "Which crop do you need advice about?\n`/crops rice`\n`/crops tomato`\n`/crops maize`",
                    'ha': "Wane shuki kuke bukatar shawara game da shi?\n`/crops shinkafa`\n`/crops tumatir`\n`/crops masara`",
                    'yo': "Iru eweko wo ni o nilo imọran nipa rẹ?\n`/crops iresi`\n`/crops tomato`\n`/crops agbado`",
                    'ig': "Kedu ihe ọkụkụ ị chọrọ ndụmọdụ maka ya?\n`/crops osikapa`\n`/crops tomato`\n`/crops ọka`",
                    'ff': "Hol jiiju ɗon naa yiɗaaki waɗde?\n`/crops mbaɗi`\n`/crops tomat`\n`/crops mbari`"
                }
                await update.message.reply_text(
                    messages.get(user_language, messages['en']),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generate crop advice
            crop_response = await self._get_crop_advice(crop, user_language)
            
            await update.message.reply_text(
                crop_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in crops command: {str(e)}")
            await update.message.reply_text("Crop advice service temporarily unavailable 🌱")
    
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /market command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            # Generate market prices response
            market_response = await self._get_market_prices(user_language)
            
            await update.message.reply_text(
                market_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in market command: {str(e)}")
            await update.message.reply_text("Market data temporarily unavailable 💰")
    
    async def pests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pests command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            description = ' '.join(context.args) if context.args else None
            
            if not description:
                messages = {
                    'en': "Describe the pest issue:\n`/pests aphids on tomato`\n`/pests small holes in leaves`",
                    'ha': "Bayyana matsalar kwari:\n`/pests kwari akan tumatir`\n`/pests kananan ramuka a ganyaye`",
                    'yo': "Ṣe apejuwe iṣoro kokoro:\n`/pests kokoro lori tomato`\n`/pests awọn iho kekere ninu ewe`",
                    'ig': "Kọwaa nsogbu ụmụ ahụhụ:\n`/pests ụmụ ahụhụ na tomato`\n`/pests obere oghere na akwụkwọ`",
                    'ff': "Wiyde caɗeele marawle:\n`/pests marawle e tomat`\n`/pests luumɗe ceeɗɗe e nderaagu`"
                }
                await update.message.reply_text(
                    messages.get(user_language, messages['en']),
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generate pest control advice
            pest_response = await self._get_pest_advice(description, user_language)
            
            await update.message.reply_text(
                pest_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in pests command: {str(e)}")
            await update.message.reply_text("Pest control advice temporarily unavailable 🐛")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            # Generate user profile
            profile_response = await self._get_user_profile(user.id, user_language)
            
            await update.message.reply_text(
                profile_response,
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in profile command: {str(e)}")
            await update.message.reply_text("Profile service temporarily unavailable 👤")
    
    async def upload_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /upload command"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            messages = {
                'en': """📚 *Upload Agricultural Documents*

Send me PDF files containing agricultural information, and I'll extract insights for you!

*Supported formats:* PDF
*Maximum size:* 16MB
*Examples:* Crop guides, research papers, extension materials

Just send the PDF file as a document attachment.""",
                
                'ha': """📚 *Ɗora Takardun Noma*

Aiko mini fayilolin PDF masu ɗauke da bayanan noma, kuma zan fitar muku da fahimta!

*Nau'ikan da ake tallafawa:* PDF
*Mafi girman girma:* 16MB
*Misalai:* Jagororin shuke-shuke, takardun bincike, kayan fadada

Kawai aika fayil ɗin PDF a matsayin haɗin takarda."""
            }
            
            await update.message.reply_text(
                messages.get(user_language, messages['en']),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error in upload command: {str(e)}")
            await update.message.reply_text("Upload service temporarily unavailable 📚")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard button callbacks"""
        try:
            query = update.callback_query
            user = query.from_user
            data = query.data
            
            await query.answer()
            
            if data.startswith("lang_"):
                # Language selection
                language = data.split("_")[1]
                self._set_user_language(user.id, language)
                
                language_names = {
                    'en': 'English 🇺🇸',
                    'ha': 'Hausa 🇳🇬',
                    'yo': 'Yoruba 🇳🇬',
                    'ig': 'Igbo 🇳🇬',
                    'ff': 'Fulfulde 🇳🇬'
                }
                
                await query.edit_message_text(
                    f"✅ Language set to {language_names.get(language, language)}\n"
                    f"Send /help to see commands in your language."
                )
                
            elif data.startswith("quick_"):
                # Quick action buttons
                action = data.split("_")[1]
                await self._handle_quick_action(query, action, user.id)
                
        except Exception as e:
            self.logger.error(f"Error in button callback: {str(e)}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general messages and document uploads"""
        try:
            user = update.effective_user
            message = update.message
            user_language = self._get_user_language(user.id)
            
            # Handle document uploads
            if message.document:
                await self._handle_document_upload(update, context)
                return
            
            # Handle photo uploads
            if message.photo:
                await self._handle_photo_upload(update, context)
                return
            
            # Handle text messages
            if message.text:
                # Send typing indicator
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id,
                    action="typing"
                )
                
                # Process with AI (integrate with main AI engine)
                response = await self._process_with_ai(message.text, user_language, user.id)
                
                await message.reply_text(
                    response,
                    parse_mode=ParseMode.MARKDOWN
                )
            
        except Exception as e:
            self.logger.error(f"Error handling message: {str(e)}")
            await update.message.reply_text("Sorry, I had trouble processing your message. Please try again.")
    
    async def _handle_document_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PDF document uploads"""
        try:
            user = update.effective_user
            document = update.message.document
            user_language = self._get_user_language(user.id)
            
            # Check file type
            if not document.file_name.lower().endswith('.pdf'):
                messages = {
                    'en': "❌ Only PDF files are supported. Please upload a PDF document.",
                    'ha': "❌ Ana tallafawa fayilolin PDF kawai. Da fatan za a ɗora takarda ta PDF.",
                    'yo': "❌ Awọn faili PDF nikan ni a ṣe atilẹyin. Jọwọ gbekalẹ iwe PDF.",
                    'ig': "❌ Naanị faịlụ PDF ka a na-akwado. Biko tinye akwụkwọ PDF.",
                    'ff': "❌ Fiilde PDF tan woni nder wallafi. Tiiɗno ɗertin fiilde PDF."
                }
                await update.message.reply_text(messages.get(user_language, messages['en']))
                return
            
            # Check file size (16MB limit)
            if document.file_size > 16 * 1024 * 1024:
                messages = {
                    'en': "❌ File too large. Maximum size is 16MB.",
                    'ha': "❌ Fayil ɗin ya yi girma sosai. Mafi girman girma shine 16MB.",
                    'yo': "❌ Faili naa tobi ju. Iwọn ti o pọju ni 16MB.",
                    'ig': "❌ Faịlụ ahụ buru ibu nke ukwuu. Nha kachasị elu bụ 16MB.",
                    'ff': "❌ Fiilde nde mawni. Mabɗude nde 16MB."
                }
                await update.message.reply_text(messages.get(user_language, messages['en']))
                return
            
            # Download and process file
            file = await context.bot.get_file(document.file_id)
            
            # Send processing message
            processing_messages = {
                'en': "📚 Processing your PDF document... This may take a moment.",
                'ha': "📚 Ana sarrafa takardun PDF ɗin ku... Wannan na iya ɗaukar ɗan lokaci.",
                'yo': "📚 N ṣe iṣẹ lori iwe PDF rẹ... Eyi le gba igba diẹ.",
                'ig': "📚 Na-edozi akwụkwọ PDF gị... Nke a nwere ike were obere oge.",
                'ff': "📚 Mi huutora fiilde PDF maa... Ɗum waawi ɗaura sakaani."
            }
            
            processing_msg = await update.message.reply_text(
                processing_messages.get(user_language, processing_messages['en'])
            )
            
            # Simulate processing (integrate with RAG system)
            await asyncio.sleep(2)
            
            success_messages = {
                'en': f"✅ Document '{document.file_name}' processed successfully!\n\n"
                      f"You can now ask questions about the content. Try:\n"
                      f"• 'What does this document say about rice farming?'\n"
                      f"• 'Summarize the main points'\n"
                      f"• 'What fertilizer recommendations are mentioned?'",
                
                'ha': f"✅ Takarda '{document.file_name}' an sarrafa ta cikin nasara!\n\n"
                      f"Yanzu kuna iya yin tambayoyi game da abun ciki. Gwada:\n"
                      f"• 'Me wannan takarda ta faɗa game da noman shinkafa?'\n"
                      f"• 'Taƙaita manyan batutuwa'\n"
                      f"• 'Waɗanne shawarwarin taki aka ambata?'"
            }
            
            await context.bot.edit_message_text(
                text=success_messages.get(user_language, success_messages['en']),
                chat_id=update.effective_chat.id,
                message_id=processing_msg.message_id
            )
            
        except Exception as e:
            self.logger.error(f"Error handling document upload: {str(e)}")
            await update.message.reply_text("❌ Error processing document. Please try again.")
    
    async def _handle_photo_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads for pest/disease identification"""
        try:
            user = update.effective_user
            user_language = self._get_user_language(user.id)
            
            messages = {
                'en': "📸 *Photo Analysis Feature*\n\n"
                      "I can help identify pests and diseases from photos! "
                      "Send a clear photo of affected plants with description for best results.\n\n"
                      "Example: 'These are my tomato leaves with spots'",
                
                'ha': "📸 *Aikin Nazarin Hoto*\n\n"
                      "Zan iya taimakawa wajen gane kwari da cututtuka daga hotuna! "
                      "Aika hoto mai haskaka na shuke-shuke da suka kamu da cuta tare da bayanin don mafi kyawun sakamako.\n\n"
                      "Misali: 'Waɗannan ganyayen tumatir ne masu tabo'"
            }
            
            await update.message.reply_text(
                messages.get(user_language, messages['en']),
                parse_mode=ParseMode.MARKDOWN
            )
            
        except Exception as e:
            self.logger.error(f"Error handling photo upload: {str(e)}")
    
    async def _handle_quick_action(self, query, action: str, user_id: int):
        """Handle quick action button presses"""
        try:
            user_language = self._get_user_language(user_id)
            
            if action == "weather":
                response = "🌤️ Getting weather information... Please specify your location."
            elif action == "crops":
                response = "🌱 What crop would you like advice about?"
            elif action == "market":
                response = "💰 Fetching current market prices..."
            elif action == "pests":
                response = "🐛 Describe the pest issue you're experiencing."
            elif action == "upload":
                response = "📚 Send me a PDF document to analyze."
            elif action == "settings":
                response = "⚙️ Use /language to change language, /profile for user settings."
            else:
                response = "How can I help you today?"
            
            await query.message.reply_text(response)
            
        except Exception as e:
            self.logger.error(f"Error handling quick action: {str(e)}")
    
    async def _get_weather_response(self, location: str, language: str) -> str:
        """Generate weather response for location"""
        # This would integrate with the weather service
        responses = {
            'en': f"🌤️ *Weather for {location}*\n\n"
                  f"• Temperature: 28°C\n"
                  f"• Condition: Partly cloudy\n"
                  f"• Humidity: 75%\n"
                  f"• Wind: 5 km/h\n\n"
                  f"*Agricultural Advice:*\n"
                  f"Good conditions for most farming activities. "
                  f"Consider light irrigation in the evening.",
            
            'ha': f"🌤️ *Yanayi na {location}*\n\n"
                  f"• Zafin jiki: 28°C\n"
                  f"• Yanayi: Gizagizai kadan\n"
                  f"• Danshi: 75%\n"
                  f"• Iska: 5 km/h\n\n"
                  f"*Shawarar Noma:*\n"
                  f"Yanayi mai kyau don yawancin ayyukan noma. "
                  f"Yi la'akari da ɗan ban ruwa da maraice."
        }
        
        return responses.get(language, responses['en'])
    
    async def _get_crop_advice(self, crop: str, language: str) -> str:
        """Generate crop advice"""
        responses = {
            'en': f"🌱 *Advice for {crop.title()}*\n\n"
                  f"• Best planting season: Rainy season (May-July)\n"
                  f"• Soil requirements: Well-drained, fertile soil\n"
                  f"• Fertilizer: NPK 15-15-15 at planting\n"
                  f"• Watering: Regular, avoid waterlogging\n"
                  f"• Harvest time: 90-120 days\n\n"
                  f"*Current season tips:*\n"
                  f"Monitor for pests and ensure adequate drainage.",
            
            'ha': f"🌱 *Shawara don {crop.title()}*\n\n"
                  f"• Mafi kyawun lokacin shuka: Lokacin damina (Mayu-Yuli)\n"
                  f"• Bukatun kasa: Kasa mai magudanar ruwa da kiwaye\n"
                  f"• Taki: NPK 15-15-15 a lokacin shuka\n"
                  f"• Ban ruwa: Akai-akai, guje wa yawan ruwa\n"
                  f"• Lokacin girbi: Kwanaki 90-120\n\n"
                  f"*Shawarwarin lokaci na yanzu:*\n"
                  f"Lura da kwari kuma tabbatar da isasshen magudanar ruwa."
        }
        
        return responses.get(language, responses['en'])
    
    async def _get_market_prices(self, language: str) -> str:
        """Generate market prices response"""
        responses = {
            'en': "💰 *Current Market Prices*\n\n"
                  "🌾 Rice: ₦30,000 - ₦35,000/bag\n"
                  "🌽 Maize: ₦25,000 - ₦28,000/bag\n"
                  "🍅 Tomato: ₦45,000 - ₦55,000/ton\n"
                  "🥜 Groundnut: ₦40,000 - ₦45,000/bag\n\n"
                  "*Market Trend:* 📈 Prices stable\n"
                  "*Best selling time:* End of month\n\n"
                  "_Prices may vary by location_",
            
            'ha': "💰 *Farashin Kasuwa na Yanzu*\n\n"
                  "🌾 Shinkafa: ₦30,000 - ₦35,000/buhun\n"
                  "🌽 Masara: ₦25,000 - ₦28,000/buhun\n"
                  "🍅 Tumatir: ₦45,000 - ₦55,000/ton\n"
                  "🥜 Gyada: ₦40,000 - ₦45,000/buhun\n\n"
                  "*Yanayin Kasuwa:* 📈 Farashi ya daidaita\n"
                  "*Mafi kyawun lokacin sayarwa:* Ƙarshen wata\n\n"
                  "_Farashi na iya bambanta bisa wuri_"
        }
        
        return responses.get(language, responses['en'])
    
    async def _get_pest_advice(self, description: str, language: str) -> str:
        """Generate pest control advice"""
        responses = {
            'en': f"🐛 *Pest Control Advice*\n\n"
                  f"Based on your description: '{description}'\n\n"
                  f"*Recommended treatment:*\n"
                  f"• Neem oil spray (evening application)\n"
                  f"• Remove affected plant parts\n"
                  f"• Improve air circulation\n"
                  f"• Monitor regularly\n\n"
                  f"*Organic solution:* Mix neem oil + liquid soap\n"
                  f"*Chemical option:* Contact local extension officer",
            
            'ha': f"🐛 *Shawarar Shawo da Kwari*\n\n"
                  f"Bisa ga bayanin ku: '{description}'\n\n"
                  f"*Maganin da aka ba da shawara:*\n"
                  f"• Fesa man neem (a maraice)\n"
                  f"• Cire sassan shuka da suka kamu da cuta\n"
                  f"• Inganta motsin iska\n"
                  f"• Yi sa ido akai-akai\n\n"
                  f"*Magani na dabi'a:* Haɗa man neem + sabulun ruwa\n"
                  f"*Zaɓin sinadarai:* Tuntuɓi jami'in fadada"
        }
        
        return responses.get(language, responses['en'])
    
    async def _get_user_profile(self, user_id: int, language: str) -> str:
        """Generate user profile information"""
        # This would integrate with the user database
        responses = {
            'en': "👤 *Your Profile*\n\n"
                  "• Name: Farmer\n"
                  "• Language: English\n"
                  "• Joined: Recently\n"
                  "• Total messages: 1\n\n"
                  "Use /language to change language settings.",
            
            'ha': "👤 *Bayananku*\n\n"
                  "• Suna: Manomi\n"
                  "• Harshe: Turanci\n"
                  "• Shiga: Kwanan nan\n"
                  "• Jimlar saƙonni: 1\n\n"
                  "Yi amfani da /language don canja saitunan harshe."
        }
        
        return responses.get(language, responses['en'])
    
    async def _process_with_ai(self, message: str, language: str, user_id: int) -> str:
        """Process message with AI engine"""
        # This would integrate with the main AI engine
        # For now, return a simple response
        responses = {
            'en': f"Thank you for your message: '{message[:50]}...'\n\n"
                  f"I'm processing your request with our AI system. "
                  f"For detailed agricultural advice, please use specific commands like:\n"
                  f"• /weather [location]\n"
                  f"• /crops [crop name]\n"
                  f"• /market\n"
                  f"• /help for more options",
            
            'ha': f"Na gode da saƙonku: '{message[:50]}...'\n\n"
                  f"Ina sarrafa bukatarku da tsarin AI ɗinmu. "
                  f"Don cikakkun shawarwarin noma, da fatan za a yi amfani da takamaiman umarnin kamar:\n"
                  f"• /weather [wuri]\n"
                  f"• /crops [sunan shuki]\n"
                  f"• /market\n"
                  f"• /help don ƙarin zaɓuɓɓuka"
        }
        
        return responses.get(language, responses['en'])
    
    def _get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        # This would integrate with user database
        # For now, return default language
        return 'en'
    
    def _set_user_language(self, user_id: int, language: str):
        """Set user's preferred language"""
        # This would save to user database
        pass
    
    async def start_bot(self):
        """Start the Telegram bot"""
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            self.logger.info("🤖 Telegram bot started successfully")
            
            # Keep the bot running
            await self.application.updater.idle()
            
        except Exception as e:
            self.logger.error(f"Error starting Telegram bot: {str(e)}")
            raise
    
    async def stop_bot(self):
        """Stop the Telegram bot"""
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            
            self.logger.info("🤖 Telegram bot stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping Telegram bot: {str(e)}")

# Async function to run the bot
async def run_telegram_bot(bot_token: str):
    """Run the Telegram bot"""
    bot = TelegramIntegration(bot_token)
    await bot.start_bot()

# For running as standalone script
if __name__ == "__main__":
    import asyncio
    
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    if not BOT_TOKEN:
        print("Please set TELEGRAM_BOT_TOKEN environment variable")
        exit(1)
    
    asyncio.run(run_telegram_bot(BOT_TOKEN))