#!/usr/bin/env python3
"""
Solar Energy Optimizer
A Python application to optimize electricity usage based on solar PV production and weather forecasts.
"""

import json
import sqlite3
import datetime
from typing import Dict, List, Tuple, Optional

from weather import WeatherAPI, WeatherData, get_sample_weather_data
from solar_calculator import SolarCalculator, SolarConfig
from scheduler import ApplianceScheduler, Appliance, ScheduleItem, Priority

class SolarOptimizer:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.db_path = "solar_data.db"
        self.api_key = None
        self.solar_config = None
        self.appliances = []
        self.weather_api = None
        self.solar_calculator = None
        self.scheduler = None
        
        self.init_database()
        self.load_config()
        self.init_components()
    
    def init_database(self):
        """Initialize SQLite database for historical data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                temperature REAL,
                cloud_cover REAL,
                solar_irradiance REAL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solar_production (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                predicted_output REAL,
                actual_output REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_components(self):
        """Initialize API and calculator components"""
        if self.api_key and self.api_key != "YOUR_OPENWEATHERMAP_API_KEY":
            self.weather_api = WeatherAPI(self.api_key)
        
        if self.solar_config:
            self.solar_calculator = SolarCalculator(self.solar_config)
            self.scheduler = ApplianceScheduler(self.appliances)
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                
            self.api_key = config.get('api_key')
            
            solar_data = config.get('solar_system', {})
            self.solar_config = SolarConfig(
                panel_wattage=solar_data.get('panel_wattage', 300),
                panel_count=solar_data.get('panel_count', 20),
                efficiency=solar_data.get('efficiency', 0.18),
                tilt_angle=solar_data.get('tilt_angle', 30),
                azimuth_angle=solar_data.get('azimuth_angle', 180),
                location=solar_data.get('location', {'lat': 40.7128, 'lon': -74.0060})
            )
            
            # Convert appliance data to proper objects
            self.appliances = []
            for app_data in config.get('appliances', []):
                priority = Priority.MEDIUM
                if app_data.get('priority') == 'high':
                    priority = Priority.HIGH
                elif app_data.get('priority') == 'low':
                    priority = Priority.LOW
                
                appliance = Appliance(
                    name=app_data['name'],
                    power_rating=app_data['power_rating'],
                    duration=app_data['duration'],
                    flexibility=app_data['flexibility'],
                    priority=priority
                )
                self.appliances.append(appliance)
            
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found. Creating default configuration.")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration file"""
        default_config = {
            "api_key": "YOUR_OPENWEATHERMAP_API_KEY",
            "solar_system": {
                "panel_wattage": 300,
                "panel_count": 20,
                "efficiency": 0.18,
                "tilt_angle": 30,
                "azimuth_angle": 180,
                "location": {
                    "lat": 40.7128,
                    "lon": -74.0060
                }
            },
            "appliances": [
                {
                    "name": "Dishwasher",
                    "power_rating": 1.5,
                    "duration": 1.5,
                    "flexibility": 8,
                    "priority": "medium"
                },
                {
                    "name": "Washing Machine",
                    "power_rating": 0.8,
                    "duration": 1.0,
                    "flexibility": 9,
                    "priority": "medium"
                },
                {
                    "name": "Dryer",
                    "power_rating": 3.0,
                    "duration": 1.5,
                    "flexibility": 7,
                    "priority": "medium"
                },
                {
                    "name": "EV Charging",
                    "power_rating": 7.2,
                    "duration": 6.0,
                    "flexibility": 6,
                    "priority": "high"
                }
            ]
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
        
        self.load_config()
    
    def run(self):
        """Main application loop"""
        print("🌞 Solar Energy Optimizer")
        print("========================")
        
        if not self.api_key or self.api_key == "YOUR_OPENWEATHERMAP_API_KEY":
            print("⚠️  Please set your OpenWeatherMap API key in config.json")
            print("💡 For testing, you can use option 1 with sample data")
        
        while True:
            print("\nOptions:")
            print("1. Show today's optimization schedule")
            print("2. Show weekly forecast")
            print("3. Create visualization plots")
            print("4. Update configuration")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                self.show_daily_schedule()
            elif choice == "2":
                self.show_weekly_forecast()
            elif choice == "3":
                self.create_visualization_plots()
            elif choice == "4":
                self.update_config()
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def get_weather_forecast(self) -> List[WeatherData]:
        """Get weather forecast data"""
        if self.weather_api:
            lat = self.solar_config.location['lat']
            lon = self.solar_config.location['lon']
            return self.weather_api.get_forecast(lat, lon)
        else:
            print("Using sample weather data (set API key for real data)")
            return get_sample_weather_data()
    
    def show_daily_schedule(self):
        """Show today's optimization schedule"""
        print("\n📅 Today's Optimization Schedule")
        print("================================")
        
        weather_forecast = self.get_weather_forecast()
        
        if not weather_forecast:
            print("❌ Unable to fetch weather data")
            return
        
        # Calculate solar production
        production_schedule = self.solar_calculator.calculate_daily_production(weather_forecast)
        
        # Optimize appliance schedule
        schedule = self.scheduler.optimize_schedule(production_schedule)
        
        # Display results
        self.display_schedule(schedule, production_schedule)
        
        # Show recommendations
        recommendations = self.scheduler.recommend_deferrals(schedule, production_schedule)
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
    
    def display_schedule(self, schedule: List[ScheduleItem], production_schedule: List[Tuple[datetime.datetime, float]]):
        """Display the optimization schedule"""
        print("\n⏰ Optimal Appliance Schedule:")
        print("-" * 50)
        
        for item in schedule:
            solar_percent = int(item.solar_coverage * 100)
            
            print(f"{item.appliance.name:15} | {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')} | "
                  f"Solar: {solar_percent:3}% | Savings: ${item.cost_savings:.2f}")
        
        if not schedule:
            print("No optimal schedule found for today.")
        
        # Show hourly production overview
        print("\n📊 Hourly Solar Production Overview:")
        print("-" * 50)
        
        categories = self.solar_calculator.get_production_categories(production_schedule)
        
        for i, (timestamp, category) in enumerate(categories):
            if i % 4 == 0:  # Show every 4th hour
                output = production_schedule[i][1]
                emoji = "🟢" if category == "green" else "🟡" if category == "yellow" else "🔴"
                print(f"{timestamp.strftime('%H:%M')} {emoji} {output:.1f}kW")
        
        # Show summary
        summary = self.scheduler.get_schedule_summary(schedule)
        print(f"\n📈 Summary:")
        print(f"  Total Energy: {summary['total_energy']:.1f} kWh")
        print(f"  Solar Coverage: {summary['solar_percentage']:.1f}%")
        print(f"  Cost Savings: ${summary['cost_savings']:.2f}")
    
    def show_weekly_forecast(self):
        """Show weekly forecast and planning"""
        print("\n📊 Weekly Energy Forecast")
        print("=========================")
        
        weather_forecast = self.get_weather_forecast()
        
        if not weather_forecast:
            print("❌ Unable to fetch weather data")
            return
        
        # Group by days
        daily_production = {}
        for weather in weather_forecast:
            date = weather.timestamp.date()
            if date not in daily_production:
                daily_production[date] = []
            daily_production[date].append(weather)
        
        print("\n📅 Daily Production Forecast:")
        print("-" * 40)
        
        for date, weather_list in sorted(daily_production.items()):
            daily_schedule = self.solar_calculator.calculate_daily_production(weather_list)
            total_production = sum(output for _, output in daily_schedule)
            
            avg_cloud_cover = sum(w.cloud_cover for w in weather_list) / len(weather_list)
            
            weather_emoji = "☀️" if avg_cloud_cover < 30 else "⛅" if avg_cloud_cover < 70 else "☁️"
            
            print(f"{date.strftime('%a %m/%d')} {weather_emoji} {total_production:.1f}kWh "
                  f"(clouds: {avg_cloud_cover:.0f}%)")
        
        # Best days for energy-intensive tasks
        print("\n🔋 Best Days for Energy-Intensive Tasks:")
        print("-" * 40)
        
        best_days = sorted(daily_production.items(), 
                          key=lambda x: sum(self.solar_calculator.calculate_solar_output(w) for w in x[1]),
                          reverse=True)[:3]
        
        for date, weather_list in best_days:
            daily_schedule = self.solar_calculator.calculate_daily_production(weather_list)
            total_production = sum(output for _, output in daily_schedule)
            print(f"  {date.strftime('%A %m/%d')}: {total_production:.1f}kWh")
    
    def update_config(self):
        """Update configuration interactively"""
        print("\n⚙️  Configuration Update")
        print("=======================")
        
        print("\nCurrent Configuration:")
        print(f"  Location: {self.solar_config.location['lat']:.2f}, {self.solar_config.location['lon']:.2f}")
        print(f"  Panels: {self.solar_config.panel_count} x {self.solar_config.panel_wattage}W")
        print(f"  Efficiency: {self.solar_config.efficiency * 100:.1f}%")
        print(f"  Tilt: {self.solar_config.tilt_angle}°")
        
        print("\nAppliances:")
        for app in self.appliances:
            print(f"  {app.name}: {app.power_rating}kW, {app.duration}h, flexibility: {app.flexibility}")
        
        print("\nConfiguration editing interface coming soon...")
        print("For now, edit the config.json file directly.")
    
    def create_visualization_plots(self):
        """Create visualization plots"""
        print("\n📊 Creating Visualization Plots")
        print("===============================")
        
        try:
            from visualizer import SolarVisualizer, PlotConfig
            
            weather_forecast = self.get_weather_forecast()
            
            if not weather_forecast:
                print("❌ Unable to fetch weather data")
                return
            
            # Calculate solar production
            production_schedule = self.solar_calculator.calculate_daily_production(weather_forecast)
            
            # Optimize appliance schedule
            schedule = self.scheduler.optimize_schedule(production_schedule)
            
            # Create visualizer
            plot_config = PlotConfig(figure_size=(15, 10), dpi=100)
            visualizer = SolarVisualizer(plot_config)
            
            print("\n📈 Generating daily simulation plot...")
            visualizer.create_daily_simulation_plot(
                production_schedule=production_schedule,
                appliance_schedule=schedule,
                base_load=2.0,
                save_path="daily_simulation.png"
            )
            
            print("\n📊 Generating summary statistics plot...")
            visualizer.create_summary_statistics_plot(
                production_schedule=production_schedule,
                appliance_schedule=schedule,
                base_load=2.0,
                save_path="energy_summary.png"
            )
            
            print("\n✅ Plots created successfully!")
            print("   • daily_simulation.png - Main simulation plot")
            print("   • energy_summary.png - Summary statistics")
            
        except ImportError:
            print("❌ Matplotlib not installed. Please install with: pip install matplotlib numpy")
        except Exception as e:
            print(f"❌ Error creating plots: {e}")

if __name__ == "__main__":
    optimizer = SolarOptimizer()
    optimizer.run()