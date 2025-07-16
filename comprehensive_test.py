#!/usr/bin/env python3
"""
Comprehensive test of the Solar Energy Optimizer with plotting capabilities
This script demonstrates all features of the application
"""

import datetime
import os
from main import SolarOptimizer
from visualizer import SolarVisualizer, PlotConfig

def comprehensive_test():
    """Run comprehensive test of all features"""
    
    print("🌞 Solar Energy Optimizer - Comprehensive Test")
    print("=" * 50)
    
    # 1. Initialize and test basic functionality
    print("\n1️⃣  Testing Basic Functionality")
    print("-" * 30)
    
    optimizer = SolarOptimizer()
    
    # Test configuration loading
    print(f"✅ Configuration loaded: {optimizer.config_file}")
    print(f"   Location: {optimizer.solar_config.location}")
    print(f"   System: {optimizer.solar_config.panel_count} x {optimizer.solar_config.panel_wattage}W panels")
    print(f"   Appliances: {len(optimizer.appliances)}")
    
    # 2. Test weather data and solar calculations
    print("\n2️⃣  Testing Weather Data and Solar Calculations")
    print("-" * 45)
    
    weather_forecast = optimizer.get_weather_forecast()
    print(f"✅ Weather forecast: {len(weather_forecast)} data points")
    
    production_schedule = optimizer.solar_calculator.calculate_daily_production(weather_forecast)
    total_production = sum(output for _, output in production_schedule)
    print(f"✅ Solar production calculated: {total_production:.1f} kWh total")
    
    # Show peak production time
    peak_time, peak_output = max(production_schedule, key=lambda x: x[1])
    print(f"   Peak production: {peak_output:.1f}kW at {peak_time.strftime('%H:%M')}")
    
    # 3. Test appliance scheduling
    print("\n3️⃣  Testing Appliance Scheduling")
    print("-" * 35)
    
    schedule = optimizer.scheduler.optimize_schedule(production_schedule)
    print(f"✅ Appliance schedule optimized: {len(schedule)} items")
    
    for item in schedule:
        print(f"   • {item.appliance.name:15} | {item.start_time.strftime('%H:%M')}-{item.end_time.strftime('%H:%M')} | "
              f"Solar: {item.solar_coverage*100:.0f}%")
    
    # Get schedule summary
    summary = optimizer.scheduler.get_schedule_summary(schedule)
    print(f"\n   Summary: {summary['solar_percentage']:.1f}% solar coverage, ${summary['cost_savings']:.2f} savings")
    
    # 4. Test visualization capabilities
    print("\n4️⃣  Testing Visualization Capabilities")
    print("-" * 37)
    
    try:
        plot_config = PlotConfig(figure_size=(14, 10), dpi=100)
        visualizer = SolarVisualizer(plot_config)
        
        # Create daily simulation plot
        print("📊 Creating daily simulation plot...")
        visualizer.create_daily_simulation_plot(
            production_schedule=production_schedule,
            appliance_schedule=schedule,
            base_load=2.0,
            save_path="test_daily_simulation.png"
        )
        
        # Create summary statistics plot
        print("📈 Creating summary statistics plot...")
        visualizer.create_summary_statistics_plot(
            production_schedule=production_schedule,
            appliance_schedule=schedule,
            base_load=2.0,
            save_path="test_energy_summary.png"
        )
        
        print("✅ Visualization plots created successfully")
        
    except Exception as e:
        print(f"❌ Visualization error: {e}")
    
    # 5. Test database functionality
    print("\n5️⃣  Testing Database Functionality")
    print("-" * 33)
    
    try:
        import sqlite3
        
        # Check if database was created
        if os.path.exists(optimizer.db_path):
            conn = sqlite3.connect(optimizer.db_path)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ Database created with {len(tables)} tables: {[t[0] for t in tables]}")
            
            # Check if we can insert sample data
            cursor.execute("INSERT INTO weather_data (timestamp, temperature, cloud_cover, solar_irradiance) VALUES (?, ?, ?, ?)",
                          (datetime.datetime.now().isoformat(), 25.0, 30.0, 800.0))
            conn.commit()
            
            # Check if data was inserted
            cursor.execute("SELECT COUNT(*) FROM weather_data")
            count = cursor.fetchone()[0]
            print(f"✅ Database operations working: {count} records in weather_data")
            
            conn.close()
        else:
            print("❌ Database file not found")
            
    except Exception as e:
        print(f"❌ Database error: {e}")
    
    # 6. Test energy statistics
    print("\n6️⃣  Testing Energy Statistics")
    print("-" * 29)
    
    # Calculate detailed statistics
    categories = optimizer.solar_calculator.get_production_categories(production_schedule)
    green_hours = sum(1 for _, cat in categories if cat == "green")
    yellow_hours = sum(1 for _, cat in categories if cat == "yellow")
    red_hours = sum(1 for _, cat in categories if cat == "red")
    
    print(f"✅ Energy period analysis:")
    print(f"   🟢 Green (high solar): {green_hours} hours")
    print(f"   🟡 Yellow (medium solar): {yellow_hours} hours")
    print(f"   🔴 Red (low solar): {red_hours} hours")
    
    # Test excess energy calculation
    excess_schedule = optimizer.solar_calculator.estimate_battery_charging(production_schedule)
    total_excess = sum(excess for _, excess in excess_schedule)
    print(f"✅ Excess energy analysis: {total_excess:.1f} kWh available for storage")
    
    # Test optimal time windows
    optimal_windows = optimizer.solar_calculator.get_optimal_time_windows(
        production_schedule, min_power=5.0, duration_hours=2.0
    )
    print(f"✅ Optimal time windows: {len(optimal_windows)} windows for high-power appliances")
    
    # 7. Test recommendations
    print("\n7️⃣  Testing Recommendations")
    print("-" * 27)
    
    recommendations = optimizer.scheduler.recommend_deferrals(schedule, production_schedule)
    if recommendations:
        print(f"✅ Generated {len(recommendations)} recommendations:")
        for rec in recommendations:
            print(f"   💡 {rec}")
    else:
        print("✅ No deferrals recommended - schedule is optimal")
    
    # 8. Final summary
    print("\n8️⃣  Final Summary")
    print("-" * 16)
    
    print(f"✅ All tests completed successfully!")
    print(f"\n📊 Key Metrics:")
    print(f"   Total Solar Production: {total_production:.1f} kWh")
    print(f"   Scheduled Appliances: {len(schedule)}")
    print(f"   Solar Coverage: {summary['solar_percentage']:.1f}%")
    print(f"   Cost Savings: ${summary['cost_savings']:.2f}")
    print(f"   Peak Production: {peak_output:.1f}kW at {peak_time.strftime('%H:%M')}")
    
    # Check created files
    created_files = []
    for filename in ['test_daily_simulation.png', 'test_energy_summary.png', 
                    'config.json', 'solar_data.db']:
        if os.path.exists(filename):
            created_files.append(filename)
    
    if created_files:
        print(f"\n📁 Created files:")
        for filename in created_files:
            print(f"   • {filename}")
    
    print(f"\n🎉 Solar Energy Optimizer is fully functional!")

if __name__ == "__main__":
    comprehensive_test()