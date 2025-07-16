"""
Appliance scheduling optimization module
"""

import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

@dataclass
class Appliance:
    """Configuration for electrical appliances"""
    name: str
    power_rating: float  # kW
    duration: float  # hours
    flexibility: int  # 0-10, higher = more flexible timing
    priority: Priority = Priority.MEDIUM
    
@dataclass
class ScheduleItem:
    """Scheduled appliance run"""
    appliance: Appliance
    start_time: datetime.datetime
    end_time: datetime.datetime
    solar_coverage: float  # 0-1, percentage covered by solar
    grid_usage: float  # kW from grid
    cost_savings: float  # estimated savings

class ApplianceScheduler:
    """Optimize appliance scheduling based on solar production"""
    
    def __init__(self, appliances: List[Appliance], base_load: float = 2.0):
        self.appliances = appliances
        self.base_load = base_load  # kW
        self.electricity_rate = 0.12  # $/kWh (default)
    
    def optimize_schedule(self, production_schedule: List[Tuple[datetime.datetime, float]]) -> List[ScheduleItem]:
        """
        Optimize appliance schedule based on solar production
        
        Args:
            production_schedule: List of (timestamp, output_kW) tuples
            
        Returns:
            List of optimized schedule items
        """
        schedule = []
        
        # Sort appliances by priority and flexibility
        sorted_appliances = sorted(
            self.appliances, 
            key=lambda a: (a.priority.value, -a.flexibility),
            reverse=True
        )
        
        # Track used time slots
        used_slots = {}
        
        for appliance in sorted_appliances:
            best_slot = self._find_best_time_slot(
                appliance, production_schedule, used_slots
            )
            
            if best_slot:
                schedule.append(best_slot)
                self._mark_slots_used(best_slot, used_slots)
        
        return schedule
    
    def _find_best_time_slot(self, appliance: Appliance, 
                           production_schedule: List[Tuple[datetime.datetime, float]],
                           used_slots: Dict[datetime.datetime, float]) -> Optional[ScheduleItem]:
        """
        Find the best time slot for an appliance
        
        Args:
            appliance: Appliance to schedule
            production_schedule: Solar production schedule
            used_slots: Already used time slots
            
        Returns:
            Best schedule item or None if no suitable slot found
        """
        best_slot = None
        best_score = -1
        
        duration_slots = int(appliance.duration)  # Assuming hourly slots
        
        # Try each possible starting time
        for i in range(len(production_schedule) - duration_slots + 1):
            start_time = production_schedule[i][0]
            
            # Check if this slot is available
            if self._is_slot_available(start_time, duration_slots, used_slots, appliance.power_rating):
                score = self._calculate_slot_score(
                    appliance, start_time, duration_slots, production_schedule, used_slots
                )
                
                if score > best_score:
                    best_score = score
                    best_slot = self._create_schedule_item(
                        appliance, start_time, duration_slots, production_schedule, used_slots
                    )
        
        return best_slot
    
    def _is_slot_available(self, start_time: datetime.datetime, duration: int, 
                          used_slots: Dict[datetime.datetime, float], power_needed: float) -> bool:
        """Check if a time slot is available for scheduling"""
        current_time = start_time
        
        for _ in range(duration):
            if current_time in used_slots:
                if used_slots[current_time] + power_needed > 10:  # Assume 10kW max capacity
                    return False
            current_time += datetime.timedelta(hours=1)
        
        return True
    
    def _calculate_slot_score(self, appliance: Appliance, start_time: datetime.datetime,
                            duration: int, production_schedule: List[Tuple[datetime.datetime, float]],
                            used_slots: Dict[datetime.datetime, float]) -> float:
        """
        Calculate score for a potential time slot
        Higher score = better slot
        """
        score = 0
        current_time = start_time
        
        # Find production data for this time slot
        for i, (timestamp, production) in enumerate(production_schedule):
            if timestamp == start_time:
                for j in range(duration):
                    if i + j < len(production_schedule):
                        _, slot_production = production_schedule[i + j]
                        used_power = used_slots.get(current_time, 0)
                        available_solar = max(0, slot_production - self.base_load - used_power)
                        
                        # Score based on solar coverage
                        solar_coverage = min(1.0, available_solar / appliance.power_rating)
                        score += solar_coverage * 100
                        
                        # Bonus for high-flexibility appliances in peak solar hours
                        if 10 <= current_time.hour <= 16 and appliance.flexibility > 7:
                            score += 20
                        
                        current_time += datetime.timedelta(hours=1)
                break
        
        return score
    
    def _create_schedule_item(self, appliance: Appliance, start_time: datetime.datetime,
                            duration: int, production_schedule: List[Tuple[datetime.datetime, float]],
                            used_slots: Dict[datetime.datetime, float]) -> ScheduleItem:
        """Create a schedule item with calculated metrics"""
        end_time = start_time + datetime.timedelta(hours=duration)
        
        total_energy = appliance.power_rating * appliance.duration
        solar_energy = 0
        grid_energy = 0
        
        current_time = start_time
        
        # Calculate solar vs grid energy usage
        for i, (timestamp, production) in enumerate(production_schedule):
            if timestamp == start_time:
                for j in range(duration):
                    if i + j < len(production_schedule):
                        _, slot_production = production_schedule[i + j]
                        used_power = used_slots.get(current_time, 0)
                        available_solar = max(0, slot_production - self.base_load - used_power)
                        
                        solar_used = min(appliance.power_rating, available_solar)
                        grid_used = appliance.power_rating - solar_used
                        
                        solar_energy += solar_used
                        grid_energy += grid_used
                        
                        current_time += datetime.timedelta(hours=1)
                break
        
        solar_coverage = solar_energy / total_energy if total_energy > 0 else 0
        cost_savings = solar_energy * self.electricity_rate
        
        return ScheduleItem(
            appliance=appliance,
            start_time=start_time,
            end_time=end_time,
            solar_coverage=solar_coverage,
            grid_usage=grid_energy,
            cost_savings=cost_savings
        )
    
    def _mark_slots_used(self, schedule_item: ScheduleItem, used_slots: Dict[datetime.datetime, float]):
        """Mark time slots as used"""
        current_time = schedule_item.start_time
        
        while current_time < schedule_item.end_time:
            if current_time not in used_slots:
                used_slots[current_time] = 0
            used_slots[current_time] += schedule_item.appliance.power_rating
            current_time += datetime.timedelta(hours=1)
    
    def get_schedule_summary(self, schedule: List[ScheduleItem]) -> Dict:
        """Get summary statistics for the schedule"""
        total_energy = sum(item.appliance.power_rating * item.appliance.duration for item in schedule)
        total_solar_energy = sum(item.solar_coverage * item.appliance.power_rating * item.appliance.duration for item in schedule)
        total_grid_energy = sum(item.grid_usage for item in schedule)
        total_savings = sum(item.cost_savings for item in schedule)
        
        return {
            'total_energy': total_energy,
            'solar_energy': total_solar_energy,
            'grid_energy': total_grid_energy,
            'solar_percentage': (total_solar_energy / total_energy * 100) if total_energy > 0 else 0,
            'cost_savings': total_savings,
            'scheduled_appliances': len(schedule)
        }
    
    def recommend_deferrals(self, schedule: List[ScheduleItem], 
                          production_schedule: List[Tuple[datetime.datetime, float]]) -> List[str]:
        """Recommend appliances to defer for better solar usage"""
        recommendations = []
        
        # Find appliances with low solar coverage
        low_solar_items = [item for item in schedule if item.solar_coverage < 0.5]
        
        for item in low_solar_items:
            if item.appliance.flexibility > 5:
                # Look for better time slots
                better_slots = self._find_better_slots(item, production_schedule)
                if better_slots:
                    recommendations.append(
                        f"Consider running {item.appliance.name} at {better_slots[0].strftime('%H:%M')} "
                        f"for {int(better_slots[1] * 100)}% solar coverage"
                    )
        
        return recommendations
    
    def _find_better_slots(self, schedule_item: ScheduleItem, 
                         production_schedule: List[Tuple[datetime.datetime, float]]) -> Optional[Tuple[datetime.datetime, float]]:
        """Find better time slots with higher solar coverage"""
        best_time = None
        best_coverage = schedule_item.solar_coverage
        
        duration_slots = int(schedule_item.appliance.duration)
        
        for i in range(len(production_schedule) - duration_slots + 1):
            start_time = production_schedule[i][0]
            
            # Skip current slot
            if start_time == schedule_item.start_time:
                continue
            
            # Calculate potential solar coverage
            coverage = self._calculate_potential_coverage(
                schedule_item.appliance, start_time, duration_slots, production_schedule
            )
            
            if coverage > best_coverage:
                best_coverage = coverage
                best_time = start_time
        
        return (best_time, best_coverage) if best_time else None
    
    def _calculate_potential_coverage(self, appliance: Appliance, start_time: datetime.datetime,
                                    duration: int, production_schedule: List[Tuple[datetime.datetime, float]]) -> float:
        """Calculate potential solar coverage for a time slot"""
        solar_energy = 0
        total_energy = appliance.power_rating * appliance.duration
        
        for i, (timestamp, production) in enumerate(production_schedule):
            if timestamp == start_time:
                for j in range(duration):
                    if i + j < len(production_schedule):
                        _, slot_production = production_schedule[i + j]
                        available_solar = max(0, slot_production - self.base_load)
                        solar_used = min(appliance.power_rating, available_solar)
                        solar_energy += solar_used
                break
        
        return solar_energy / total_energy if total_energy > 0 else 0