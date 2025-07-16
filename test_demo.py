#!/usr/bin/env python3
"""
Test demo for Solar Energy Optimizer
"""

from main import SolarOptimizer
import datetime

def test_solar_optimizer():
    print("🌞 Solar Energy Optimizer - Demo Test")
    print("=" * 40)
    
    # Create optimizer instance
    optimizer = SolarOptimizer()
    
    # Test daily schedule functionality
    print("\n📅 Testing Daily Schedule:")
    print("-" * 30)
    
    # Get weather forecast (will use sample data)
    weather_forecast = optimizer.get_weather_forecast()
    print(f"✓ Weather forecast loaded: {len(weather_forecast)} data points")
    
    # Calculate solar production
    production_schedule = optimizer.solar_calculator.calculate_daily_production(weather_forecast)
    print(f"✓ Solar production calculated: {len(production_schedule)} hourly values")
    
    # Show some sample production values
    print("\n📊 Sample Solar Production:")
    for i in range(0, min(24, len(production_schedule)), 4):
        timestamp, output = production_schedule[i]
        print(f"  {timestamp.strftime('%H:%M')}: {output:.1f}kW")
    
    # Optimize appliance schedule
    schedule = optimizer.scheduler.optimize_schedule(production_schedule)
    print(f"\n✓ Appliance schedule optimized: {len(schedule)} items")
    
    # Display schedule
    print("\n⏰ Optimized Schedule:")
    for item in schedule:
        solar_percent = int(item.solar_coverage * 100)
        print(f"  {item.appliance.name:15} | {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')} | "
              f"Solar: {solar_percent:3}% | Savings: ${item.cost_savings:.2f}")
    
    # Show summary
    summary = optimizer.scheduler.get_schedule_summary(schedule)
    print(f"\n📈 Summary:")
    print(f"  Total Energy: {summary['total_energy']:.1f} kWh")
    print(f"  Solar Coverage: {summary['solar_percentage']:.1f}%")
    print(f"  Cost Savings: ${summary['cost_savings']:.2f}")
    
    # Test configuration display
    print(f"\n⚙️  System Configuration:")
    print(f"  Location: {optimizer.solar_config.location['lat']:.2f}, {optimizer.solar_config.location['lon']:.2f}")
    print(f"  Panels: {optimizer.solar_config.panel_count} x {optimizer.solar_config.panel_wattage}W")
    print(f"  Efficiency: {optimizer.solar_config.efficiency * 100:.1f}%")
    
    print(f"\n  Appliances:")
    for app in optimizer.appliances:
        print(f"    {app.name}: {app.power_rating}kW, {app.duration}h, flexibility: {app.flexibility}")
    
    print("\n✅ All tests completed successfully!")

if __name__ == "__main__":
    test_solar_optimizer()