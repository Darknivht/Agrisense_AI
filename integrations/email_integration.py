"""
AgriSense AI - Email Integration
Advanced email service for newsletters, alerts, and notifications
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import aiosmtplib
from jinja2 import Template

class EmailIntegration:
    """Email integration for AgriSense AI"""
    
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port)
        self.username = username
        self.password = password
        self.logger = logging.getLogger(__name__)
        
        # Email templates
        self.templates = {
            'weather_alert': {
                'subject': '🌤️ AgriSense Weather Alert - {{location}}',
                'html': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Weather Alert</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #4CAF50, #2196F3); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
                        .alert-box { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 8px; margin: 15px 0; }
                        .weather-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; margin: 20px 0; }
                        .weather-item { background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>🌾 AgriSense Weather Alert</h2>
                            <p>{{location}} - {{date}}</p>
                        </div>
                        <div class="content">
                            {% if alert_message %}
                            <div class="alert-box">
                                <strong>⚠️ Alert:</strong> {{alert_message}}
                            </div>
                            {% endif %}
                            
                            <div class="weather-grid">
                                <div class="weather-item">
                                    <h4>🌡️ Temperature</h4>
                                    <p><strong>{{temperature}}°C</strong></p>
                                </div>
                                <div class="weather-item">
                                    <h4>☁️ Condition</h4>
                                    <p>{{condition}}</p>
                                </div>
                                <div class="weather-item">
                                    <h4>💧 Humidity</h4>
                                    <p>{{humidity}}%</p>
                                </div>
                                <div class="weather-item">
                                    <h4>🌧️ Rainfall</h4>
                                    <p>{{rainfall}}mm</p>
                                </div>
                            </div>
                            
                            <h3>🌾 Agricultural Recommendations:</h3>
                            <ul>
                                {% for recommendation in recommendations %}
                                <li>{{recommendation}}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        <div class="footer">
                            <p>AgriSense AI - Smart Agricultural Intelligence</p>
                            <p>Unsubscribe: <a href="{{unsubscribe_link}}">Click here</a></p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            },
            
            'market_newsletter': {
                'subject': '💰 AgriSense Market Newsletter - {{date}}',
                'html': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Market Newsletter</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #FF9800, #4CAF50); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
                        .price-table { width: 100%; border-collapse: collapse; margin: 20px 0; background: white; border-radius: 8px; overflow: hidden; }
                        .price-table th, .price-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                        .price-table th { background: #4CAF50; color: white; }
                        .trend-up { color: #4CAF50; font-weight: bold; }
                        .trend-down { color: #f44336; font-weight: bold; }
                        .trend-stable { color: #FF9800; font-weight: bold; }
                        .insights-box { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>💰 Market Newsletter</h2>
                            <p>{{date}} - Current Crop Prices</p>
                        </div>
                        <div class="content">
                            <h3>📊 Current Market Prices</h3>
                            <table class="price-table">
                                <thead>
                                    <tr>
                                        <th>Crop</th>
                                        <th>Price Range</th>
                                        <th>Trend</th>
                                        <th>Change</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for price in prices %}
                                    <tr>
                                        <td>{{price.crop}}</td>
                                        <td>{{price.range}}</td>
                                        <td class="trend-{{price.trend_class}}">{{price.trend}}</td>
                                        <td class="trend-{{price.trend_class}}">{{price.change}}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                            
                            <div class="insights-box">
                                <h3>💡 Market Insights</h3>
                                <ul>
                                    {% for insight in insights %}
                                    <li>{{insight}}</li>
                                    {% endfor %}
                                </ul>
                            </div>
                            
                            <h3>🎯 Selling Recommendations</h3>
                            <ul>
                                {% for recommendation in selling_tips %}
                                <li>{{recommendation}}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        <div class="footer">
                            <p>AgriSense AI - Smart Agricultural Intelligence</p>
                            <p>Unsubscribe: <a href="{{unsubscribe_link}}">Click here</a></p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            },
            
            'weekly_tips': {
                'subject': '🌱 AgriSense Weekly Farming Tips - Week {{week_number}}',
                'html': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Weekly Tips</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #4CAF50, #8BC34A); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
                        .tip-card { background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4CAF50; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .tip-icon { font-size: 24px; margin-bottom: 10px; }
                        .tip-title { font-size: 18px; font-weight: bold; color: #4CAF50; margin-bottom: 10px; }
                        .seasonal-box { background: #fff3cd; padding: 15px; border-radius: 8px; margin: 20px 0; }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>🌱 Weekly Farming Tips</h2>
                            <p>Week {{week_number}} - {{date_range}}</p>
                        </div>
                        <div class="content">
                            <div class="seasonal-box">
                                <strong>🗓️ This Week's Focus:</strong> {{weekly_focus}}
                            </div>
                            
                            {% for tip in tips %}
                            <div class="tip-card">
                                <div class="tip-icon">{{tip.icon}}</div>
                                <div class="tip-title">{{tip.title}}</div>
                                <p>{{tip.description}}</p>
                                {% if tip.action_items %}
                                <ul>
                                    {% for action in tip.action_items %}
                                    <li>{{action}}</li>
                                    {% endfor %}
                                </ul>
                                {% endif %}
                            </div>
                            {% endfor %}
                            
                            <div class="seasonal-box">
                                <h3>📅 Next Week Preview</h3>
                                <p>{{next_week_preview}}</p>
                            </div>
                        </div>
                        <div class="footer">
                            <p>AgriSense AI - Smart Agricultural Intelligence</p>
                            <p>Unsubscribe: <a href="{{unsubscribe_link}}">Click here</a></p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            },
            
            'document_analysis': {
                'subject': '📚 Your Document Analysis is Ready - AgriSense AI',
                'html': '''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Document Analysis</title>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #9C27B0, #673AB7); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
                        .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }
                        .doc-info { background: white; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #9C27B0; }
                        .insights-section { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
                        .key-points { background: #f3e5f5; padding: 15px; border-radius: 8px; margin: 15px 0; }
                        .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>📚 Document Analysis Complete</h2>
                            <p>AI-Powered Agricultural Insights</p>
                        </div>
                        <div class="content">
                            <div class="doc-info">
                                <h3>📄 Document Details</h3>
                                <p><strong>Filename:</strong> {{filename}}</p>
                                <p><strong>Analyzed:</strong> {{analysis_date}}</p>
                                <p><strong>Pages:</strong> {{page_count}}</p>
                                <p><strong>Language:</strong> {{language}}</p>
                            </div>
                            
                            <div class="insights-section">
                                <h3>🔍 Key Insights</h3>
                                <div class="key-points">
                                    <h4>🎯 Main Topics Covered:</h4>
                                    <ul>
                                        {% for topic in main_topics %}
                                        <li>{{topic}}</li>
                                        {% endfor %}
                                    </ul>
                                </div>
                                
                                <h4>📊 Summary:</h4>
                                <p>{{summary}}</p>
                                
                                <h4>💡 Actionable Recommendations:</h4>
                                <ul>
                                    {% for recommendation in recommendations %}
                                    <li>{{recommendation}}</li>
                                    {% endfor %}
                                </ul>
                                
                                <h4>🔗 Related Resources:</h4>
                                <ul>
                                    {% for resource in related_resources %}
                                    <li><a href="{{resource.url}}">{{resource.title}}</a></li>
                                    {% endfor %}
                                </ul>
                            </div>
                            
                            <p><strong>💬 Ask Questions:</strong> You can now ask specific questions about this document through any of our platforms (WhatsApp, Telegram, Discord, or our web app).</p>
                        </div>
                        <div class="footer">
                            <p>AgriSense AI - Smart Agricultural Intelligence</p>
                            <p>Access your documents: <a href="{{dashboard_link}}">Dashboard</a></p>
                        </div>
                    </div>
                </body>
                </html>
                '''
            }
        }
    
    async def send_email(self, to_email: str, subject: str, html_content: str, text_content: Optional[str] = None) -> bool:
        """Send a single email"""
        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.username
            message['To'] = to_email
            
            # Add text content if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                message.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)
            
            # Send email using aiosmtplib for async operation
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.username,
                password=self.password
            )
            
            self.logger.info(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_bulk_email(self, email_addresses: List[str], subject: str, html_content: str, text_content: Optional[str] = None) -> Dict[str, bool]:
        """Send bulk emails"""
        results = {}
        
        # Send emails in batches to avoid overwhelming the SMTP server
        batch_size = 10
        for i in range(0, len(email_addresses), batch_size):
            batch = email_addresses[i:i + batch_size]
            
            # Send batch concurrently
            tasks = [
                self.send_email(email, subject, html_content, text_content)
                for email in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Store results
            for email, result in zip(batch, batch_results):
                results[email] = result if isinstance(result, bool) else False
            
            # Add small delay between batches
            if i + batch_size < len(email_addresses):
                await asyncio.sleep(1)
        
        success_count = sum(1 for success in results.values() if success)
        self.logger.info(f"📧 Bulk email sent: {success_count}/{len(email_addresses)} successful")
        
        return results
    
    async def send_weather_alert(self, email_addresses: List[str], weather_data: Dict[str, Any]) -> Dict[str, bool]:
        """Send weather alert email"""
        try:
            template = Template(self.templates['weather_alert']['html'])
            subject_template = Template(self.templates['weather_alert']['subject'])
            
            html_content = template.render(**weather_data)
            subject = subject_template.render(**weather_data)
            
            return await self.send_bulk_email(email_addresses, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Error sending weather alert emails: {str(e)}")
            return {email: False for email in email_addresses}
    
    async def send_market_newsletter(self, email_addresses: List[str], market_data: Dict[str, Any]) -> Dict[str, bool]:
        """Send market newsletter"""
        try:
            template = Template(self.templates['market_newsletter']['html'])
            subject_template = Template(self.templates['market_newsletter']['subject'])
            
            html_content = template.render(**market_data)
            subject = subject_template.render(**market_data)
            
            return await self.send_bulk_email(email_addresses, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Error sending market newsletter: {str(e)}")
            return {email: False for email in email_addresses}
    
    async def send_weekly_tips(self, email_addresses: List[str], tips_data: Dict[str, Any]) -> Dict[str, bool]:
        """Send weekly farming tips"""
        try:
            template = Template(self.templates['weekly_tips']['html'])
            subject_template = Template(self.templates['weekly_tips']['subject'])
            
            html_content = template.render(**tips_data)
            subject = subject_template.render(**tips_data)
            
            return await self.send_bulk_email(email_addresses, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Error sending weekly tips: {str(e)}")
            return {email: False for email in email_addresses}
    
    async def send_document_analysis(self, email: str, analysis_data: Dict[str, Any]) -> bool:
        """Send document analysis results"""
        try:
            template = Template(self.templates['document_analysis']['html'])
            subject_template = Template(self.templates['document_analysis']['subject'])
            
            html_content = template.render(**analysis_data)
            subject = subject_template.render(**analysis_data)
            
            return await self.send_email(email, subject, html_content)
            
        except Exception as e:
            self.logger.error(f"Error sending document analysis email: {str(e)}")
            return False
    
    async def send_welcome_email(self, email: str, user_data: Dict[str, Any]) -> bool:
        """Send welcome email to new users"""
        try:
            welcome_html = f'''
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to AgriSense AI</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #4CAF50, #2196F3); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .feature-box {{ background: white; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #4CAF50; }}
                    .cta-button {{ background: #4CAF50; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; display: inline-block; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🌾 Welcome to AgriSense AI!</h1>
                        <p>Your Smart Agricultural Intelligence Partner</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user_data.get('name', 'Farmer')}! 👋</h2>
                        
                        <p>Thank you for joining AgriSense AI! We're excited to help you optimize your farming with the power of artificial intelligence.</p>
                        
                        <div class="feature-box">
                            <h3>🤖 AI-Powered Assistance</h3>
                            <p>Get instant answers to your farming questions through multiple platforms.</p>
                        </div>
                        
                        <div class="feature-box">
                            <h3>🌤️ Weather Intelligence</h3>
                            <p>Receive real-time weather alerts and agricultural recommendations.</p>
                        </div>
                        
                        <div class="feature-box">
                            <h3>💰 Market Insights</h3>
                            <p>Stay updated with crop prices and market trends.</p>
                        </div>
                        
                        <div class="feature-box">
                            <h3>📚 Document Analysis</h3>
                            <p>Upload agricultural PDFs and get AI-powered insights.</p>
                        </div>
                        
                        <div class="feature-box">
                            <h3>🌐 Multi-Platform Access</h3>
                            <p>Connect through WhatsApp, Telegram, Discord, or our web app.</p>
                        </div>
                        
                        <center>
                            <a href="{user_data.get('dashboard_link', '#')}" class="cta-button">Get Started Now 🚀</a>
                        </center>
                        
                        <h3>📱 Connect with us on:</h3>
                        <ul>
                            <li><strong>WhatsApp:</strong> Message us at {user_data.get('whatsapp_number', '+234-XXX-XXXX')}</li>
                            <li><strong>Telegram:</strong> Search for @AgriSenseBot</li>
                            <li><strong>Discord:</strong> Join our farming community server</li>
                            <li><strong>Web App:</strong> Access your dashboard anytime</li>
                        </ul>
                        
                        <p>If you have any questions, just reply to this email or reach out through any of our platforms!</p>
                        
                        <p>Happy farming! 🌱</p>
                        <p><strong>The AgriSense AI Team</strong></p>
                    </div>
                    <div class="footer">
                        <p>AgriSense AI - Smart Agricultural Intelligence</p>
                        <p>Unsubscribe: <a href="{user_data.get('unsubscribe_link', '#')}">Click here</a></p>
                    </div>
                </div>
            </body>
            </html>
            '''
            
            return await self.send_email(
                email,
                "🌾 Welcome to AgriSense AI - Your Smart Farming Partner!",
                welcome_html
            )
            
        except Exception as e:
            self.logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            server.quit()
            
            self.logger.info("✅ Email connection test successful")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Email connection test failed: {str(e)}")
            return False