#!/usr/bin/env python3
"""
Quick plotting demo for Solar Energy Optimizer
Shows a simple example of the visualization capabilities
"""

import matplotlib.pyplot as plt
import datetime

def simple_plot_demo():
    """Create a simple demo plot without running the full simulation"""
    
    print("🎨 Solar Energy Optimizer - Quick Plot Demo")
    print("=" * 45)
    
    # Create sample data for a typical day
    hours = list(range(24))
    timestamps = [datetime.datetime.now().replace(hour=h, minute=0, second=0, microsecond=0) for h in hours]
    
    # Simulate solar production curve
    import math
    solar_production = []
    for h in hours:
        if h < 6 or h > 18:
            solar_production.append(0)
        else:
            # Bell curve for solar production
            sun_factor = math.sin(math.pi * (h - 6) / 12)
            cloud_factor = 0.8 + 0.2 * math.sin(2 * math.pi * h / 24)  # Some cloud variation
            solar_production.append(6.0 * sun_factor * cloud_factor)
    
    # Base load (always on)
    base_load = [2.0] * 24
    
    # Appliance usage
    appliance_usage = [0] * 24
    
    # EV Charging: 10 AM - 4 PM
    for h in range(10, 16):
        appliance_usage[h] += 7.2
    
    # Dishwasher: 12 PM - 1:30 PM
    for h in range(12, 14):
        appliance_usage[h] += 1.5
    
    # Washing Machine: 11 AM - 12 PM
    appliance_usage[11] += 0.8
    
    # Dryer: 2 PM - 3:30 PM
    for h in range(14, 16):
        appliance_usage[h] += 3.0
    
    # Total consumption
    total_consumption = [base + app for base, app in zip(base_load, appliance_usage)]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot solar production
    ax.fill_between(hours, 0, solar_production, alpha=0.7, color='#FFA500', label='Solar Production')
    
    # Plot consumption
    ax.plot(hours, total_consumption, linewidth=3, color='#DC143C', label='Total Consumption')
    ax.plot(hours, base_load, linewidth=2, color='#4169E1', linestyle='--', label='Base Load')
    
    # Mark appliance operations
    appliance_colors = {'EV Charging': '#00CED1', 'Dishwasher': '#4169E1', 
                       'Washing Machine': '#9370DB', 'Dryer': '#FF1493'}
    
    # EV Charging marker
    ax.axvspan(10, 16, alpha=0.2, color=appliance_colors['EV Charging'], label='EV Charging')
    
    # Dishwasher marker
    ax.axvspan(12, 14, alpha=0.3, color=appliance_colors['Dishwasher'], label='Dishwasher')
    
    # Washing Machine marker
    ax.axvspan(11, 12, alpha=0.3, color=appliance_colors['Washing Machine'], label='Washing Machine')
    
    # Dryer marker
    ax.axvspan(14, 16, alpha=0.3, color=appliance_colors['Dryer'], label='Dryer')
    
    # Formatting
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Power (kW)')
    ax.set_title('Solar Energy Optimizer - Daily Schedule Demo', fontsize=16, fontweight='bold')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    # Set hour labels
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels([f'{h:02d}:00' for h in range(0, 24, 2)])
    
    # Add annotations
    ax.annotate('Peak Solar\nProduction', xy=(12, 6), xytext=(15, 8),
                arrowprops=dict(arrowstyle='->', color='orange', lw=2),
                fontsize=12, ha='center', 
                bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', alpha=0.7))
    
    ax.annotate('Optimized\nEV Charging', xy=(13, 10), xytext=(9, 12),
                arrowprops=dict(arrowstyle='->', color='darkturquoise', lw=2),
                fontsize=12, ha='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='lightblue', alpha=0.7))
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('plot_demo.png', dpi=100, bbox_inches='tight')
    print("✅ Demo plot saved as 'plot_demo.png'")
    
    # Display key metrics
    total_solar = sum(solar_production)
    total_consumption_sum = sum(total_consumption)
    solar_coverage = min(total_solar, total_consumption_sum) / total_consumption_sum * 100
    
    print(f"\n📊 Demo Metrics:")
    print(f"   Total Solar Production: {total_solar:.1f} kWh")
    print(f"   Total Consumption: {total_consumption_sum:.1f} kWh")
    print(f"   Solar Coverage: {solar_coverage:.1f}%")
    print(f"   Estimated Savings: ${(min(total_solar, total_consumption_sum) * 0.12):.2f}")
    
    # Show when to run appliances
    print(f"\n💡 Optimal Appliance Schedule:")
    print(f"   🚗 EV Charging: 10:00-16:00 (during peak solar)")
    print(f"   🍽️  Dishwasher: 12:00-14:00 (midday peak)")
    print(f"   👕 Washing Machine: 11:00-12:00 (good solar)")
    print(f"   🔥 Dryer: 14:00-16:00 (afternoon solar)")
    
    plt.show()

if __name__ == "__main__":
    simple_plot_demo()
    
    print("\n🎉 Demo complete! For full simulation, run: python daily_simulation.py")