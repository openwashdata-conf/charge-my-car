"""
Visualization module for Solar Energy Optimizer
Creates plots showing solar production and appliance scheduling
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime
from typing import List, Tuple, Dict
from dataclasses import dataclass

from scheduler import ScheduleItem

@dataclass
class PlotConfig:
    """Configuration for plot styling"""
    figure_size: Tuple[int, int] = (15, 10)
    dpi: int = 100
    style: str = 'default'

class SolarVisualizer:
    """Create visualizations for solar production and appliance scheduling"""
    
    def __init__(self, config: PlotConfig = None):
        self.config = config or PlotConfig()
        plt.style.use(self.config.style)
        
        # Color scheme
        self.colors = {
            'solar_production': '#FFA500',  # Orange
            'base_load': '#DC143C',        # Crimson
            'excess_solar': '#32CD32',     # Lime Green
            'grid_power': '#FF4500',       # Red Orange
            'appliance_markers': {
                'Dishwasher': '#4169E1',      # Royal Blue
                'Washing Machine': '#9370DB',  # Medium Purple
                'Dryer': '#FF1493',           # Deep Pink
                'EV Charging': '#00CED1',     # Dark Turquoise
                'Water Heater': '#FF8C00',    # Dark Orange
                'Heat Pump': '#228B22'        # Forest Green
            }
        }
    
    def create_daily_simulation_plot(self, 
                                   production_schedule: List[Tuple[datetime.datetime, float]],
                                   appliance_schedule: List[ScheduleItem],
                                   base_load: float = 2.0,
                                   save_path: str = None) -> None:
        """
        Create a comprehensive daily simulation plot
        
        Args:
            production_schedule: List of (timestamp, solar_output_kW) tuples
            appliance_schedule: List of scheduled appliances
            base_load: Base household load in kW
            save_path: Optional path to save the plot
        """
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=self.config.figure_size, dpi=self.config.dpi)
        
        # Extract data
        timestamps = [item[0] for item in production_schedule]
        solar_output = [item[1] for item in production_schedule]
        
        # Plot 1: Solar Production vs Consumption
        self._plot_production_consumption(ax1, timestamps, solar_output, appliance_schedule, base_load)
        
        # Plot 2: Appliance Schedule Timeline
        self._plot_appliance_timeline(ax2, appliance_schedule, timestamps[0], timestamps[-1])
        
        # Plot 3: Energy Balance and Grid Usage
        self._plot_energy_balance(ax3, timestamps, solar_output, appliance_schedule, base_load)
        
        # Format and save
        self._format_plot(fig, "Daily Solar Energy Optimization")
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.dpi)
            print(f"Plot saved to: {save_path}")
        
        plt.show()
    
    def _plot_production_consumption(self, ax, timestamps, solar_output, appliance_schedule, base_load):
        """Plot solar production vs total consumption"""
        
        # Calculate total consumption at each time point
        total_consumption = self._calculate_hourly_consumption(timestamps, appliance_schedule, base_load)
        
        # Plot solar production
        ax.fill_between(timestamps, 0, solar_output, 
                       alpha=0.7, color=self.colors['solar_production'], 
                       label='Solar Production')
        
        # Plot consumption
        ax.plot(timestamps, total_consumption, 
               linewidth=2, color=self.colors['base_load'], 
               label='Total Consumption')
        
        # Highlight excess solar periods
        excess_solar = [max(0, prod - cons) for prod, cons in zip(solar_output, total_consumption)]
        ax.fill_between(timestamps, 0, excess_solar, 
                       alpha=0.3, color=self.colors['excess_solar'], 
                       label='Excess Solar')
        
        # Add appliance markers
        self._add_appliance_markers(ax, appliance_schedule)
        
        ax.set_ylabel('Power (kW)')
        ax.set_title('Solar Production vs Energy Consumption')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    
    def _plot_appliance_timeline(self, ax, appliance_schedule, start_time, end_time):
        """Plot appliance operation timeline"""
        
        if not appliance_schedule:
            ax.text(0.5, 0.5, 'No appliances scheduled', 
                   transform=ax.transAxes, ha='center', va='center')
            ax.set_ylabel('Appliances')
            ax.set_title('Appliance Schedule Timeline')
            return
        
        # Create timeline bars
        y_pos = range(len(appliance_schedule))
        
        for i, item in enumerate(appliance_schedule):
            # Calculate duration in hours
            duration = (item.end_time - item.start_time).total_seconds() / 3600
            
            # Get color for this appliance
            color = self.colors['appliance_markers'].get(item.appliance.name, '#888888')
            
            # Create horizontal bar
            ax.barh(i, duration, left=mdates.date2num(item.start_time), 
                   height=0.6, color=color, alpha=0.7,
                   label=f"{item.appliance.name} ({item.solar_coverage*100:.0f}% solar)")
            
            # Add power rating text
            ax.text(mdates.date2num(item.start_time) + duration/2, i, 
                   f"{item.appliance.power_rating}kW", 
                   ha='center', va='center', fontsize=9, fontweight='bold')
        
        # Format y-axis
        ax.set_yticks(y_pos)
        ax.set_yticklabels([item.appliance.name for item in appliance_schedule])
        ax.set_ylabel('Appliances')
        ax.set_title('Appliance Operation Schedule')
        
        # Set x-axis limits
        ax.set_xlim(mdates.date2num(start_time), mdates.date2num(end_time))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        
        ax.grid(True, alpha=0.3)
    
    def _plot_energy_balance(self, ax, timestamps, solar_output, appliance_schedule, base_load):
        """Plot energy balance showing grid usage"""
        
        # Calculate grid vs solar usage
        grid_usage = []
        solar_usage = []
        
        for i, (timestamp, production) in enumerate(zip(timestamps, solar_output)):
            # Calculate consumption at this time
            appliance_load = self._get_appliance_load_at_time(timestamp, appliance_schedule)
            total_consumption = base_load + appliance_load
            
            # Determine how much comes from solar vs grid
            solar_used = min(production, total_consumption)
            grid_used = max(0, total_consumption - production)
            
            solar_usage.append(solar_used)
            grid_usage.append(grid_used)
        
        # Stack the usage
        ax.fill_between(timestamps, 0, solar_usage, 
                       alpha=0.7, color=self.colors['excess_solar'], 
                       label='Solar-Powered')
        
        ax.fill_between(timestamps, solar_usage, 
                       [s + g for s, g in zip(solar_usage, grid_usage)], 
                       alpha=0.7, color=self.colors['grid_power'], 
                       label='Grid-Powered')
        
        ax.set_ylabel('Power (kW)')
        ax.set_title('Energy Source Breakdown')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    
    def _calculate_hourly_consumption(self, timestamps, appliance_schedule, base_load):
        """Calculate total consumption for each timestamp"""
        consumption = []
        
        for timestamp in timestamps:
            appliance_load = self._get_appliance_load_at_time(timestamp, appliance_schedule)
            consumption.append(base_load + appliance_load)
        
        return consumption
    
    def _get_appliance_load_at_time(self, timestamp, appliance_schedule):
        """Get total appliance load at a specific time"""
        total_load = 0
        
        for item in appliance_schedule:
            if item.start_time <= timestamp < item.end_time:
                total_load += item.appliance.power_rating
        
        return total_load
    
    def _add_appliance_markers(self, ax, appliance_schedule):
        """Add vertical markers for appliance start/end times"""
        
        for item in appliance_schedule:
            color = self.colors['appliance_markers'].get(item.appliance.name, '#888888')
            
            # Start marker
            ax.axvline(x=item.start_time, color=color, linestyle='--', alpha=0.7, linewidth=1)
            
            # End marker
            ax.axvline(x=item.end_time, color=color, linestyle='--', alpha=0.7, linewidth=1)
            
            # Add label at start time
            ax.text(item.start_time, ax.get_ylim()[1] * 0.9, 
                   f"{item.appliance.name}\n{item.appliance.power_rating}kW", 
                   rotation=90, ha='right', va='top', fontsize=8,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor=color, alpha=0.3))
    
    def _format_plot(self, fig, title):
        """Format the overall plot"""
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Adjust layout
        fig.tight_layout()
        fig.subplots_adjust(top=0.93)
        
        # Add timestamp
        fig.text(0.99, 0.01, f'Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 
                ha='right', va='bottom', fontsize=8, style='italic')
    
    def create_summary_statistics_plot(self, 
                                     production_schedule: List[Tuple[datetime.datetime, float]],
                                     appliance_schedule: List[ScheduleItem],
                                     base_load: float = 2.0,
                                     save_path: str = None) -> None:
        """
        Create a summary statistics plot with pie charts and bar charts
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10), dpi=self.config.dpi)
        
        # Calculate statistics
        stats = self._calculate_energy_statistics(production_schedule, appliance_schedule, base_load)
        
        # Plot 1: Energy source pie chart
        self._plot_energy_source_pie(ax1, stats)
        
        # Plot 2: Appliance energy usage bar chart
        self._plot_appliance_energy_bar(ax2, appliance_schedule)
        
        # Plot 3: Hourly solar efficiency
        self._plot_solar_efficiency(ax3, production_schedule, appliance_schedule, base_load)
        
        # Plot 4: Cost analysis
        self._plot_cost_analysis(ax4, appliance_schedule, stats)
        
        # Format and save
        self._format_plot(fig, "Daily Energy Summary Statistics")
        
        if save_path:
            plt.savefig(save_path, bbox_inches='tight', dpi=self.config.dpi)
            print(f"Summary plot saved to: {save_path}")
        
        plt.show()
    
    def _plot_energy_source_pie(self, ax, stats):
        """Plot pie chart of energy sources"""
        labels = ['Solar Energy', 'Grid Energy']
        sizes = [stats['total_solar_used'], stats['total_grid_used']]
        colors = [self.colors['excess_solar'], self.colors['grid_power']]
        
        ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax.set_title('Energy Source Distribution')
    
    def _plot_appliance_energy_bar(self, ax, appliance_schedule):
        """Plot bar chart of appliance energy usage"""
        if not appliance_schedule:
            ax.text(0.5, 0.5, 'No appliances scheduled', 
                   transform=ax.transAxes, ha='center', va='center')
            ax.set_title('Appliance Energy Usage')
            return
        
        names = [item.appliance.name for item in appliance_schedule]
        energy = [item.appliance.power_rating * item.appliance.duration for item in appliance_schedule]
        colors = [self.colors['appliance_markers'].get(name, '#888888') for name in names]
        
        bars = ax.bar(names, energy, color=colors, alpha=0.7)
        ax.set_ylabel('Energy (kWh)')
        ax.set_title('Appliance Energy Usage')
        ax.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars, energy):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                   f'{value:.1f}', ha='center', va='bottom')
    
    def _plot_solar_efficiency(self, ax, production_schedule, appliance_schedule, base_load):
        """Plot solar efficiency over time"""
        timestamps = [item[0] for item in production_schedule]
        solar_output = [item[1] for item in production_schedule]
        
        efficiency = []
        for i, (timestamp, production) in enumerate(zip(timestamps, solar_output)):
            appliance_load = self._get_appliance_load_at_time(timestamp, appliance_schedule)
            total_consumption = base_load + appliance_load
            
            if total_consumption > 0:
                eff = min(1.0, production / total_consumption)
            else:
                eff = 1.0 if production > 0 else 0.0
            
            efficiency.append(eff * 100)
        
        ax.plot(timestamps, efficiency, linewidth=2, color=self.colors['solar_production'])
        ax.fill_between(timestamps, 0, efficiency, alpha=0.3, color=self.colors['solar_production'])
        ax.set_ylabel('Solar Efficiency (%)')
        ax.set_title('Solar Coverage Efficiency')
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))
    
    def _plot_cost_analysis(self, ax, appliance_schedule, stats):
        """Plot cost analysis"""
        if not appliance_schedule:
            ax.text(0.5, 0.5, 'No cost data available', 
                   transform=ax.transAxes, ha='center', va='center')
            ax.set_title('Cost Analysis')
            return
        
        names = [item.appliance.name for item in appliance_schedule]
        grid_cost = [(1 - item.solar_coverage) * item.appliance.power_rating * item.appliance.duration * 0.12 
                    for item in appliance_schedule]
        savings = [item.cost_savings for item in appliance_schedule]
        
        x = np.arange(len(names))
        width = 0.35
        
        ax.bar(x - width/2, grid_cost, width, label='Grid Cost', color=self.colors['grid_power'], alpha=0.7)
        ax.bar(x + width/2, savings, width, label='Solar Savings', color=self.colors['excess_solar'], alpha=0.7)
        
        ax.set_ylabel('Cost ($)')
        ax.set_title('Cost Analysis by Appliance')
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=45)
        ax.legend()
    
    def _calculate_energy_statistics(self, production_schedule, appliance_schedule, base_load):
        """Calculate comprehensive energy statistics"""
        total_production = sum(output for _, output in production_schedule)
        total_solar_used = 0
        total_grid_used = 0
        
        timestamps = [item[0] for item in production_schedule]
        solar_output = [item[1] for item in production_schedule]
        
        for i, (timestamp, production) in enumerate(zip(timestamps, solar_output)):
            appliance_load = self._get_appliance_load_at_time(timestamp, appliance_schedule)
            total_consumption = base_load + appliance_load
            
            solar_used = min(production, total_consumption)
            grid_used = max(0, total_consumption - production)
            
            total_solar_used += solar_used
            total_grid_used += grid_used
        
        return {
            'total_production': total_production,
            'total_solar_used': total_solar_used,
            'total_grid_used': total_grid_used,
            'total_consumption': total_solar_used + total_grid_used,
            'solar_efficiency': (total_solar_used / (total_solar_used + total_grid_used)) * 100 if (total_solar_used + total_grid_used) > 0 else 0
        }