"""
Weather data fetching and processing module
"""

import requests
import datetime
import time
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Weather data structure"""
    timestamp: datetime.datetime
    temperature: float  # Celsius
    cloud_cover: float  # 0-100%
    solar_irradiance: float  # W/m²
    wind_speed: float  # m/s
    humidity: float  # %

class WeatherAPI:
    """Weather API client with rate limiting"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.last_request_time = 0
        self.min_request_interval = 1.0  # seconds
    
    def _rate_limit(self):
        """Implement basic rate limiting"""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
    
    def get_current_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        """Get current weather data"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return WeatherData(
                timestamp=datetime.datetime.now(),
                temperature=data['main']['temp'],
                cloud_cover=data['clouds']['all'],
                solar_irradiance=self._estimate_solar_irradiance(
                    data['clouds']['all'],
                    datetime.datetime.now()
                ),
                wind_speed=data['wind']['speed'],
                humidity=data['main']['humidity']
            )
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching current weather: {e}")
            return None
        except KeyError as e:
            print(f"Error parsing weather data: {e}")
            return None
    
    def get_forecast(self, lat: float, lon: float, days: int = 5) -> List[WeatherData]:
        """Get weather forecast for specified days"""
        self._rate_limit()
        
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            forecast_list = []
            
            for item in data['list']:
                timestamp = datetime.datetime.fromtimestamp(item['dt'])
                
                weather_data = WeatherData(
                    timestamp=timestamp,
                    temperature=item['main']['temp'],
                    cloud_cover=item['clouds']['all'],
                    solar_irradiance=self._estimate_solar_irradiance(
                        item['clouds']['all'],
                        timestamp
                    ),
                    wind_speed=item['wind']['speed'],
                    humidity=item['main']['humidity']
                )
                
                forecast_list.append(weather_data)
            
            return forecast_list
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather forecast: {e}")
            return []
        except KeyError as e:
            print(f"Error parsing forecast data: {e}")
            return []
    
    def _estimate_solar_irradiance(self, cloud_cover: float, timestamp: datetime.datetime) -> float:
        """
        Estimate solar irradiance based on cloud cover and sun position
        This is a simplified calculation - in reality, you'd want more sophisticated models
        """
        # Maximum solar irradiance at sea level (W/m²)
        max_irradiance = 1000
        
        # Calculate sun angle based on time of day (simplified)
        hour = timestamp.hour
        
        # Simple sun elevation calculation (0 at night, 1 at noon)
        if hour < 6 or hour > 18:
            sun_elevation = 0
        else:
            sun_elevation = abs(math.sin(math.pi * (hour - 6) / 12))
        
        # Account for cloud cover (0-100% -> 0-1)
        cloud_factor = 1 - (cloud_cover / 100) * 0.8  # Clouds reduce irradiance by up to 80%
        
        # Calculate estimated irradiance
        irradiance = max_irradiance * sun_elevation * cloud_factor
        
        return max(0, irradiance)

def get_sample_weather_data() -> List[WeatherData]:
    """Generate sample weather data for testing without API calls"""
    sample_data = []
    now = datetime.datetime.now()
    
    # Generate 24 hours of sample data
    for hour in range(24):
        timestamp = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Simulate daily temperature variation
        base_temp = 20 + 10 * math.sin(2 * math.pi * hour / 24)
        
        # Simulate cloud cover variation
        cloud_cover = 30 + 40 * math.sin(2 * math.pi * hour / 24 + math.pi/4)
        cloud_cover = max(0, min(100, cloud_cover))
        
        # Calculate solar irradiance
        if hour < 6 or hour > 18:
            irradiance = 0
        else:
            sun_factor = math.sin(math.pi * (hour - 6) / 12)
            cloud_factor = 1 - (cloud_cover / 100) * 0.8
            irradiance = 1000 * sun_factor * cloud_factor
        
        sample_data.append(WeatherData(
            timestamp=timestamp,
            temperature=base_temp,
            cloud_cover=cloud_cover,
            solar_irradiance=max(0, irradiance),
            wind_speed=3.0,
            humidity=60.0
        ))
    
    return sample_data

import math