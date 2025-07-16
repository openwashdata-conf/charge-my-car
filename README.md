# Solar Energy Optimizer

A Python application that helps optimize electricity usage based on solar PV production and weather forecasts.

## Features

- **Weather Data Integration**: Fetches weather data from OpenWeatherMap API for accurate solar irradiance forecasting
- **Solar Production Calculation**: Calculates predicted solar PV output based on weather conditions, panel specifications, and sun angles
- **Appliance Scheduling**: Optimizes timing for high-energy appliances (dishwasher, washing machine, dryer, EV charging)
- **Visual Schedule Display**: Shows daily schedules with green/yellow/red periods indicating solar availability
- **Interactive Plotting**: Creates detailed plots showing solar production vs consumption with appliance markers
- **Cost Savings Analysis**: Calculates potential savings from solar-powered operation
- **Weekly Forecasting**: Provides multi-day planning for energy-intensive tasks
- **Scenario Comparison**: Compare sunny vs cloudy day performance

## Installation

1. Clone or download the project files
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   This will install:
   - `requests` for API calls
   - `matplotlib` for plotting
   - `numpy` for numerical calculations
3. Get a free API key from [OpenWeatherMap](https://openweathermap.org/api)
4. Run the application:
   ```bash
   python main.py
   ```

## Configuration

On first run, the application creates a `config.json` file with default settings. Edit this file to match your system:

```json
{
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
    }
  ]
}
```

### Configuration Parameters

- **Solar System**:
  - `panel_wattage`: Watts per panel (e.g., 300W)
  - `panel_count`: Number of panels in your system
  - `efficiency`: Panel efficiency as decimal (18% = 0.18)
  - `tilt_angle`: Panel tilt angle in degrees
  - `azimuth_angle`: Panel orientation (180 = south-facing)
  - `location`: Your latitude and longitude

- **Appliances**:
  - `name`: Appliance name for display
  - `power_rating`: Power consumption in kW
  - `duration`: How long it runs in hours
  - `flexibility`: 0-10 scale (higher = more flexible timing)
  - `priority`: "high", "medium", or "low"

## Usage

### Main Menu Options

1. **Daily Schedule**: Shows today's optimized appliance schedule
2. **Weekly Forecast**: Displays multi-day solar production forecast
3. **Create Visualization Plots**: Generate detailed plots showing solar production and appliance scheduling
4. **Configuration**: View current system settings
5. **Exit**: Quit the application

### Plotting and Visualization

The application now includes comprehensive plotting capabilities:

- **Daily Simulation Plot**: Shows solar production vs consumption with appliance markers
- **Summary Statistics**: Pie charts and bar graphs showing energy distribution
- **Appliance Timeline**: Visual timeline of when each appliance operates
- **Energy Balance**: Breakdown of solar vs grid power usage

#### Running Simulations

```bash
# Quick plot demo
python plot_demo.py

# Full daily simulation with detailed plots
python daily_simulation.py

# Interactive plotting through main application
python main.py
# Then select option 3
```

### Sample Output

```
🌞 Solar Energy Optimizer
========================

⏰ Optimal Appliance Schedule:
--------------------------------------------------
EV Charging     | 10:00-16:00 | Solar:  85% | Savings: $4.32
Dishwasher      | 12:00-13:30 | Solar:  92% | Savings: $0.27
Washing Machine | 11:00-12:00 | Solar:  88% | Savings: $0.11
Dryer           | 13:30-15:00 | Solar:  78% | Savings: $0.35

📊 Hourly Solar Production Overview:
--------------------------------------------------
08:00 🟡 2.1kW
12:00 🟢 5.8kW
16:00 🟡 3.2kW
20:00 🔴 0.0kW

📈 Summary:
  Total Energy: 12.9 kWh
  Solar Coverage: 84.2%
  Cost Savings: $5.05
```

## Testing Without API Key

The application includes sample weather data for testing. Simply run the application and select option 1 to see the optimizer in action with simulated data.

## Technical Details

### Solar Calculations
- Accounts for sun angle, seasonal variations, and panel orientation
- Considers temperature effects on panel efficiency
- Includes cloud cover impact on solar irradiance

### Scheduling Algorithm
- Prioritizes appliances by importance and flexibility
- Maximizes solar energy usage
- Considers appliance power requirements and duration
- Provides recommendations for better timing

### Data Storage
- SQLite database for historical weather and production data
- Persistent configuration storage
- Rate limiting for API calls

## Files Structure

```
solar-optimizer/
├── main.py              # Main application
├── weather.py           # Weather API integration
├── solar_calculator.py  # Solar production calculations
├── scheduler.py         # Appliance scheduling logic
├── visualizer.py        # Plotting and visualization
├── daily_simulation.py  # Detailed daily simulation
├── plot_demo.py         # Quick plotting demo
├── test_demo.py         # Basic functionality test
├── requirements.txt     # Dependencies
├── README.md           # This file
├── config.json         # User configuration (auto-generated)
└── solar_data.db       # SQLite database (auto-generated)
```

## Example Visualizations

The application generates several types of plots:

1. **Daily Simulation Plot**: 
   - Top panel: Solar production vs total consumption
   - Middle panel: Appliance operation timeline
   - Bottom panel: Energy source breakdown (solar vs grid)

2. **Summary Statistics**:
   - Energy source pie chart
   - Appliance usage bar chart
   - Solar efficiency over time
   - Cost analysis comparison

3. **Scenario Comparison**:
   - Sunny day vs cloudy day performance
   - Production differences and optimization impact

## Contributing

Feel free to submit issues and pull requests to improve the application.

## License

This project is released under the MIT License.