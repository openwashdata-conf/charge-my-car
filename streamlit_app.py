#!/usr/bin/env python3
"""
Solar Energy Optimizer - Streamlit Web App
Interactive web interface for optimizing electricity usage based on solar PV production
"""

import streamlit as st
import pandas as pd
import numpy as np
import datetime
import json
import io
from typing import Dict, List

# Import existing modules
from weather import WeatherAPI, get_sample_weather_data
from solar_calculator import SolarCalculator, SolarConfig
from scheduler import ApplianceScheduler, Appliance, Priority
from visualizer import SolarVisualizer, PlotConfig

# Configure Streamlit page
st.set_page_config(
    page_title="Solar Energy Optimizer",
    page_icon="🌞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF6B35;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stButton > button {
        width: 100%;
        background-color: #FF6B35;
        color: white;
        border: none;
        padding: 0.5rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #E55A2E;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'optimizer_config' not in st.session_state:
    st.session_state.optimizer_config = {
        'api_key': '',
        'location': {'lat': 40.7128, 'lon': -74.0060},
        'solar_system': {
            'panel_wattage': 300,
            'panel_count': 20,
            'efficiency': 0.18,
            'tilt_angle': 30,
            'azimuth_angle': 180
        },
        'appliances': [
            {'name': 'Dishwasher', 'power_rating': 1.5, 'duration': 1.5, 'flexibility': 8, 'priority': 'medium'},
            {'name': 'Washing Machine', 'power_rating': 0.8, 'duration': 1.0, 'flexibility': 9, 'priority': 'medium'},
            {'name': 'Dryer', 'power_rating': 3.0, 'duration': 1.5, 'flexibility': 7, 'priority': 'medium'},
            {'name': 'EV Charging', 'power_rating': 7.2, 'duration': 6.0, 'flexibility': 6, 'priority': 'high'}
        ]
    }

def create_solar_config():
    """Create SolarConfig from session state"""
    config = st.session_state.optimizer_config
    return SolarConfig(
        panel_wattage=config['solar_system']['panel_wattage'],
        panel_count=config['solar_system']['panel_count'],
        efficiency=config['solar_system']['efficiency'],
        tilt_angle=config['solar_system']['tilt_angle'],
        azimuth_angle=config['solar_system']['azimuth_angle'],
        location=config['location']
    )

def create_appliances_list():
    """Create list of Appliance objects from session state"""
    appliances = []
    for app_data in st.session_state.optimizer_config['appliances']:
        priority = Priority.HIGH if app_data['priority'] == 'high' else Priority.LOW if app_data['priority'] == 'low' else Priority.MEDIUM
        appliance = Appliance(
            name=app_data['name'],
            power_rating=app_data['power_rating'],
            duration=app_data['duration'],
            flexibility=app_data['flexibility'],
            priority=priority
        )
        appliances.append(appliance)
    return appliances

def render_sidebar():
    """Render sidebar with configuration options"""
    st.sidebar.markdown("## ⚙️ System Configuration")
    
    # Location settings
    st.sidebar.markdown("### 📍 Location")
    lat = st.sidebar.number_input("Latitude", value=st.session_state.optimizer_config['location']['lat'], format="%.4f")
    lon = st.sidebar.number_input("Longitude", value=st.session_state.optimizer_config['location']['lon'], format="%.4f")
    st.session_state.optimizer_config['location'] = {'lat': lat, 'lon': lon}
    
    # Solar system settings
    st.sidebar.markdown("### ☀️ Solar System")
    panel_wattage = st.sidebar.slider("Panel Wattage (W)", 100, 500, st.session_state.optimizer_config['solar_system']['panel_wattage'])
    panel_count = st.sidebar.slider("Number of Panels", 1, 50, st.session_state.optimizer_config['solar_system']['panel_count'])
    efficiency = st.sidebar.slider("Panel Efficiency (%)", 10, 25, int(st.session_state.optimizer_config['solar_system']['efficiency'] * 100)) / 100
    tilt_angle = st.sidebar.slider("Tilt Angle (°)", 0, 90, st.session_state.optimizer_config['solar_system']['tilt_angle'])
    azimuth_angle = st.sidebar.slider("Azimuth Angle (°)", 0, 360, st.session_state.optimizer_config['solar_system']['azimuth_angle'])
    
    st.session_state.optimizer_config['solar_system'] = {
        'panel_wattage': panel_wattage,
        'panel_count': panel_count,
        'efficiency': efficiency,
        'tilt_angle': tilt_angle,
        'azimuth_angle': azimuth_angle
    }
    
    # Weather API
    st.sidebar.markdown("### 🌤️ Weather API")
    api_key = st.sidebar.text_input("OpenWeatherMap API Key", value=st.session_state.optimizer_config['api_key'], type="password")
    st.session_state.optimizer_config['api_key'] = api_key
    
    if not api_key:
        st.sidebar.info("💡 Without API key, sample weather data will be used")
    
    # System capacity display
    total_capacity = panel_wattage * panel_count / 1000
    st.sidebar.markdown(f"### 📊 System Capacity")
    st.sidebar.metric("Total Capacity", f"{total_capacity:.1f} kW")
    st.sidebar.metric("Daily Potential", f"{total_capacity * 5:.1f} kWh")

def render_appliance_profiles():
    """Render appliance load profile configuration"""
    st.markdown("## 🏠 Appliance Load Profiles")
    
    # Create columns for appliance configuration
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Configure Your Appliances")
        
        # Create a form for adding/editing appliances
        with st.form("appliance_form"):
            cols = st.columns(4)
            
            with cols[0]:
                name = st.text_input("Appliance Name", value="New Appliance")
            with cols[1]:
                power_rating = st.number_input("Power (kW)", min_value=0.1, max_value=20.0, value=1.0, step=0.1)
            with cols[2]:
                duration = st.number_input("Duration (hours)", min_value=0.1, max_value=24.0, value=1.0, step=0.1)
            with cols[3]:
                flexibility = st.slider("Flexibility (0-10)", 0, 10, 5)
            
            priority = st.selectbox("Priority", ['low', 'medium', 'high'], index=1)
            
            if st.form_submit_button("Add/Update Appliance"):
                # Add new appliance to the list
                new_appliance = {
                    'name': name,
                    'power_rating': power_rating,
                    'duration': duration,
                    'flexibility': flexibility,
                    'priority': priority
                }
                
                # Check if appliance already exists
                existing_index = None
                for i, app in enumerate(st.session_state.optimizer_config['appliances']):
                    if app['name'] == name:
                        existing_index = i
                        break
                
                if existing_index is not None:
                    st.session_state.optimizer_config['appliances'][existing_index] = new_appliance
                    st.success(f"Updated {name}!")
                else:
                    st.session_state.optimizer_config['appliances'].append(new_appliance)
                    st.success(f"Added {name}!")
                
                st.rerun()
    
    with col2:
        st.markdown("### Current Appliances")
        
        # Display current appliances
        for i, app in enumerate(st.session_state.optimizer_config['appliances']):
            with st.expander(f"{app['name']} - {app['power_rating']}kW"):
                st.write(f"**Duration**: {app['duration']} hours")
                st.write(f"**Flexibility**: {app['flexibility']}/10")
                st.write(f"**Priority**: {app['priority']}")
                st.write(f"**Daily Energy**: {app['power_rating'] * app['duration']:.1f} kWh")
                
                if st.button(f"Remove {app['name']}", key=f"remove_{i}"):
                    st.session_state.optimizer_config['appliances'].pop(i)
                    st.rerun()
    
    # Display appliance summary table
    st.markdown("### 📋 Appliance Summary")
    
    if st.session_state.optimizer_config['appliances']:
        df = pd.DataFrame(st.session_state.optimizer_config['appliances'])
        df['Daily Energy (kWh)'] = df['power_rating'] * df['duration']
        
        # Format the dataframe for display
        display_df = df[['name', 'power_rating', 'duration', 'flexibility', 'priority', 'Daily Energy (kWh)']]
        display_df.columns = ['Appliance', 'Power (kW)', 'Duration (h)', 'Flexibility', 'Priority', 'Daily Energy (kWh)']
        
        st.dataframe(display_df, use_container_width=True)
        
        # Show totals
        total_energy = df['Daily Energy (kWh)'].sum()
        st.metric("Total Daily Energy Consumption", f"{total_energy:.1f} kWh")
    else:
        st.info("No appliances configured. Add some appliances above to get started!")

def run_optimization():
    """Run the solar optimization"""
    if not st.session_state.optimizer_config['appliances']:
        st.error("Please add at least one appliance to optimize!")
        return None, None, None
    
    # Create configuration objects
    solar_config = create_solar_config()
    appliances = create_appliances_list()
    
    # Get weather data
    if st.session_state.optimizer_config['api_key']:
        try:
            weather_api = WeatherAPI(st.session_state.optimizer_config['api_key'])
            weather_forecast = weather_api.get_forecast(
                solar_config.location['lat'], 
                solar_config.location['lon']
            )
            if not weather_forecast:
                st.warning("Failed to fetch weather data. Using sample data.")
                weather_forecast = get_sample_weather_data()
        except Exception as e:
            st.warning(f"Weather API error: {e}. Using sample data.")
            weather_forecast = get_sample_weather_data()
    else:
        weather_forecast = get_sample_weather_data()
    
    # Calculate solar production
    solar_calculator = SolarCalculator(solar_config)
    production_schedule = solar_calculator.calculate_daily_production(weather_forecast)
    
    # Optimize appliance schedule
    scheduler = ApplianceScheduler(appliances)
    appliance_schedule = scheduler.optimize_schedule(production_schedule)
    
    return production_schedule, appliance_schedule, scheduler

def create_streamlit_visualization(production_schedule, appliance_schedule):
    """Create Streamlit-specific visualization"""
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    
    # Extract data
    timestamps = [item[0] for item in production_schedule]
    solar_output = [item[1] for item in production_schedule]
    
    # Calculate total consumption
    base_load = 2.0
    consumption = []
    for timestamp in timestamps:
        appliance_load = sum(
            item.appliance.power_rating 
            for item in appliance_schedule 
            if item.start_time <= timestamp < item.end_time
        )
        consumption.append(base_load + appliance_load)
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot 1: Solar Production vs Consumption
    ax1.fill_between(range(len(timestamps)), 0, solar_output, 
                    alpha=0.7, color='#FFA500', label='Solar Production')
    ax1.plot(range(len(timestamps)), consumption, 
            linewidth=2, color='#DC143C', label='Total Consumption')
    ax1.plot(range(len(timestamps)), [base_load] * len(timestamps), 
            linewidth=1, color='#4169E1', linestyle='--', label='Base Load')
    
    # Add appliance markers
    colors = {'Dishwasher': '#4169E1', 'Washing Machine': '#9370DB', 
              'Dryer': '#FF1493', 'EV Charging': '#00CED1'}
    
    for item in appliance_schedule:
        color = colors.get(item.appliance.name, '#888888')
        start_idx = next((i for i, (t, _) in enumerate(production_schedule) 
                         if t >= item.start_time), 0)
        end_idx = next((i for i, (t, _) in enumerate(production_schedule) 
                       if t >= item.end_time), len(production_schedule))
        
        ax1.axvspan(start_idx, end_idx, alpha=0.3, color=color, 
                   label=f"{item.appliance.name} ({item.solar_coverage*100:.0f}% solar)")
    
    ax1.set_ylabel('Power (kW)')
    ax1.set_title('Solar Production vs Energy Consumption')
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax1.grid(True, alpha=0.3)
    
    # Set x-axis labels
    hour_labels = [t.strftime('%H:%M') for t in timestamps[::4]]
    ax1.set_xticks(range(0, len(timestamps), 4))
    ax1.set_xticklabels(hour_labels)
    
    # Plot 2: Energy Balance
    solar_usage = [min(prod, cons) for prod, cons in zip(solar_output, consumption)]
    grid_usage = [max(0, cons - prod) for prod, cons in zip(solar_output, consumption)]
    
    ax2.fill_between(range(len(timestamps)), 0, solar_usage, 
                    alpha=0.7, color='#32CD32', label='Solar-Powered')
    ax2.fill_between(range(len(timestamps)), solar_usage, 
                    [s + g for s, g in zip(solar_usage, grid_usage)], 
                    alpha=0.7, color='#FF4500', label='Grid-Powered')
    
    ax2.set_ylabel('Power (kW)')
    ax2.set_xlabel('Time of Day')
    ax2.set_title('Energy Source Breakdown')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Set x-axis labels
    ax2.set_xticks(range(0, len(timestamps), 4))
    ax2.set_xticklabels(hour_labels)
    
    plt.tight_layout()
    
    # Display in Streamlit
    st.pyplot(fig)
    
    # Additional metrics
    col1, col2, col3 = st.columns(3)
    
    total_solar_used = sum(solar_usage)
    total_grid_used = sum(grid_usage)
    total_consumption = total_solar_used + total_grid_used
    
    with col1:
        st.metric("Solar Energy Used", f"{total_solar_used:.1f} kWh")
    
    with col2:
        st.metric("Grid Energy Used", f"{total_grid_used:.1f} kWh")
    
    with col3:
        if total_consumption > 0:
            solar_percentage = (total_solar_used / total_consumption) * 100
            st.metric("Solar Efficiency", f"{solar_percentage:.1f}%")

def render_results():
    """Render optimization results"""
    st.markdown("## 📊 Optimization Results")
    
    if st.button("🚀 Run Optimization", key="optimize_button"):
        with st.spinner("Optimizing your energy schedule..."):
            production_schedule, appliance_schedule, scheduler = run_optimization()
            
            if production_schedule is None:
                return
            
            # Store results in session state
            st.session_state.results = {
                'production_schedule': production_schedule,
                'appliance_schedule': appliance_schedule,
                'scheduler': scheduler
            }
    
    # Display results if available
    if 'results' in st.session_state:
        production_schedule = st.session_state.results['production_schedule']
        appliance_schedule = st.session_state.results['appliance_schedule']
        scheduler = st.session_state.results['scheduler']
        
        # Key metrics
        st.markdown("### 📈 Key Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_production = sum(output for _, output in production_schedule)
        summary = scheduler.get_schedule_summary(appliance_schedule)
        
        with col1:
            st.metric("Total Solar Production", f"{total_production:.1f} kWh")
        
        with col2:
            st.metric("Solar Coverage", f"{summary['solar_percentage']:.1f}%")
        
        with col3:
            st.metric("Cost Savings", f"${summary['cost_savings']:.2f}")
        
        with col4:
            st.metric("Scheduled Appliances", f"{len(appliance_schedule)}")
        
        # Optimized schedule
        st.markdown("### ⏰ Optimized Schedule")
        
        if appliance_schedule:
            schedule_data = []
            for item in appliance_schedule:
                schedule_data.append({
                    'Appliance': item.appliance.name,
                    'Start Time': item.start_time.strftime('%H:%M'),
                    'End Time': item.end_time.strftime('%H:%M'),
                    'Duration': f"{item.appliance.duration:.1f}h",
                    'Power': f"{item.appliance.power_rating:.1f} kW",
                    'Solar Coverage': f"{item.solar_coverage * 100:.0f}%",
                    'Cost Savings': f"${item.cost_savings:.2f}"
                })
            
            df = pd.DataFrame(schedule_data)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No optimal schedule found. Try adjusting your appliance settings.")
        
        # Visualization
        st.markdown("### 📊 Energy Production & Consumption")
        
        try:
            # Create streamlit-specific visualization
            create_streamlit_visualization(production_schedule, appliance_schedule)
            
        except Exception as e:
            st.error(f"Error creating visualization: {e}")
        
        # Recommendations
        recommendations = scheduler.recommend_deferrals(appliance_schedule, production_schedule)
        if recommendations:
            st.markdown("### 💡 Recommendations")
            for rec in recommendations:
                st.info(rec)
        
        # Export options
        st.markdown("### 📥 Export Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Export Schedule as CSV"):
                if appliance_schedule:
                    df = pd.DataFrame(schedule_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"solar_schedule_{datetime.datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            if st.button("📄 Export Configuration"):
                config_json = json.dumps(st.session_state.optimizer_config, indent=2)
                st.download_button(
                    label="Download Config",
                    data=config_json,
                    file_name="solar_config.json",
                    mime="application/json"
                )

def main():
    """Main Streamlit app"""
    # Header
    st.markdown('<div class="main-header">🌞 Solar Energy Optimizer</div>', unsafe_allow_html=True)
    st.markdown("*Optimize your electricity usage based on solar PV production and weather forecasts*")
    
    # Sidebar
    render_sidebar()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["🏠 Configure Appliances", "📊 Optimization Results", "ℹ️ About"])
    
    with tab1:
        render_appliance_profiles()
    
    with tab2:
        render_results()
    
    with tab3:
        st.markdown("## About Solar Energy Optimizer")
        st.markdown("""
        This web application helps you optimize your electricity usage by scheduling appliances 
        to run when solar energy production is highest, maximizing your use of clean energy 
        and minimizing costs.
        
        ### Features:
        - 🌤️ **Weather Integration**: Real-time weather data for accurate solar forecasting
        - ⚡ **Smart Scheduling**: Intelligent appliance scheduling based on solar production
        - 📊 **Visual Analytics**: Interactive charts showing energy production and consumption
        - 💰 **Cost Savings**: Calculate potential savings from solar-powered operation
        - 🎛️ **Flexible Configuration**: Easy-to-use interface for system and appliance setup
        
        ### How It Works:
        1. **Configure** your solar system specifications and location
        2. **Add** your appliances with their power ratings and flexibility
        3. **Optimize** to get the best schedule for maximum solar usage
        4. **Export** your optimized schedule and configuration
        
        ### Getting Started:
        1. Set your location and solar system details in the sidebar
        2. Add your appliances in the "Configure Appliances" tab
        3. Click "Run Optimization" to see your optimal schedule
        
        *Built with Streamlit and powered by advanced solar energy algorithms*
        """)

if __name__ == "__main__":
    main()