"""
strategy_comparison.py
----------------------
Compare different cleaning strategies and analyze performance.
"""

import matplotlib.pyplot as plt
import numpy as np
from environment.grid import Environment
from agent.vacuum import VaccumCleaner
import json

class StrategyComparator:
    def __init__(self, grid_size=5, dirt_prob=0.3, runs_per_strategy=5):
        """Initialize comparison framework."""
        self.grid_size = grid_size
        self.dirt_prob = dirt_prob
        self.runs_per_strategy = runs_per_strategy
        self.strategies = ['random', 'astar', 'optimized']
        self.results = {}
        
    def run_comparison(self):
        """Run comprehensive strategy comparison."""
        for strategy in self.strategies:
            print(f"Testing {strategy} strategy...")
            strategy_results = []

            epsilons = [1.0, 1.5, 2.0] if strategy == 'astar' else [None]

            for eps in epsilons:
                for run in range(self.runs_per_strategy):
                    env = Environment(self.grid_size, self.dirt_prob)
                    
                    if strategy == 'astar':
                        vacuum = vacuumCleaner(env, strategy='astar', epsilon=eps)
                    else:
                        vacuum = vacuumCleaner(env, strategy)

                    # Run simulation
                    max_steps = 100
                    for step in range(max_steps):
                        if not env.get_dirty_cells() or vacuum.battery.is_empty():
                            break
                        vacuum.step()

                    # Collect results
                    result = {
                        'run': run + 1,
                        'epsilon': eps,
                        'steps': vacuum.metrics.steps_taken,
                        'dirt_cleaned': vacuum.cleaned,
                        'battery_used': vacuum.battery.total_consumed,
                        'efficiency': vacuum.metrics.calculate_efficiency(),
                        'coverage': vacuum.metrics.calculate_coverage(self.grid_size**2),
                        'battery_remaining': vacuum.battery.current
                    }
                    strategy_results.append(result)

            self.results[strategy] = strategy_results

        return self.results
    
    def generate_report(self):
        """Generate detailed comparison report."""
        report = {}
        
        for strategy in self.strategies:
            results = self.results[strategy]
            steps = [r['steps'] for r in results]
            efficiency = [r['efficiency'] for r in results]
            coverage = [r['coverage'] for r in results]
            
            report[strategy] = {
                'avg_steps': np.mean(steps),
                'std_steps': np.std(steps),
                'avg_efficiency': np.mean(efficiency),
                'avg_coverage': np.mean(coverage),
                'success_rate': len([r for r in results if r['dirt_cleaned'] >= 6]) / len(results)
            }
            
        return report
    
    def save_results(self, filename='comparison_results.json'):
        """Save results to JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                'summary': self.generate_report(),
                'raw_results': self.results
            }, f, indent=2)
        return filename