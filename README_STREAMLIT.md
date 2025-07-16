# Solar Energy Optimizer - Streamlit Web App

A web-based interface for the Solar Energy Optimizer that allows users to configure their solar systems and optimize appliance schedules through an interactive browser interface.

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_app.py
```

The app will be available at `http://localhost:8501`

### Testing
```bash
# Test app functionality
python test_streamlit.py
```

## 🌐 Deployment Options

### 1. Streamlit Cloud (Recommended - FREE)
1. Fork this repository to your GitHub account
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from your repository
5. Set `streamlit_app.py` as the main file

**Cost**: Free  
**URL**: Automatic subdomain (e.g., `yourapp.streamlit.app`)

### 2. Heroku
```bash
# Create Procfile
echo "web: streamlit run streamlit_app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Deploy to Heroku
git add .
git commit -m "Add Streamlit app"
git push heroku main
```

**Cost**: $5-7/month  
**URL**: Custom domain available

### 3. Railway
```bash
# Create railway.json
echo '{"deploy": {"startCommand": "streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0"}}' > railway.json

# Deploy to Railway
railway login
railway init
railway up
```

**Cost**: $5/month  
**URL**: Custom subdomain

### 4. Docker (Self-hosted)
```bash
# Build Docker image
docker build -t solar-optimizer .

# Run container
docker run -p 8501:8501 solar-optimizer
```

## 📱 Web App Features

### 🏠 Appliance Configuration
- **Interactive Form**: Add/edit appliances with power ratings, duration, and flexibility
- **Real-time Updates**: Instant configuration changes
- **Summary Table**: Overview of all configured appliances
- **Remove/Edit**: Easy appliance management

### ⚙️ System Configuration
- **Location Settings**: GPS coordinates for accurate solar calculations
- **Solar System Setup**: Panel specifications, tilt, and orientation
- **Weather Integration**: Optional OpenWeatherMap API key
- **Live Metrics**: Real-time system capacity calculations

### 📊 Optimization Results
- **One-Click Optimization**: Single button to run complete analysis
- **Visual Dashboard**: Interactive charts and metrics
- **Schedule Display**: Optimized appliance timeline
- **Export Options**: Download results as CSV/JSON

### 📈 Interactive Visualizations
- **Solar Production Chart**: Real-time solar generation curves
- **Energy Balance**: Solar vs grid power breakdown
- **Appliance Timeline**: Visual schedule with solar coverage
- **Efficiency Metrics**: Live calculation of solar utilization

## 🎛️ User Interface

### Sidebar Configuration
- **📍 Location**: Latitude/longitude input
- **☀️ Solar System**: Panel specifications and setup
- **🌤️ Weather API**: OpenWeatherMap integration
- **📊 System Metrics**: Live capacity calculations

### Main Tabs
1. **🏠 Configure Appliances**: Add and manage appliances
2. **📊 Optimization Results**: Run optimization and view results
3. **ℹ️ About**: Application information and help

### Key Controls
- **Sliders**: Interactive input for numerical values
- **Forms**: Structured appliance configuration
- **Buttons**: One-click optimization and export
- **Metrics**: Real-time performance indicators

## 🔧 Advanced Configuration

### API Integration
- **OpenWeatherMap**: Add API key for real weather data
- **Fallback Mode**: Automatic switch to sample data if API unavailable
- **Rate Limiting**: Built-in API protection

### Customization
- **Themes**: Professional color scheme
- **Responsive**: Works on desktop and mobile
- **Export**: Multiple format support (CSV, JSON)

### Performance
- **Caching**: Streamlit session state for fast updates
- **Lazy Loading**: Components load on demand
- **Optimized Plots**: Efficient matplotlib integration

## 🚀 Production Deployment

### Environment Variables
```bash
# For production deployment
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
OPENWEATHER_API_KEY=your_api_key_here
```

### Security
- **API Key Protection**: Secure input handling
- **CORS Configuration**: Proper cross-origin setup
- **Input Validation**: All user inputs validated

### Monitoring
- **Error Handling**: Graceful degradation
- **User Feedback**: Clear error messages
- **Performance Metrics**: Built-in monitoring

## 📖 Usage Guide

### Getting Started
1. **Set Location**: Enter your GPS coordinates in the sidebar
2. **Configure Solar System**: Set panel specifications and orientation
3. **Add Appliances**: Configure your electrical appliances
4. **Run Optimization**: Click "Run Optimization" to get results
5. **Export Results**: Download your optimized schedule

### Best Practices
- **Accurate Data**: Use precise location and system specifications
- **Flexibility Settings**: Higher flexibility = better optimization
- **Regular Updates**: Re-run optimization with seasonal changes
- **API Key**: Add weather API key for accurate forecasts

### Troubleshooting
- **No Results**: Check that appliances are configured properly
- **API Errors**: Verify API key or use sample data mode
- **Performance**: Reduce number of appliances for faster optimization
- **Visualization**: Ensure matplotlib is properly installed

## 🛠️ Development

### Adding New Features
1. **New Appliances**: Add to default configuration
2. **Additional Metrics**: Extend the metrics display
3. **Custom Visualizations**: Add new chart types
4. **Export Formats**: Support additional file formats

### Code Structure
- **streamlit_app.py**: Main application file
- **Core Modules**: Reused from CLI application
- **Configuration**: Streamlit-specific settings
- **Testing**: Comprehensive test suite

The Streamlit web app provides an intuitive interface for the Solar Energy Optimizer, making it accessible to users who prefer graphical interfaces over command-line tools.