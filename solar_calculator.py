"""
Solar PV output calculation module
"""

import math
import datetime
from typing import List, Tuple
from dataclasses import dataclass
from weather import WeatherData

@dataclass
class SolarConfig:
    """Configuration for solar panel system"""
    panel_wattage: float  # Watts per panel
    panel_count: int
    efficiency: float  # 0-1 (18% = 0.18)
    tilt_angle: float  # degrees
    azimuth_angle: float  # degrees (180 = south-facing)
    location: dict  # {'lat': latitude, 'lon': longitude}

class SolarCalculator:
    """Calculate solar PV output based on weather conditions and system specifications"""
    
    def __init__(self, config: SolarConfig):
        self.config = config
        self.latitude = math.radians(config.location['lat'])
    
    def calculate_solar_output(self, weather_data: WeatherData) -> float:
        """
        Calculate solar PV output in kW for given weather conditions
        
        Args:
            weather_data: WeatherData object with irradiance, temperature, etc.
            
        Returns:
            Solar output in kW
        """
        # Base calculation: Panel area * efficiency * irradiance
        panel_area = self.config.panel_count * 2.0  # Assume 2 m² per panel
        base_output = (panel_area * self.config.efficiency * 
                      weather_data.solar_irradiance) / 1000  # Convert to kW
        
        # Apply temperature coefficient (panels are less efficient when hot)
        temp_coefficient = -0.004  # -0.4% per degree C above 25°C
        temp_factor = 1 + temp_coefficient * (weather_data.temperature - 25)
        
        # Apply tilt and orientation factors
        angle_factor = self._calculate_angle_factor(weather_data.timestamp)
        
        # Apply cloud cover factor (already included in irradiance calculation)
        
        output = base_output * temp_factor * angle_factor
        
        return max(0, output)
    
    def _calculate_angle_factor(self, timestamp: datetime.datetime) -> float:
        """
        Calculate the factor for panel tilt and orientation
        Simplified calculation - in reality, this would be more complex
        """
        # Day of year for seasonal adjustment
        day_of_year = timestamp.timetuple().tm_yday
        
        # Solar declination angle (simplified)
        declination = 23.45 * math.sin(math.radians(360 * (284 + day_of_year) / 365))
        declination = math.radians(declination)
        
        # Hour angle
        hour = timestamp.hour + timestamp.minute / 60.0
        hour_angle = math.radians(15 * (hour - 12))
        
        # Solar elevation angle
        elevation = math.asin(
            math.sin(declination) * math.sin(self.latitude) +
            math.cos(declination) * math.cos(self.latitude) * math.cos(hour_angle)
        )
        
        # Solar azimuth angle (simplified)
        azimuth = math.atan2(
            math.sin(hour_angle),
            math.cos(hour_angle) * math.sin(self.latitude) - 
            math.tan(declination) * math.cos(self.latitude)
        )
        
        # Angle of incidence on tilted panel
        panel_tilt = math.radians(self.config.tilt_angle)
        panel_azimuth = math.radians(self.config.azimuth_angle - 180)  # Convert to math convention
        
        cos_incidence = (
            math.sin(elevation) * math.cos(panel_tilt) +
            math.cos(elevation) * math.sin(panel_tilt) * 
            math.cos(azimuth - panel_azimuth)
        )
        
        # Factor based on angle of incidence
        angle_factor = max(0, cos_incidence)
        
        return angle_factor
    
    def calculate_daily_production(self, weather_forecast: List[WeatherData]) -> List[Tuple[datetime.datetime, float]]:
        """
        Calculate hourly solar production for a day
        
        Args:
            weather_forecast: List of hourly weather data
            
        Returns:
            List of (timestamp, output_kW) tuples
        """
        production_schedule = []
        
        for weather in weather_forecast:
            output = self.calculate_solar_output(weather)
            production_schedule.append((weather.timestamp, output))
        
        return production_schedule
    
    def get_production_categories(self, production_schedule: List[Tuple[datetime.datetime, float]]) -> List[Tuple[datetime.datetime, str]]:
        """
        Categorize production levels into green/yellow/red periods
        
        Args:
            production_schedule: List of (timestamp, output_kW) tuples
            
        Returns:
            List of (timestamp, category) tuples
        """
        # Calculate system capacity
        system_capacity = (self.config.panel_count * self.config.panel_wattage) / 1000  # kW
        
        categories = []
        
        for timestamp, output in production_schedule:
            # Define thresholds as percentages of system capacity
            if output >= system_capacity * 0.7:
                category = "green"  # High production
            elif output >= system_capacity * 0.3:
                category = "yellow"  # Medium production
            else:
                category = "red"  # Low production
            
            categories.append((timestamp, category))
        
        return categories
    
    def estimate_battery_charging(self, production_schedule: List[Tuple[datetime.datetime, float]], 
                                 base_load: float = 2.0) -> List[Tuple[datetime.datetime, float]]:
        """
        Estimate excess energy available for battery charging or high-energy appliances
        
        Args:
            production_schedule: List of (timestamp, output_kW) tuples
            base_load: Base household load in kW
            
        Returns:
            List of (timestamp, excess_kW) tuples
        """
        excess_schedule = []
        
        for timestamp, output in production_schedule:
            excess = max(0, output - base_load)
            excess_schedule.append((timestamp, excess))
        
        return excess_schedule
    
    def get_optimal_time_windows(self, production_schedule: List[Tuple[datetime.datetime, float]], 
                               min_power: float, duration_hours: float) -> List[Tuple[datetime.datetime, datetime.datetime]]:
        """
        Find optimal time windows for running high-energy appliances
        
        Args:
            production_schedule: List of (timestamp, output_kW) tuples
            min_power: Minimum power required in kW
            duration_hours: Duration the appliance needs to run
            
        Returns:
            List of (start_time, end_time) tuples for optimal windows
        """
        optimal_windows = []
        
        # Simple algorithm: find consecutive hours with sufficient power
        current_window_start = None
        current_window_duration = 0
        
        for i, (timestamp, output) in enumerate(production_schedule):
            if output >= min_power:
                if current_window_start is None:
                    current_window_start = timestamp
                    current_window_duration = 1
                else:
                    current_window_duration += 1
                
                # Check if we have enough duration
                if current_window_duration >= duration_hours:
                    window_end = timestamp
                    optimal_windows.append((current_window_start, window_end))
                    current_window_start = None
                    current_window_duration = 0
            else:
                current_window_start = None
                current_window_duration = 0
        
        return optimal_windows