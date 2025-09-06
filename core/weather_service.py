"""
AgriSense AI - Weather Service
Advanced weather data integration for agricultural decision making
"""

import os
import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

class WeatherService:
    """Advanced weather service for agricultural applications"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
        self.geolocator = Nominatim(user_agent="agrisense-ai")
        
        # Agricultural weather thresholds
        self.thresholds = {
            'temperature': {
                'heat_stress': 35,  # °C
                'cold_stress': 10,  # °C
                'optimal_min': 20,  # °C
                'optimal_max': 30   # °C
            },
            'humidity': {
                'low': 30,      # %
                'high': 80,     # %
                'optimal': 60   # %
            },
            'wind_speed': {
                'high': 10,     # m/s
                'very_high': 15 # m/s
            },
            'rainfall': {
                'light': 2.5,   # mm/day
                'moderate': 10, # mm/day
                'heavy': 50     # mm/day
            }
        }
        
        # Crop-specific weather requirements
        self.crop_requirements = {
            'rice': {
                'water_need': 'high',
                'temp_range': (20, 35),
                'humidity_preference': 'high',
                'critical_stages': ['flowering', 'grain_filling']
            },
            'maize': {
                'water_need': 'moderate',
                'temp_range': (18, 32),
                'humidity_preference': 'moderate',
                'critical_stages': ['silking', 'grain_filling']
            },
            'tomato': {
                'water_need': 'high',
                'temp_range': (15, 29),
                'humidity_preference': 'moderate',
                'critical_stages': ['flowering', 'fruit_development']
            },
            'cassava': {
                'water_need': 'low',
                'temp_range': (25, 35),
                'humidity_preference': 'moderate',
                'critical_stages': ['root_development']
            }
        }
    
    def get_coordinates(self, location: str) -> Optional[tuple]:
        """Get latitude and longitude for a location"""
        try:
            # Handle Nigerian locations specifically
            if not any(word in location.lower() for word in ['nigeria', 'ng']):
                location = f"{location}, Nigeria"
            
            location_data = self.geolocator.geocode(location, timeout=10)
            if location_data:
                return (location_data.latitude, location_data.longitude)
            return None
            
        except GeocoderTimedOut:
            self.logger.warning(f"Geocoding timeout for location: {location}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting coordinates for {location}: {str(e)}")
            return None
    
    def get_weather(self, location: str) -> Dict[str, Any]:
        """Get current weather data for a location"""
        try:
            coords = self.get_coordinates(location)
            if not coords:
                return self._get_fallback_weather(location)
            
            lat, lon = coords
            
            # Get current weather
            current_url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(current_url, params=params, timeout=10)
            response.raise_for_status()
            
            weather_data = response.json()
            
            # Process and enhance weather data
            processed_data = self._process_weather_data(weather_data)
            processed_data['location'] = location
            processed_data['coordinates'] = coords
            
            return processed_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Weather API request failed for {location}: {str(e)}")
            return self._get_fallback_weather(location)
        except Exception as e:
            self.logger.error(f"Error getting weather for {location}: {str(e)}")
            return self._get_fallback_weather(location)
    
    def get_forecast(self, location: str, days: int = 5) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        try:
            coords = self.get_coordinates(location)
            if not coords:
                return self._get_fallback_forecast(location)
            
            lat, lon = coords
            
            # Get 5-day forecast
            forecast_url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(forecast_url, params=params, timeout=10)
            response.raise_for_status()
            
            forecast_data = response.json()
            
            # Process forecast data
            processed_forecast = self._process_forecast_data(forecast_data, days)
            processed_forecast['location'] = location
            processed_forecast['coordinates'] = coords
            
            return processed_forecast
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Forecast API request failed for {location}: {str(e)}")
            return self._get_fallback_forecast(location)
        except Exception as e:
            self.logger.error(f"Error getting forecast for {location}: {str(e)}")
            return self._get_fallback_forecast(location)
    
    def get_agricultural_advice(self, weather_data: Dict[str, Any], crop: str = None) -> Dict[str, Any]:
        """Generate agricultural advice based on weather conditions"""
        try:
            advice = {
                'alerts': [],
                'recommendations': [],
                'irrigation_advice': '',
                'planting_advice': '',
                'harvesting_advice': '',
                'pest_risk': 'low'
            }
            
            temp = weather_data.get('temperature', {}).get('current', 25)
            humidity = weather_data.get('humidity', 50)
            wind_speed = weather_data.get('wind_speed', 0)
            rainfall = weather_data.get('rainfall', {}).get('today', 0)
            
            # Temperature-based advice
            if temp > self.thresholds['temperature']['heat_stress']:
                advice['alerts'].append({
                    'type': 'heat_stress',
                    'severity': 'high',
                    'message': f"Extreme heat alert: {temp}°C. Crops at risk of heat stress."
                })
                advice['recommendations'].append("Increase irrigation frequency")
                advice['recommendations'].append("Provide shade for sensitive crops")
                advice['irrigation_advice'] = "Irrigate early morning and evening"
            
            elif temp < self.thresholds['temperature']['cold_stress']:
                advice['alerts'].append({
                    'type': 'cold_stress',
                    'severity': 'medium',
                    'message': f"Cold weather alert: {temp}°C. Protect sensitive crops."
                })
                advice['recommendations'].append("Cover young plants")
                advice['recommendations'].append("Delay planting if possible")
            
            # Humidity-based advice
            if humidity > self.thresholds['humidity']['high']:
                advice['pest_risk'] = 'high'
                advice['recommendations'].append("Monitor for fungal diseases")
                advice['recommendations'].append("Ensure good air circulation")
            
            elif humidity < self.thresholds['humidity']['low']:
                advice['recommendations'].append("Increase irrigation to raise humidity")
                advice['recommendations'].append("Use mulching to retain moisture")
            
            # Wind-based advice
            if wind_speed > self.thresholds['wind_speed']['very_high']:
                advice['alerts'].append({
                    'type': 'high_wind',
                    'severity': 'high',
                    'message': f"Very strong winds: {wind_speed} m/s. Protect crops."
                })
                advice['recommendations'].append("Secure tall crops and structures")
                advice['recommendations'].append("Postpone spraying activities")
            
            # Rainfall-based advice
            if rainfall > self.thresholds['rainfall']['heavy']:
                advice['alerts'].append({
                    'type': 'heavy_rain',
                    'severity': 'medium',
                    'message': f"Heavy rainfall expected: {rainfall}mm. Ensure drainage."
                })
                advice['irrigation_advice'] = "Skip irrigation today"
                advice['recommendations'].append("Check drainage systems")
                advice['recommendations'].append("Protect crops from waterlogging")
            
            elif rainfall < self.thresholds['rainfall']['light']:
                advice['irrigation_advice'] = "Increase irrigation frequency"
                advice['recommendations'].append("Monitor soil moisture closely")
            
            # Crop-specific advice
            if crop and crop.lower() in self.crop_requirements:
                crop_advice = self._get_crop_specific_advice(weather_data, crop.lower())
                advice.update(crop_advice)
            
            # Planting advice based on conditions
            advice['planting_advice'] = self._get_planting_advice(weather_data)
            advice['harvesting_advice'] = self._get_harvesting_advice(weather_data)
            
            return advice
            
        except Exception as e:
            self.logger.error(f"Error generating agricultural advice: {str(e)}")
            return {'error': 'Failed to generate agricultural advice'}
    
    def _process_weather_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and enhance raw weather data"""
        try:
            processed = {
                'timestamp': datetime.utcnow().isoformat(),
                'temperature': {
                    'current': round(data['main']['temp'], 1),
                    'feels_like': round(data['main']['feels_like'], 1),
                    'min': round(data['main']['temp_min'], 1),
                    'max': round(data['main']['temp_max'], 1)
                },
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'wind_speed': data['wind'].get('speed', 0),
                'wind_direction': data['wind'].get('deg', 0),
                'cloudiness': data['clouds']['all'],
                'visibility': data.get('visibility', 10000) / 1000,  # Convert to km
                'weather': {
                    'main': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'icon': data['weather'][0]['icon']
                },
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                'rainfall': {
                    'today': data.get('rain', {}).get('1h', 0)
                }
            }
            
            # Add agricultural assessments
            processed['agricultural_conditions'] = self._assess_agricultural_conditions(processed)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing weather data: {str(e)}")
            return {}
    
    def _process_forecast_data(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Process forecast data for agricultural use"""
        try:
            processed = {
                'timestamp': datetime.utcnow().isoformat(),
                'forecast': []
            }
            
            # Group forecasts by day
            daily_forecasts = {}
            for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
                date = datetime.fromtimestamp(item['dt']).date()
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            # Process each day
            for date, forecasts in list(daily_forecasts.items())[:days]:
                daily_data = self._process_daily_forecast(date, forecasts)
                processed['forecast'].append(daily_data)
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing forecast data: {str(e)}")
            return {'forecast': []}
    
    def _process_daily_forecast(self, date, forecasts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process forecast data for a single day"""
        temps = [f['main']['temp'] for f in forecasts]
        humidity_values = [f['main']['humidity'] for f in forecasts]
        wind_speeds = [f['wind'].get('speed', 0) for f in forecasts]
        rainfall = sum([f.get('rain', {}).get('3h', 0) for f in forecasts])
        
        return {
            'date': date.strftime('%Y-%m-%d'),
            'day_name': date.strftime('%A'),
            'temperature': {
                'min': round(min(temps), 1),
                'max': round(max(temps), 1),
                'avg': round(sum(temps) / len(temps), 1)
            },
            'humidity': {
                'avg': round(sum(humidity_values) / len(humidity_values), 1)
            },
            'wind_speed': {
                'avg': round(sum(wind_speeds) / len(wind_speeds), 1),
                'max': round(max(wind_speeds), 1)
            },
            'rainfall': round(rainfall, 1),
            'weather': forecasts[len(forecasts)//2]['weather'][0]['description'],  # Midday weather
            'agricultural_advice': self._get_daily_agricultural_advice(date, {
                'temp_min': min(temps),
                'temp_max': max(temps),
                'humidity': sum(humidity_values) / len(humidity_values),
                'rainfall': rainfall,
                'wind_speed': max(wind_speeds)
            })
        }
    
    def _assess_agricultural_conditions(self, weather: Dict[str, Any]) -> Dict[str, Any]:
        """Assess current weather conditions for agriculture"""
        temp = weather['temperature']['current']
        humidity = weather['humidity']
        wind_speed = weather['wind_speed']
        
        conditions = {
            'overall_rating': 'good',
            'temperature_status': 'optimal',
            'humidity_status': 'optimal',
            'wind_status': 'calm',
            'irrigation_needed': False,
            'pest_risk_level': 'low'
        }
        
        # Temperature assessment
        if temp > self.thresholds['temperature']['heat_stress']:
            conditions['temperature_status'] = 'too_hot'
            conditions['overall_rating'] = 'poor'
            conditions['irrigation_needed'] = True
        elif temp < self.thresholds['temperature']['cold_stress']:
            conditions['temperature_status'] = 'too_cold'
            conditions['overall_rating'] = 'poor'
        elif temp < self.thresholds['temperature']['optimal_min'] or temp > self.thresholds['temperature']['optimal_max']:
            conditions['temperature_status'] = 'suboptimal'
            conditions['overall_rating'] = 'fair'
        
        # Humidity assessment
        if humidity > self.thresholds['humidity']['high']:
            conditions['humidity_status'] = 'too_high'
            conditions['pest_risk_level'] = 'high'
        elif humidity < self.thresholds['humidity']['low']:
            conditions['humidity_status'] = 'too_low'
            conditions['irrigation_needed'] = True
        
        # Wind assessment
        if wind_speed > self.thresholds['wind_speed']['very_high']:
            conditions['wind_status'] = 'very_strong'
            conditions['overall_rating'] = 'poor'
        elif wind_speed > self.thresholds['wind_speed']['high']:
            conditions['wind_status'] = 'strong'
        
        return conditions
    
    def _get_crop_specific_advice(self, weather: Dict[str, Any], crop: str) -> Dict[str, Any]:
        """Get crop-specific weather advice"""
        if crop not in self.crop_requirements:
            return {}
        
        crop_info = self.crop_requirements[crop]
        temp = weather['temperature']['current']
        humidity = weather['humidity']
        
        advice = {
            'crop_specific_alerts': [],
            'crop_recommendations': []
        }
        
        # Temperature check for crop
        temp_min, temp_max = crop_info['temp_range']
        if temp < temp_min or temp > temp_max:
            advice['crop_specific_alerts'].append({
                'crop': crop,
                'message': f"Temperature {temp}°C is outside optimal range for {crop} ({temp_min}-{temp_max}°C)"
            })
        
        # Humidity check for crop
        if crop_info['humidity_preference'] == 'high' and humidity < 60:
            advice['crop_recommendations'].append(f"Increase humidity around {crop} plants")
        elif crop_info['humidity_preference'] == 'low' and humidity > 70:
            advice['crop_recommendations'].append(f"Improve ventilation around {crop} plants")
        
        return advice
    
    def _get_planting_advice(self, weather: Dict[str, Any]) -> str:
        """Get planting advice based on current weather"""
        temp = weather['temperature']['current']
        humidity = weather['humidity']
        rainfall = weather.get('rainfall', {}).get('today', 0)
        
        if temp < 15:
            return "Wait for warmer weather before planting"
        elif temp > 35:
            return "Too hot for planting. Wait for cooler conditions"
        elif rainfall > 20:
            return "Soil may be too wet for planting. Wait for drier conditions"
        elif humidity > 80:
            return "High humidity may increase disease risk for new plantings"
        else:
            return "Good conditions for planting"
    
    def _get_harvesting_advice(self, weather: Dict[str, Any]) -> str:
        """Get harvesting advice based on current weather"""
        rainfall = weather.get('rainfall', {}).get('today', 0)
        humidity = weather['humidity']
        wind_speed = weather['wind_speed']
        
        if rainfall > 5:
            return "Delay harvesting due to rain. Wait for dry conditions"
        elif humidity > 85:
            return "High humidity may affect crop quality during harvest"
        elif wind_speed > 15:
            return "Strong winds may make harvesting difficult"
        else:
            return "Good conditions for harvesting"
    
    def _get_daily_agricultural_advice(self, date, weather_summary: Dict[str, Any]) -> str:
        """Get agricultural advice for a specific day"""
        temp_max = weather_summary['temp_max']
        rainfall = weather_summary['rainfall']
        
        if rainfall > 20:
            return "Heavy rain expected. Skip irrigation and protect crops from waterlogging."
        elif temp_max > 35:
            return "Very hot day ahead. Ensure adequate irrigation and provide shade if possible."
        elif temp_max < 15:
            return "Cool day. Monitor cold-sensitive crops and consider protection."
        elif rainfall > 5:
            return "Some rain expected. Reduce irrigation and monitor field conditions."
        else:
            return "Generally favorable conditions for farming activities."
    
    def _get_fallback_weather(self, location: str) -> Dict[str, Any]:
        """Provide fallback weather data when API is unavailable"""
        return {
            'location': location,
            'error': 'Weather service unavailable',
            'fallback': True,
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': {'current': 28, 'min': 22, 'max': 34},
            'humidity': 65,
            'weather': {'description': 'partly cloudy'},
            'agricultural_advice': {
                'recommendations': ['Monitor crops regularly', 'Maintain normal irrigation schedule'],
                'alerts': [{'type': 'service_unavailable', 'message': 'Weather data unavailable. Use local observations.'}]
            }
        }
    
    def _get_fallback_forecast(self, location: str) -> Dict[str, Any]:
        """Provide fallback forecast when API is unavailable"""
        return {
            'location': location,
            'error': 'Forecast service unavailable',
            'fallback': True,
            'timestamp': datetime.utcnow().isoformat(),
            'forecast': []
        }