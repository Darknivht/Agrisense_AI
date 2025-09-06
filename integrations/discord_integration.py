"""
AgriSense AI - Discord Bot Integration
Advanced Discord bot for farming communities and servers
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import discord
from discord.ext import commands, tasks
import json

class AgriSenseDiscordBot(commands.Bot):
    """Discord bot for agricultural communities"""
    
    def __init__(self):
        # Bot configuration
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=['!agri ', '!farm ', '!ag '],
            intents=intents,
            description="AgriSense AI - Smart Agricultural Assistant for Discord",
            help_command=None
        )
        
        self.logger = logging.getLogger(__name__)
        
        # Language templates
        self.language_templates = {
            'welcome': {
                'en': """🌾 **Welcome to AgriSense AI!**

I'm your smart farming assistant, ready to help your Discord community with:
🤖 AI-powered agricultural advice
🌤️ Weather forecasts and alerts  
💰 Market prices and trends
🐛 Pest identification and control
📚 Agricultural knowledge from documents

**Quick Commands:**
`!agri weather <location>` - Get weather info
`!agri crops <crop>` - Crop advice
`!agri market` - Market prices
`!agri pests <description>` - Pest control
`!agri help` - Show all commands

**Community Features:**
📊 Farming discussion channels
📈 Price alerts for your server
🎓 Educational content sharing
👥 Farmer networking

Just mention me or use commands to get started! 🚀""",
                
                'ha': """🌾 **Barka da zuwa AgriSense AI!**

Ni mai taimako na noma ne, shirye don taimaka wa al'ummarku ta Discord da:
🤖 Shawarwarin noma ta hanyar AI
🌤️ Hasashen yanayi da gargadi
💰 Farashin kasuwa da yanayin cinikin
🐛 Gane kwari da magance su
📚 Ilimin noma daga takardun

**Umarnin Gajeriyar:**
`!agri weather <wuri>` - Samun bayanan yanayi
`!agri crops <shuki>` - Shawarar shuke-shuke
`!agri market` - Farashin kasuwa
`!agri pests <bayani>` - Shawo da kwari
`!agri help` - Nuna duk umarnin

**Abubuwan Al'umma:**
📊 Tashoshi na tattaunawa kan noma
📈 Gargadin farashi don server ɗinku
🎓 Raba abun ciki na ilimi
👥 Haɗin gwiwar manoma

Kawai ku ambata ni ko yi amfani da umarnin don farawa! 🚀"""
            },
            
            'help_embed': {
                'en': {
                    'title': '🌾 AgriSense AI - Command Guide',
                    'description': 'Your complete agricultural assistant for Discord!',
                    'fields': [
                        {
                            'name': '🌤️ Weather Commands',
                            'value': '`!agri weather <location>` - Current weather\n'
                                   '`!agri forecast <location>` - 5-day forecast\n'
                                   '`!agri alerts setup` - Setup weather alerts',
                            'inline': False
                        },
                        {
                            'name': '🌱 Crop Management',
                            'value': '`!agri crops <crop>` - Get crop advice\n'
                                   '`!agri planting <crop>` - Planting guide\n'
                                   '`!agri fertilizer <crop>` - Fertilizer tips',
                            'inline': False
                        },
                        {
                            'name': '🐛 Pest & Disease Control',
                            'value': '`!agri pests <description>` - Pest identification\n'
                                   '`!agri diseases <symptoms>` - Disease diagnosis\n'
                                   '`!agri organic <pest>` - Organic solutions',
                            'inline': False
                        },
                        {
                            'name': '💰 Market Information',
                            'value': '`!agri market` - Current prices\n'
                                   '`!agri prices <crop>` - Specific crop prices\n'
                                   '`!agri trends` - Market analysis',
                            'inline': False
                        },
                        {
                            'name': '📚 Knowledge & Learning',
                            'value': '`!agri search <query>` - Search knowledge\n'
                                   '`!agri tips` - Daily farming tips\n'
                                   '`!agri guide <topic>` - Detailed guides',
                            'inline': False
                        },
                        {
                            'name': '⚙️ Server Management',
                            'value': '`!agri setup` - Server configuration\n'
                                   '`!agri channels` - Create farming channels\n'
                                   '`!agri roles` - Setup farmer roles',
                            'inline': False
                        }
                    ]
                }
            }
        }
        
        # Farming channels to create
        self.farming_channels = [
            {'name': '🌾-general-farming', 'topic': 'General farming discussions and questions'},
            {'name': '🌤️-weather-alerts', 'topic': 'Weather updates and agricultural alerts'},
            {'name': '💰-market-prices', 'topic': 'Crop prices and market discussions'},
            {'name': '🐛-pest-control', 'topic': 'Pest identification and organic solutions'},
            {'name': '📚-knowledge-sharing', 'topic': 'Share farming guides, research, and tips'},
            {'name': '🤝-farmer-networking', 'topic': 'Connect with fellow farmers'},
            {'name': '📊-farm-analytics', 'topic': 'Data and analytics for farming decisions'}
        ]
        
        # Farmer roles
        self.farmer_roles = [
            {'name': '🌾 Crop Farmer', 'color': 0x4CAF50},
            {'name': '🐄 Livestock Farmer', 'color': 0x8BC34A},
            {'name': '🍅 Vegetable Grower', 'color': 0xFF5722},
            {'name': '🌳 Tree Crop Farmer', 'color': 0x795548},
            {'name': '🐟 Fish Farmer', 'color': 0x2196F3},
            {'name': '🌿 Organic Farmer', 'color': 0x66BB6A},
            {'name': '📚 Agricultural Student', 'color': 0x9C27B0},
            {'name': '🎓 Extension Officer', 'color': 0xFF9800}
        ]
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.logger.info(f'🤖 AgriSense Discord Bot logged in as {self.user}')
        self.logger.info(f'📊 Connected to {len(self.guilds)} servers')
        
        # Start background tasks
        self.daily_tips.start()
        self.price_updates.start()
        
        # Set bot status
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="farmers | !agri help"
            )
        )
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        self.logger.info(f'🏠 Joined new server: {guild.name} (ID: {guild.id})')
        
        # Send welcome message to system channel or first text channel
        channel = guild.system_channel or next(
            (ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages),
            None
        )
        
        if channel:
            embed = discord.Embed(
                title="🌾 Thank you for adding AgriSense AI!",
                description=self.language_templates['welcome']['en'],
                color=0x4CAF50
            )
            embed.add_field(
                name="🚀 Getting Started",
                value="Type `!agri setup` to configure your farming server\n"
                      "Type `!agri help` to see all available commands",
                inline=False
            )
            embed.set_footer(text="Made with ❤️ for farming communities")
            
            await channel.send(embed=embed)
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Ignore bot messages
        if message.author.bot:
            return
        
        # Process commands
        await self.process_commands(message)
        
        # Handle mentions
        if self.user.mentioned_in(message) and not message.mention_everyone:
            await self.handle_mention(message)
    
    async def handle_mention(self, message):
        """Handle when bot is mentioned"""
        try:
            # Remove mention from message
            content = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            if not content:
                # Just mentioned, show quick help
                embed = discord.Embed(
                    title="👋 Hello there!",
                    description="I'm AgriSense AI, your farming assistant!\n\n"
                               "Type `!agri help` for commands or just ask me farming questions!",
                    color=0x4CAF50
                )
                await message.reply(embed=embed)
                return
            
            # Process the message as a question
            await self.process_natural_language(message, content)
            
        except Exception as e:
            self.logger.error(f"Error handling mention: {str(e)}")
    
    async def process_natural_language(self, message, content):
        """Process natural language questions"""
        try:
            # Send typing indicator
            async with message.channel.typing():
                # Simulate AI processing (integrate with main AI engine)
                await asyncio.sleep(1)
                
                # Generate response based on content
                response = await self.generate_ai_response(content, message.author.id)
                
                embed = discord.Embed(
                    title="🤖 AgriSense AI Response",
                    description=response,
                    color=0x2196F3
                )
                embed.set_footer(text=f"Asked by {message.author.display_name}")
                
                await message.reply(embed=embed)
        
        except Exception as e:
            self.logger.error(f"Error processing natural language: {str(e)}")
            await message.reply("Sorry, I had trouble processing your question. Please try again!")
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        try:
            help_data = self.language_templates['help_embed']['en']
            
            embed = discord.Embed(
                title=help_data['title'],
                description=help_data['description'],
                color=0x4CAF50
            )
            
            for field in help_data['fields']:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline']
                )
            
            embed.add_field(
                name="💡 Tips",
                value="• Use `@AgriSense` to ask natural language questions\n"
                      "• Join farming channels for community discussions\n"
                      "• Set up alerts for weather and price updates",
                inline=False
            )
            
            embed.set_footer(text="AgriSense AI • Made for farming communities")
            embed.set_thumbnail(url=self.user.avatar.url if self.user.avatar else None)
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in help command: {str(e)}")
            await ctx.reply("Error displaying help. Please try again.")
    
    @commands.command(name='weather')
    async def weather_command(self, ctx, *, location: str = None):
        """Get weather information"""
        try:
            if not location:
                await ctx.reply("Please specify a location: `!agri weather Lagos`")
                return
            
            # Generate weather embed
            embed = await self.get_weather_embed(location)
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in weather command: {str(e)}")
            await ctx.reply("Weather service temporarily unavailable 🌤️")
    
    @commands.command(name='crops')
    async def crops_command(self, ctx, *, crop: str = None):
        """Get crop advice"""
        try:
            if not crop:
                await ctx.reply("Which crop do you need advice about? `!agri crops rice`")
                return
            
            embed = await self.get_crop_embed(crop)
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in crops command: {str(e)}")
            await ctx.reply("Crop advice service temporarily unavailable 🌱")
    
    @commands.command(name='market')
    async def market_command(self, ctx):
        """Get market prices"""
        try:
            embed = await self.get_market_embed()
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in market command: {str(e)}")
            await ctx.reply("Market service temporarily unavailable 💰")
    
    @commands.command(name='pests')
    async def pests_command(self, ctx, *, description: str = None):
        """Get pest control advice"""
        try:
            if not description:
                await ctx.reply("Describe the pest issue: `!agri pests aphids on tomato`")
                return
            
            embed = await self.get_pest_embed(description)
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in pests command: {str(e)}")
            await ctx.reply("Pest control service temporarily unavailable 🐛")
    
    @commands.command(name='setup')
    @commands.has_permissions(manage_guild=True)
    async def setup_command(self, ctx):
        """Setup farming server (Admin only)"""
        try:
            embed = discord.Embed(
                title="🏗️ AgriSense Server Setup",
                description="Setting up your farming community server...",
                color=0xFF9800
            )
            
            setup_msg = await ctx.reply(embed=embed)
            
            # Create farming category
            category = await ctx.guild.create_category(
                "🌾 Farming Hub",
                reason="AgriSense AI server setup"
            )
            
            # Create farming channels
            created_channels = []
            for channel_info in self.farming_channels:
                channel = await ctx.guild.create_text_channel(
                    channel_info['name'],
                    category=category,
                    topic=channel_info['topic'],
                    reason="AgriSense AI farming channels"
                )
                created_channels.append(channel.mention)
            
            # Create farmer roles
            created_roles = []
            for role_info in self.farmer_roles:
                role = await ctx.guild.create_role(
                    name=role_info['name'],
                    color=discord.Color(role_info['color']),
                    mentionable=True,
                    reason="AgriSense AI farmer roles"
                )
                created_roles.append(role.mention)
            
            # Update embed with results
            embed.title = "✅ Server Setup Complete!"
            embed.description = "Your farming community server has been configured!"
            embed.color = 0x4CAF50
            
            embed.add_field(
                name="📋 Created Channels",
                value="\n".join(created_channels[:10]),  # Limit display
                inline=False
            )
            
            embed.add_field(
                name="👥 Created Roles",
                value="\n".join(created_roles[:8]),  # Limit display
                inline=False
            )
            
            embed.add_field(
                name="🎯 Next Steps",
                value="• Members can use `!agri role` to get farmer roles\n"
                      "• Use `!agri alerts setup` for weather notifications\n"
                      "• Start discussions in the farming channels!",
                inline=False
            )
            
            await setup_msg.edit(embed=embed)
            
        except discord.Forbidden:
            await ctx.reply("❌ I need `Manage Channels` and `Manage Roles` permissions to setup the server.")
        except Exception as e:
            self.logger.error(f"Error in setup command: {str(e)}")
            await ctx.reply("❌ Error setting up server. Please check my permissions.")
    
    @commands.command(name='role')
    async def role_command(self, ctx):
        """Let users select farmer roles"""
        try:
            # Get available farmer roles
            guild_roles = ctx.guild.roles
            farmer_roles = [role for role in guild_roles if any(fr['name'] in role.name for fr in self.farmer_roles)]
            
            if not farmer_roles:
                await ctx.reply("No farmer roles found. Ask an admin to run `!agri setup` first.")
                return
            
            embed = discord.Embed(
                title="👥 Select Your Farmer Role",
                description="React with the corresponding emoji to get a role:",
                color=0x9C27B0
            )
            
            emojis = ['🌾', '🐄', '🍅', '🌳', '🐟', '🌿', '📚', '🎓']
            role_text = []
            
            for i, role in enumerate(farmer_roles[:8]):  # Limit to 8 roles
                emoji = emojis[i] if i < len(emojis) else '🔹'
                role_text.append(f"{emoji} {role.name}")
            
            embed.add_field(
                name="Available Roles",
                value="\n".join(role_text),
                inline=False
            )
            
            message = await ctx.reply(embed=embed)
            
            # Add reactions
            for i in range(min(len(farmer_roles), len(emojis))):
                await message.add_reaction(emojis[i])
            
        except Exception as e:
            self.logger.error(f"Error in role command: {str(e)}")
            await ctx.reply("Error displaying roles. Please try again.")
    
    @commands.command(name='tips')
    async def tips_command(self, ctx):
        """Get daily farming tips"""
        try:
            tips = [
                "🌱 **Soil Health**: Test your soil pH regularly. Most crops prefer slightly acidic to neutral soil (6.0-7.0 pH).",
                "💧 **Water Management**: Water plants early morning to reduce evaporation and prevent fungal diseases.",
                "🐛 **Natural Pest Control**: Companion planting with marigolds can help deter harmful insects naturally.",
                "🌾 **Crop Rotation**: Rotate crops annually to prevent soil depletion and break pest cycles.",
                "📅 **Timing**: Plant crops according to local climate patterns and seasonal calendars for best results.",
                "🌿 **Organic Matter**: Add compost to your soil regularly to improve fertility and water retention.",
                "🦗 **Beneficial Insects**: Encourage beneficial insects by planting diverse flowering plants around your farm.",
                "📊 **Record Keeping**: Keep detailed records of planting dates, treatments, and yields for better planning."
            ]
            
            import random
            daily_tip = random.choice(tips)
            
            embed = discord.Embed(
                title="💡 Daily Farming Tip",
                description=daily_tip,
                color=0xFFEB3B
            )
            embed.set_footer(text="New tip available daily!")
            
            await ctx.reply(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in tips command: {str(e)}")
            await ctx.reply("Tips service temporarily unavailable 💡")
    
    @tasks.loop(hours=24)
    async def daily_tips(self):
        """Send daily tips to configured channels"""
        try:
            # This would send tips to channels that have opted in
            pass
        except Exception as e:
            self.logger.error(f"Error in daily tips task: {str(e)}")
    
    @tasks.loop(hours=6)
    async def price_updates(self):
        """Send market price updates"""
        try:
            # This would send price updates to market channels
            pass
        except Exception as e:
            self.logger.error(f"Error in price updates task: {str(e)}")
    
    async def get_weather_embed(self, location: str) -> discord.Embed:
        """Generate weather embed"""
        # This would integrate with weather service
        embed = discord.Embed(
            title=f"🌤️ Weather for {location.title()}",
            color=0x2196F3
        )
        
        embed.add_field(name="🌡️ Temperature", value="28°C", inline=True)
        embed.add_field(name="☁️ Condition", value="Partly Cloudy", inline=True)
        embed.add_field(name="💧 Humidity", value="75%", inline=True)
        embed.add_field(name="💨 Wind", value="5 km/h", inline=True)
        embed.add_field(name="🌧️ Rainfall", value="0mm", inline=True)
        embed.add_field(name="👁️ Visibility", value="10km", inline=True)
        
        embed.add_field(
            name="🌾 Agricultural Advice",
            value="Good conditions for most farming activities. Consider light irrigation in the evening.",
            inline=False
        )
        
        embed.set_footer(text="Weather data updates every hour")
        
        return embed
    
    async def get_crop_embed(self, crop: str) -> discord.Embed:
        """Generate crop advice embed"""
        embed = discord.Embed(
            title=f"🌱 Growing Guide: {crop.title()}",
            color=0x4CAF50
        )
        
        embed.add_field(
            name="📅 Best Planting Season",
            value="Rainy season (May-July)",
            inline=True
        )
        
        embed.add_field(
            name="🌍 Soil Requirements",
            value="Well-drained, fertile soil",
            inline=True
        )
        
        embed.add_field(
            name="🧪 Fertilizer",
            value="NPK 15-15-15 at planting",
            inline=True
        )
        
        embed.add_field(
            name="💧 Watering",
            value="Regular, avoid waterlogging",
            inline=True
        )
        
        embed.add_field(
            name="⏰ Harvest Time",
            value="90-120 days",
            inline=True
        )
        
        embed.add_field(
            name="🌡️ Temperature Range",
            value="20-30°C optimal",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Current Season Tips",
            value="Monitor for pests and ensure adequate drainage. Consider mulching to retain moisture.",
            inline=False
        )
        
        return embed
    
    async def get_market_embed(self) -> discord.Embed:
        """Generate market prices embed"""
        embed = discord.Embed(
            title="💰 Current Market Prices",
            description="Latest crop prices from major markets",
            color=0xFF9800
        )
        
        prices = [
            ("🌾 Rice", "₦30,000 - ₦35,000/bag", "📈 +2%"),
            ("🌽 Maize", "₦25,000 - ₦28,000/bag", "📉 -1%"),
            ("🍅 Tomato", "₦45,000 - ₦55,000/ton", "📈 +5%"),
            ("🥜 Groundnut", "₦40,000 - ₦45,000/bag", "📊 Stable"),
            ("🫘 Beans", "₦35,000 - ₦38,000/bag", "📈 +3%"),
            ("🥔 Yam", "₦20,000 - ₦25,000/bag", "📉 -2%")
        ]
        
        for crop, price, trend in prices:
            embed.add_field(
                name=crop,
                value=f"{price}\n{trend}",
                inline=True
            )
        
        embed.add_field(
            name="📊 Market Analysis",
            value="Prices generally stable with seasonal variations. "
                  "Best selling time is typically end of month.",
            inline=False
        )
        
        embed.set_footer(text="Prices updated every 6 hours • Varies by location")
        
        return embed
    
    async def get_pest_embed(self, description: str) -> discord.Embed:
        """Generate pest control embed"""
        embed = discord.Embed(
            title="🐛 Pest Control Advice",
            description=f"Based on your description: *{description}*",
            color=0xF44336
        )
        
        embed.add_field(
            name="🎯 Recommended Treatment",
            value="• Neem oil spray (evening application)\n"
                  "• Remove affected plant parts\n"
                  "• Improve air circulation\n"
                  "• Monitor regularly",
            inline=False
        )
        
        embed.add_field(
            name="🌿 Organic Solution",
            value="Mix neem oil + liquid soap\nSpray in the evening",
            inline=True
        )
        
        embed.add_field(
            name="🧪 Chemical Option",
            value="Contact local extension officer\nfor specific pesticides",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Prevention",
            value="• Crop rotation\n• Companion planting\n• Regular monitoring\n• Good sanitation",
            inline=False
        )
        
        return embed
    
    async def generate_ai_response(self, content: str, user_id: int) -> str:
        """Generate AI response for natural language questions"""
        # This would integrate with the main AI engine
        # For now, return a contextual response
        
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['weather', 'rain', 'temperature', 'climate']):
            return ("I can help you with weather information! Use `!agri weather <location>` "
                   "for detailed forecasts and agricultural advice based on current conditions.")
        
        elif any(word in content_lower for word in ['crop', 'plant', 'grow', 'farming']):
            return ("I'd love to help with your crop questions! Use `!agri crops <crop_name>` "
                   "for specific growing guides, or ask me about planting seasons, fertilizers, or harvesting.")
        
        elif any(word in content_lower for word in ['pest', 'insect', 'bug', 'disease']):
            return ("For pest and disease issues, use `!agri pests <description>` and describe "
                   "what you're seeing. I can help identify the problem and suggest organic or chemical solutions.")
        
        elif any(word in content_lower for word in ['price', 'market', 'sell', 'buy']):
            return ("Check current market prices with `!agri market`! I can also help you "
                   "understand market trends and the best times to sell your produce.")
        
        else:
            return ("I'm here to help with all your farming questions! You can ask me about:\n"
                   "🌤️ Weather and climate\n🌱 Crop cultivation\n🐛 Pest control\n💰 Market prices\n\n"
                   "Use `!agri help` to see all available commands, or just keep asking questions!")

class DiscordIntegration:
    """Discord integration wrapper"""
    
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.bot = AgriSenseDiscordBot()
        self.logger = logging.getLogger(__name__)
    
    async def start_bot(self):
        """Start the Discord bot"""
        try:
            await self.bot.start(self.bot_token)
        except Exception as e:
            self.logger.error(f"Error starting Discord bot: {str(e)}")
            raise
    
    async def stop_bot(self):
        """Stop the Discord bot"""
        try:
            await self.bot.close()
        except Exception as e:
            self.logger.error(f"Error stopping Discord bot: {str(e)}")

# For running as standalone script
async def run_discord_bot(bot_token: str):
    """Run the Discord bot"""
    integration = DiscordIntegration(bot_token)
    await integration.start_bot()

if __name__ == "__main__":
    import asyncio
    
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    if not BOT_TOKEN:
        print("Please set DISCORD_BOT_TOKEN environment variable")
        exit(1)
    
    asyncio.run(run_discord_bot(BOT_TOKEN))