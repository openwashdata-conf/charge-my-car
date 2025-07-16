# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
python main.py                    # Main interactive application
python daily_simulation.py       # Detailed simulation with advanced weather modeling
python plot_demo.py             # Quick visualization demo
```

### Testing
```bash
python test_demo.py              # Basic functionality test
python comprehensive_test.py     # Full system test with database verification
```

### Setup and Dependencies
```bash
pip install -r requirements.txt  # Install matplotlib, numpy, requests
```

### Configuration
- Edit `config.json` to modify solar system specifications and appliances
- Set `api_key` for OpenWeatherMap integration (optional - uses sample data as fallback)
- Application auto-creates default configuration on first run

## Code Architecture

### Central Orchestrator Pattern
The `SolarOptimizer` class in `main.py` coordinates all components:
- Manages configuration loading and database initialization
- Orchestrates data flow between weather → solar calculation → scheduling → visualization
- Handles user interface and component integration

### Core Data Flow
```
Config (JSON) → Weather API → Solar Calculator → Scheduler → Visualizer
     ↓              ↓              ↓              ↓          ↓
  Database ← Historical Data ← Production ← Optimization ← Plots
```

### Key Components and Relationships

**Weather Layer** (`weather.py`):
- `WeatherAPI` class handles OpenWeatherMap integration with rate limiting
- `WeatherData` dataclass structures weather conditions with solar irradiance estimation
- Falls back to `get_sample_weather_data()` when API unavailable

**Solar Calculation Layer** (`solar_calculator.py`):
- `SolarCalculator` performs comprehensive solar output calculations
- Considers sun angle math, seasonal variations, temperature effects, and panel orientation
- Provides production categorization (green/yellow/red periods) and optimal time windows

**Scheduling Layer** (`scheduler.py`):
- `ApplianceScheduler` implements priority-based optimization algorithm
- Uses `Priority` enum (HIGH/MEDIUM/LOW) and flexibility scoring (0-10 scale)
- Maximizes solar coverage while handling schedule conflicts
- Generates recommendations for better timing

**Visualization Layer** (`visualizer.py`):
- `SolarVisualizer` creates multi-panel plots with professional styling
- Generates daily simulation plots, summary statistics, and energy balance charts
- Includes appliance timeline displays with solar coverage indicators

### Data Structures

**Configuration Objects**:
- `SolarConfig`: Panel specifications (wattage, count, efficiency, orientation, location)
- `Appliance`: Power rating, duration, flexibility, priority
- `ScheduleItem`: Optimized run with start/end times, solar coverage, cost savings

**Core Algorithms**:
- Solar calculation uses advanced sun angle mathematics with atmospheric factors
- Scheduling uses greedy algorithm with priority queues and flexibility scoring
- Optimization maximizes solar coverage while minimizing grid usage

### Database Design
- SQLite backend with `weather_data` and `solar_production` tables
- Historical data tracking for analytics and machine learning potential
- Automatic table creation and data persistence

### Testing Patterns
- `test_demo.py`: Basic component integration testing
- `comprehensive_test.py`: Full system validation with database verification
- `daily_simulation.py`: Advanced weather modeling and scenario comparison
- Each test script validates specific aspects of the system

### Error Handling and Resilience
- Graceful degradation with sample data fallback
- Rate limiting prevents API abuse
- Comprehensive exception handling with user feedback
- Database resilience with automatic initialization

### Visualization System
- Multi-panel plots: production vs consumption, appliance timeline, energy balance
- Summary statistics with pie charts and bar graphs
- Professional styling with customizable colors and DPI settings
- Supports both interactive display and PNG export

### Configuration Management
- JSON-based configuration for easy editing and version control
- Automatic default creation with NYC location and common appliances
- Validation and error handling for malformed configurations
- Flexible appliance definitions supporting various device types

## Development Workflow

1. **Setup**: Install dependencies and configure system specifications
2. **Testing**: Run test scripts to verify functionality across components
3. **Simulation**: Use daily simulation for detailed analysis and scenario testing
4. **Visualization**: Generate plots for analysis and presentation
5. **Database**: Historical data automatically tracked for future analytics

## Important Implementation Details

### Weather Integration
- OpenWeatherMap API with fallback to mathematical weather simulation
- Solar irradiance estimation based on cloud cover and sun position calculations
- Rate limiting with 1-second intervals between API calls

### Solar Calculations
- Comprehensive modeling including seasonal variations, panel orientation, and temperature effects
- Production categorization helps users understand optimal usage periods
- Optimal time window identification for high-energy appliances

### Scheduling Algorithm
- Priority-based greedy algorithm with flexibility scoring
- Handles appliance conflicts and maximizes solar coverage
- Generates actionable recommendations for schedule improvements

### Extensibility
- Modular design allows easy addition of new appliances or features
- Configuration-driven behavior modification
- Clear interfaces for extending functionality (new weather sources, optimization algorithms)

The codebase demonstrates professional software engineering practices with clean architecture, comprehensive testing, and robust error handling suitable for both personal use and potential commercial applications.