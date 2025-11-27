"""
main.py
Final entry point.
Includes Speed Slider support and Robust Quit.
"""

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

# --- Imports ---
from environment.grid import Environment
from agent.vaccum import VaccumCleaner
from utils.visualizations import VisualizationManager
from utils.strategy_comparison import StrategyComparator
# ---------------

class GuiController:
    """Toolbar + event loop for figure-window control."""

    def __init__(self, env, vacuum, viz):
        self.env = env
        self.vac = vacuum
        self.viz = viz
        
        # State Flags
        self.running = False  
        self.quit_requested = False
        self.finished = False
        self.step_cnt = 0
        
        self._build_widgets()

    def _build_widgets(self):
        # Run/Pause Button (Bottom Left)
        ax_run = plt.axes([0.01, 0.01, 0.08, 0.04])
        self.btn_run = plt.Button(ax_run, 'Run/Pause')
        self.btn_run.on_clicked(self._toggle_run)

        # Quit Button (Bottom Right)
        ax_quit = plt.axes([0.90, 0.01, 0.08, 0.04])
        self.btn_quit = plt.Button(ax_quit, 'Quit')
        self.btn_quit.on_clicked(self._request_quit)

    def _toggle_run(self, event):
        self.running = not self.running

    def _request_quit(self, event):
        self.quit_requested = True
        self.running = False

    def run_event_loop(self):
        print("GUI Controls: [Run/Pause] to toggle, [Quit] to close.")
        print("Use the 'Delay' slider to control speed.")
        
        while not self.quit_requested:
            # 1. Check if Window was closed (OS 'X' button)
            if not plt.fignum_exists(self.viz.fig.number):
                print("Window closed by user.")
                break

            # 2. Simulation Logic
            if self.running and not self.finished:
                if not self.env.get_dirty_cells() or self.vac.battery.is_empty():
                    self.finished = True
                    self.running = False
                    self.viz.show_final_stats(self.vac)
                else:
                    self.vac.step()
                    self.step_cnt += 1
                    
                    self.viz.update_display(self.env, self.vac, self.step_cnt)
                    
                    # DYNAMIC DELAY: Read from the slider
                    # Default to 0.2s if slider isn't ready
                    delay = self.viz.speed_slider.val if self.viz.speed_slider else 0.2
                    plt.pause(delay) 

            # 3. Idle Handling
            else:
                plt.pause(0.1)

        plt.close('all')
        print("Simulation exited.")


# ----------  simulation runners  ----------

def run_single_simulation(strategy='astar', visualize=True, epsilon=1.0):
    print(f"=== Running {strategy.upper()} Strategy ===")

    # CLI Path (Fast, no GUI)
    if not visualize:
        env = Environment(size=5, dirt_prob=0.3)
        vacuum = VaccumCleaner(env, strategy=strategy, epsilon=epsilon)
        for _ in range(100):
            if not env.get_dirty_cells() or vacuum.battery.is_empty():
                break
            vacuum.step()
        summary = vacuum.metrics.generate_summary()
        print(f"Done. Steps: {summary['total_steps']}, Cleaned: {summary['dirt_cleaned']}")
        return summary

    # GUI Path
    env = Environment(size=5, dirt_prob=0.3)
    vacuum = VaccumCleaner(env, strategy=strategy, epsilon=epsilon)
    
    viz = VisualizationManager()
    viz.display_initial_state(env, vacuum)
    
    # Add controls
    viz.add_speed_slider() # <--- New Speed Slider
    if strategy == 'astar':
        viz.add_epsilon_slider(epsilon, vacuum)

    ctrl = GuiController(env, vacuum, viz)
    ctrl.run_event_loop()

def run_strategy_comparison():
    print("=== Running Strategy Comparison ===")
    comp = StrategyComparator(runs_per_strategy=5)
    results = comp.run_comparison()
    viz = VisualizationManager()
    viz.create_comparison_charts(results)
    return comp.generate_report()

def interactive_demo():
    print("=== Interactive Demo ===")
    for strat in ('random', 'astar', 'optimized'):
        input(f"\nPress Enter to run {strat.upper()} strategy...")
        run_single_simulation(strat, visualize=True)


# ----------  main menu  ----------

def main():
    print("Vacuum Cleaner AI Simulation")
    print("================================")
    while True:
        print("\nOptions:")
        print("1. Single Simulation (Visualized)")
        print("2. Strategy Comparison")
        print("3. Interactive Demo")
        print("4. Quick Run (Console only)")
        print("5. Exit")

        choice = input("\nSelect option (1-5): ").strip()
        
        try:
            if choice == '1':
                strat = input("Strategy (random/astar/optimized) [astar]: ").strip() or 'astar'
                eps = 1.0
                if strat == 'astar':
                    val = input("Weighted-A* epsilon (≥1) [1.0]: ").strip()
                    eps = float(val) if val else 1.0
                run_single_simulation(strat, visualize=True, epsilon=eps)

            elif choice == '2':
                run_strategy_comparison()

            elif choice == '3':
                interactive_demo()

            elif choice == '4':
                strat = input("Strategy (random/astar/optimized) [astar]: ").strip() or 'astar'
                run_single_simulation(strat, visualize=False)

            elif choice == '5':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")
                
        except KeyboardInterrupt:
            print("\nUser interrupted.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()