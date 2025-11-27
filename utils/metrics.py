"""
metrics.py
-----------
Performance tracking and analysis for vacuum cleaner simulation.
Records efficiency, coverage, energy usage, and cleaning effectiveness.
"""

import time
import json
from datetime import datetime

class PerformanceMetrics:
    def __init__(self):
        """Initialize metrics tracking."""
        self.start_time = time.time()
        self.steps_taken = 0
        self.dirt_cleaned = 0
        self.cells_visited = set()
        self.battery_usage = []
        self.path_efficiency = []
        self.decisions_made = []
        
        # Strategy comparison metrics
        self.strategies_tested = {
            'random': {'steps': 0, 'dirt_cleaned': 0, 'efficiency': 0},
            'astar': {'steps': 0, 'dirt_cleaned': 0, 'efficiency': 0},
            'optimized': {'steps': 0, 'dirt_cleaned': 0, 'efficiency': 0}
        }
        
    def record_step(self, position, battery_level, action, strategy='astar'):
        """Record a single simulation step."""
        self.steps_taken += 1
        self.cells_visited.add(position)
        self.battery_usage.append(battery_level)
        self.decisions_made.append({
            'step': self.steps_taken,
            'position': position,
            'action': action,
            'battery': battery_level,
            'strategy': strategy
        })
        
    def record_cleaning(self, strategy='astar'):
        """Record dirt cleaning event."""
        self.dirt_cleaned += 1
        if strategy in self.strategies_tested:
            self.strategies_tested[strategy]['dirt_cleaned'] += 1
            
    def calculate_coverage(self, total_cells):
        """Calculate percentage of cells visited."""
        return (len(self.cells_visited) / total_cells) * 100
    
    def calculate_efficiency(self):
        """Calculate cleaning efficiency (dirt per step)."""
        if self.steps_taken == 0:
            return 0
        return self.dirt_cleaned / self.steps_taken
    
    def calculate_energy_efficiency(self):
        """Calculate energy used per dirt cleaned."""
        if self.dirt_cleaned == 0:
            return 0
        return sum(self.battery_usage) / self.dirt_cleaned
    
    def generate_summary(self):
        """Generate performance summary."""
        return {
            'simulation_time': time.time() - self.start_time,
            'total_steps': self.steps_taken,
            'dirt_cleaned': self.dirt_cleaned,
            'coverage_percentage': self.calculate_coverage(25),  # 5x5 grid
            'efficiency': self.calculate_efficiency(),
            'energy_efficiency': self.calculate_energy_efficiency(),
            'strategies_comparison': self.strategies_tested
        }
    
    def save_report(self, filename='simulation_report.json'):
        """Save detailed metrics to file."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': self.generate_summary(),
            'detailed_steps': self.decisions_made,
            'battery_usage': self.battery_usage
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename