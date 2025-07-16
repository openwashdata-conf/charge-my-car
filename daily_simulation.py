#!/usr/bin/env python3
"""
Daily Simulation with Plotting
Simulates a typical day and produces detailed plots showing solar production and appliance scheduling
"""

import datetime
import numpy as np
from typing import List, Tuple

from main import SolarOptimizer
from visualizer import SolarVisualizer, PlotConfig
from weather import WeatherData, get_sample_weather_data
from scheduler import ScheduleItem

def create_detailed_weather_simulation() -> List[WeatherData]:
    """
    Create a more detailed weather simulation with realistic solar conditions
    """
    weather_data = []
    base_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Create 24 hours of detailed weather data (every 15 minutes)
    for quarter_hour in range(96):  # 24 hours * 4 quarters
        timestamp = base_date + datetime.timedelta(minutes=15 * quarter_hour)
        hour = timestamp.hour + timestamp.minute / 60.0
        
        # More realistic temperature variation
        temp_base = 18 + 8 * np.sin(2 * np.pi * (hour - 6) / 24)  # Peak at 2 PM
        temp_variation = np.random.normal(0, 1)  # Small random variation
        temperature = temp_base + temp_variation
        
        # Cloud cover with morning fog, afternoon clearing, evening clouds
        if hour < 8:
            cloud_base = 60 + 20 * np.sin(np.pi * hour / 8)  # Morning fog
        elif hour < 14:
            cloud_base = 20 + 10 * np.sin(np.pi * (hour - 8) / 6)  # Clearing
        else:
            cloud_base = 30 + 25 * np.sin(np.pi * (hour - 14) / 10)  # Evening clouds
        
        cloud_variation = np.random.normal(0, 10)
        cloud_cover = max(0, min(100, cloud_base + cloud_variation))
        
        # Calculate solar irradiance with realistic factors
        if hour < 6 or hour > 18:
            irradiance = 0
        else:
            # Sun elevation factor
            sun_elevation = np.sin(np.pi * (hour - 6) / 12)
            
            # Atmospheric losses
            atmospheric_factor = 0.75 + 0.25 * sun_elevation
            
            # Cloud reduction
            cloud_factor = 1 - (cloud_cover / 100) * 0.8
            
            # Clear sky irradiance
            max_irradiance = 1200  # W/m²
            irradiance = max_irradiance * sun_elevation * atmospheric_factor * cloud_factor
        
        weather_data.append(WeatherData(
            timestamp=timestamp,
            temperature=temperature,
            cloud_cover=cloud_cover,
            solar_irradiance=max(0, irradiance),
            wind_speed=3.0 + np.random.normal(0, 1),
            humidity=50 + 20 * np.sin(2 * np.pi * hour / 24)
        ))
    
    return weather_data

def run_daily_simulation():
    """
    Run a comprehensive daily simulation with detailed plotting
    """
    print("🌞 Solar Energy Optimizer - Daily Simulation")
    print("=" * 50)
    
    # Initialize the optimizer
    optimizer = SolarOptimizer()
    
    # Create detailed weather simulation
    print("📊 Generating detailed weather simulation...")
    weather_forecast = create_detailed_weather_simulation()
    
    # Calculate solar production
    print("⚡ Calculating solar production...")
    production_schedule = optimizer.solar_calculator.calculate_daily_production(weather_forecast)
    
    # Optimize appliance schedule
    print("🔧 Optimizing appliance schedule...")
    appliance_schedule = optimizer.scheduler.optimize_schedule(production_schedule)
    
    # Create visualizer
    plot_config = PlotConfig(figure_size=(16, 12), dpi=100)
    visualizer = SolarVisualizer(plot_config)
    
    # Print summary before plotting
    print("\n📋 Simulation Summary:")
    print("-" * 30)
    
    total_production = sum(output for _, output in production_schedule)
    print(f"Total Solar Production: {total_production:.1f} kWh")
    
    if appliance_schedule:
        print(f"Scheduled Appliances: {len(appliance_schedule)}")
        for item in appliance_schedule:
            print(f"  • {item.appliance.name}: {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')} "
                  f"({item.solar_coverage*100:.0f}% solar, ${item.cost_savings:.2f} savings)")
    
    # Get statistics
    summary = optimizer.scheduler.get_schedule_summary(appliance_schedule)
    print(f"\nOverall Statistics:")
    print(f"  Total Energy Used: {summary['total_energy']:.1f} kWh")
    print(f"  Solar Coverage: {summary['solar_percentage']:.1f}%")
    print(f"  Cost Savings: ${summary['cost_savings']:.2f}")
    
    # Create plots
    print("\n📈 Creating detailed simulation plots...")
    
    # Main simulation plot
    visualizer.create_daily_simulation_plot(
        production_schedule=production_schedule,
        appliance_schedule=appliance_schedule,
        base_load=2.0,
        save_path="daily_simulation.png"
    )
    
    # Summary statistics plot
    visualizer.create_summary_statistics_plot(
        production_schedule=production_schedule,
        appliance_schedule=appliance_schedule,
        base_load=2.0,
        save_path="energy_summary.png"
    )
    
    print("\n✅ Simulation complete! Check the generated plots:")
    print("   • daily_simulation.png - Main simulation plot")
    print("   • energy_summary.png - Summary statistics")

def create_scenario_comparison():
    """
    Create a comparison of different scenarios (sunny vs cloudy day)
    """
    print("\n🌤️  Creating Scenario Comparison...")
    print("=" * 40)
    
    optimizer = SolarOptimizer()
    
    # Scenario 1: Sunny day
    sunny_weather = []
    base_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for hour in range(24):
        timestamp = base_date + datetime.timedelta(hours=hour)
        
        # Sunny day conditions
        temperature = 22 + 6 * np.sin(2 * np.pi * (hour - 6) / 24)
        cloud_cover = 10 + 5 * np.sin(2 * np.pi * hour / 24)  # Minimal clouds
        
        if hour < 6 or hour > 18:
            irradiance = 0
        else:
            sun_elevation = np.sin(np.pi * (hour - 6) / 12)
            irradiance = 1100 * sun_elevation * (1 - cloud_cover / 100 * 0.8)
        
        sunny_weather.append(WeatherData(
            timestamp=timestamp,
            temperature=temperature,
            cloud_cover=cloud_cover,
            solar_irradiance=max(0, irradiance),
            wind_speed=2.0,
            humidity=40
        ))
    
    # Scenario 2: Cloudy day
    cloudy_weather = []
    
    for hour in range(24):
        timestamp = base_date + datetime.timedelta(hours=hour)
        
        # Cloudy day conditions
        temperature = 18 + 4 * np.sin(2 * np.pi * (hour - 6) / 24)
        cloud_cover = 70 + 20 * np.sin(2 * np.pi * hour / 24)  # Heavy clouds
        
        if hour < 6 or hour > 18:
            irradiance = 0
        else:
            sun_elevation = np.sin(np.pi * (hour - 6) / 12)
            irradiance = 1100 * sun_elevation * (1 - cloud_cover / 100 * 0.8)
        
        cloudy_weather.append(WeatherData(
            timestamp=timestamp,
            temperature=temperature,
            cloud_cover=cloud_cover,
            solar_irradiance=max(0, irradiance),
            wind_speed=5.0,
            humidity=80
        ))
    
    # Calculate production for both scenarios
    sunny_production = optimizer.solar_calculator.calculate_daily_production(sunny_weather)
    cloudy_production = optimizer.solar_calculator.calculate_daily_production(cloudy_weather)
    
    # Optimize schedules
    sunny_schedule = optimizer.scheduler.optimize_schedule(sunny_production)
    cloudy_schedule = optimizer.scheduler.optimize_schedule(cloudy_production)
    
    # Print comparison
    sunny_total = sum(output for _, output in sunny_production)
    cloudy_total = sum(output for _, output in cloudy_production)
    
    print(f"☀️  Sunny Day: {sunny_total:.1f} kWh total production")
    print(f"☁️  Cloudy Day: {cloudy_total:.1f} kWh total production")
    print(f"📊 Difference: {sunny_total - cloudy_total:.1f} kWh ({(sunny_total/cloudy_total - 1)*100:.1f}% more)")
    
    # Get schedule summaries
    sunny_summary = optimizer.scheduler.get_schedule_summary(sunny_schedule)
    cloudy_summary = optimizer.scheduler.get_schedule_summary(cloudy_schedule)
    
    print(f"\n☀️  Sunny Day Schedule:")
    print(f"   Solar Coverage: {sunny_summary['solar_percentage']:.1f}%")
    print(f"   Cost Savings: ${sunny_summary['cost_savings']:.2f}")
    
    print(f"\n☁️  Cloudy Day Schedule:")
    print(f"   Solar Coverage: {cloudy_summary['solar_percentage']:.1f}%")
    print(f"   Cost Savings: ${cloudy_summary['cost_savings']:.2f}")

if __name__ == "__main__":
    # Run the main simulation
    run_daily_simulation()
    
    # Run scenario comparison
    create_scenario_comparison()
    
    print("\n🎉 All simulations completed successfully!")