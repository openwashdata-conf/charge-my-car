#!/usr/bin/env python3
"""
Test script to verify Streamlit app functionality
"""

import sys
import os
import subprocess

def test_streamlit_imports():
    """Test that all required modules can be imported"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
        
        import pandas as pd
        print("✅ Pandas imported successfully")
        
        import matplotlib.pyplot as plt
        print("✅ Matplotlib imported successfully")
        
        import numpy as np
        print("✅ Numpy imported successfully")
        
        # Test importing our modules
        from weather import WeatherAPI, get_sample_weather_data
        print("✅ Weather module imported successfully")
        
        from solar_calculator import SolarCalculator, SolarConfig
        print("✅ Solar calculator module imported successfully")
        
        from scheduler import ApplianceScheduler, Appliance, Priority
        print("✅ Scheduler module imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_streamlit_app_syntax():
    """Test that the streamlit app has valid syntax"""
    try:
        # Try to compile the streamlit app
        with open('streamlit_app.py', 'r') as f:
            code = f.read()
        
        compile(code, 'streamlit_app.py', 'exec')
        print("✅ Streamlit app syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"❌ Syntax error in streamlit app: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of the core modules"""
    try:
        # Import here to avoid scope issues
        from weather import get_sample_weather_data
        from solar_calculator import SolarCalculator, SolarConfig
        from scheduler import ApplianceScheduler, Appliance, Priority
        
        # Test weather data
        weather_data = get_sample_weather_data()
        print(f"✅ Sample weather data generated: {len(weather_data)} data points")
        
        # Test solar configuration
        solar_config = SolarConfig(
            panel_wattage=300,
            panel_count=20,
            efficiency=0.18,
            tilt_angle=30,
            azimuth_angle=180,
            location={'lat': 40.7128, 'lon': -74.0060}
        )
        print("✅ Solar configuration created successfully")
        
        # Test solar calculator
        calculator = SolarCalculator(solar_config)
        production_schedule = calculator.calculate_daily_production(weather_data)
        print(f"✅ Solar production calculated: {len(production_schedule)} hourly values")
        
        # Test appliances
        appliances = [
            Appliance(name="Test Appliance", power_rating=1.0, duration=1.0, flexibility=5, priority=Priority.MEDIUM)
        ]
        print("✅ Appliances created successfully")
        
        # Test scheduler
        scheduler = ApplianceScheduler(appliances)
        schedule = scheduler.optimize_schedule(production_schedule)
        print(f"✅ Schedule optimized: {len(schedule)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Streamlit App Functionality")
    print("=" * 40)
    
    tests = [
        ("Module Imports", test_streamlit_imports),
        ("App Syntax", test_streamlit_app_syntax),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Test:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Streamlit app is ready to run.")
        print("\n🚀 To start the app, run:")
        print("   streamlit run streamlit_app.py")
        print("\n🌐 The app will be available at:")
        print("   http://localhost:8501")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())