"""
visualizations.py
Final visualization kit with Speed and Epsilon controls.
"""

import matplotlib
import numpy as np

matplotlib.use("TkAgg")
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.widgets as widgets
import seaborn as sns
from matplotlib.colors import ListedColormap
from matplotlib.patches import Rectangle

plt.ion()  # Non-blocking mode
sns.set_palette("husl")


def show_non_blocking():
    """Draw canvas but return control to terminal."""
    plt.draw()
    plt.pause(0.001)


class VisualizationManager:
    """Handles all visuals + optional GUI controls."""

    def __init__(self):
        plt.style.use("seaborn-v0_8-darkgrid")
        # colormap: 0 clean 1 dirt 2 obstacle 3 charger 4 visited 5 vacuum
        self.cmap = ListedColormap(
            ["white", "saddlebrown", "black", "green", "royalblue", "red"]
        )
        self.fig = None
        self.ax = None
        self.texts = {}
        self.speed_slider = None  # Reference to speed slider

    # ----------  Interactive Sliders  ----------
    def add_epsilon_slider(self, initial_eps, vacuum):
        """Adds a slider to adjust greedy-ness of A* (Top slider)."""
        if self.fig is None:
            return None

        # Position: [left, bottom, width, height]
        ax_eps = self.fig.add_axes([0.25, 0.06, 0.45, 0.03])
        slider = widgets.Slider(
            ax_eps, "ε (Greedy)", 1.0, 5.0, valinit=initial_eps, valstep=0.1
        )

        def _upd(val):
            vacuum.epsilon = round(val, 1)

        slider.on_changed(_upd)
        return slider

    def add_speed_slider(self):
        """Adds a slider to adjust simulation speed (Bottom slider)."""
        if self.fig is None:
            return None

        # Position: [left, bottom, width, height]
        ax_speed = self.fig.add_axes([0.25, 0.02, 0.45, 0.03])
        # valinit=0.2 is the default delay (slower/watchable)
        slider = widgets.Slider(
            ax_speed, "Delay (s)", 0.01, 1.0, valinit=0.2, valstep=0.01
        )

        self.speed_slider = slider
        return slider

    # ----------  Drawing Helpers  ----------
    def display_initial_state(self, env, vacuum):
        # Close any existing figures to prevent stacking
        plt.close("all")
        self.fig, self.ax = plt.subplots(figsize=(10, 8))

        # Adjust subplot to make room for sliders at bottom
        plt.subplots_adjust(bottom=0.15)

        self._draw_grid(env, vacuum, "Initial State")
        show_non_blocking()

    def update_display(self, env, vacuum, step):
        if self.ax is None or not plt.fignum_exists(self.fig.number):
            return

        img = self._build_display_array(env, vacuum)

        # Optimize: Update data instead of redrawing everything
        if len(self.ax.images) > 0:
            self.ax.images[0].set_array(img)
        else:
            self.ax.imshow(img, cmap=self.cmap, vmin=0, vmax=5)

        self.ax.set_title(
            f"Step {step} – {vacuum.strategy.upper()}  ε={vacuum.epsilon}",
            fontsize=14,
            fontweight="bold",
        )

        if "battery" in self.texts:
            self.texts["battery"].set_text(str(vacuum.battery))
        if "stats" in self.texts:
            self.texts["stats"].set_text(
                f"Cleaned: {vacuum.cleaned} | Visited: {len(vacuum.visited)}"
            )

        show_non_blocking()

    def show_final_stats(self, vacuum):
        if self.ax is None or not plt.fignum_exists(self.fig.number):
            return

        summary = vacuum.metrics.generate_summary()
        txt = (
            f"SIMULATION COMPLETE\n\n"
            f"Steps: {summary['total_steps']}   Dirt: {summary['dirt_cleaned']}\n"
            f"Efficiency: {summary['efficiency']:.3f}   Coverage: {summary['coverage_percentage']:.1f}%"
        )

        self.ax.text(
            0.5,
            0.5,
            txt,
            transform=self.ax.transAxes,
            ha="center",
            va="center",
            bbox=dict(boxstyle="round,pad=0.7", facecolor="lightyellow"),
            fontsize=12,
            family="monospace",
        )
        show_non_blocking()

    # ----------  Comparison Charts  ----------
    def create_comparison_charts(self, results):
        fig, axs = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("Strategy Comparison", fontsize=16, fontweight="bold")
        strategies = list(results.keys())
        colours = ["red", "blue", "green"]

        def get_metric(s, key):
            return [r[key] for r in results[s]]

        steps = [get_metric(s, "steps") for s in strategies]
        bp1 = axs[0, 0].boxplot(steps, labels=strategies, patch_artist=True)
        for patch, col in zip(bp1["boxes"], colours):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        axs[0, 0].set_title("Steps")
        axs[0, 0].set_ylabel("count")

        eff = [get_metric(s, "efficiency") for s in strategies]
        bp2 = axs[0, 1].boxplot(eff, labels=strategies, patch_artist=True)
        for patch, col in zip(bp2["boxes"], colours):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        axs[0, 1].set_title("Efficiency")
        axs[0, 1].set_ylabel("dirt/step")

        cov = [get_metric(s, "coverage") for s in strategies]
        bp3 = axs[1, 0].boxplot(cov, labels=strategies, patch_artist=True)
        for patch, col in zip(bp3["boxes"], colours):
            patch.set_facecolor(col)
            patch.set_alpha(0.7)
        axs[1, 0].set_title("Coverage %")
        axs[1, 0].set_ylabel("percent")

        succ = []
        for s in strategies:
            total = len(results[s])
            if total == 0:
                succ.append(0)
            else:
                wins = sum(1 for r in results[s] if r["dirt_cleaned"] >= 1)
                succ.append(wins / total)

        bars = axs[1, 1].bar(strategies, succ, color=colours, alpha=0.7)
        axs[1, 1].set_title("Success Rate")
        axs[1, 1].set_ylabel("rate")
        axs[1, 1].set_ylim(0, 1.1)
        for bar, v in zip(bars, succ):
            axs[1, 1].text(
                bar.get_x() + bar.get_width() / 2,
                v + 0.02,
                f"{v:.1%}",
                ha="center",
                va="bottom",
                fontweight="bold",
            )

        plt.tight_layout()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"strategy_comparison_{ts}.png"
        plt.savefig(fname, dpi=300, bbox_inches="tight")
        print(f"Comparison chart saved: {fname}")
        plt.show(block=True)

    # ----------  Internal Helpers  ----------
    def _draw_grid(self, env, vacuum, title):
        self.ax.clear()
        img = self._build_display_array(env, vacuum)
        self.ax.imshow(img, cmap=self.cmap, vmin=0, vmax=5)

        self.ax.set_xticks(np.arange(-0.5, env.size, 1), minor=True)
        self.ax.set_yticks(np.arange(-0.5, env.size, 1), minor=True)
        self.ax.grid(which="minor", color="gray", linewidth=1)
        self.ax.set_title(title, fontsize=14, fontweight="bold")

        legend_patches = [
            Rectangle((0, 0), 1, 1, facecolor="white", edgecolor="k", label="Clean"),
            Rectangle((0, 0), 1, 1, facecolor="saddlebrown", label="Dirt"),
            Rectangle((0, 0), 1, 1, facecolor="black", label="Obstacle"),
            Rectangle((0, 0), 1, 1, facecolor="green", label="Charger"),
            Rectangle((0, 0), 1, 1, facecolor="royalblue", label="Visited"),
            Rectangle((0, 0), 1, 1, facecolor="red", label="Vacuum"),
        ]
        self.ax.legend(
            handles=legend_patches, loc="upper right", bbox_to_anchor=(1.15, 1)
        )

        bat = self.ax.text(
            0.02,
            0.98,
            str(vacuum.battery),
            transform=self.ax.transAxes,
            va="top",
            bbox=dict(boxstyle="round", facecolor="lightblue"),
        )
        stats = self.ax.text(
            0.02,
            0.02,
            f"Cleaned: {vacuum.cleaned} | Visited: {len(vacuum.visited)}",
            transform=self.ax.transAxes,
            bbox=dict(boxstyle="round", facecolor="lightgreen"),
        )
        self.texts = {"battery": bat, "stats": stats}

    def _build_display_array(self, env, vacuum):
        arr = np.zeros((env.size, env.size), dtype=int)
        for y in range(env.size):
            for x in range(env.size):
                val = env.grid[y][x]
                if val == -1:
                    arr[y, x] = 2  # obstacle
                elif val == 1:
                    arr[y, x] = 1  # dirt
                elif val == 2:
                    arr[y, x] = 3  # charger
                elif val == 0:
                    arr[y, x] = 0  # clean
                if (x, y) in vacuum.visited and arr[y, x] == 0:
                    arr[y, x] = 4  # visited
        arr[vacuum.y, vacuum.x] = 5
        return arr
