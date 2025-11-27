"""
vacuum.py
----------
Enhanced VacuumCleaner agent with battery management,
multiple strategies, and performance optimization.
"""

import heapq
import random

from utils.metrics import PerformanceMetrics

from .battery import Battery


class VaccumCleaner:
    def __init__(self, env, strategy="astar", epsilon=1.0):
        """
        Initialize the vacuum cleaner agent.

        Args:
            env (Environment): The environment grid
            strategy (str): Cleaning strategy ('random', 'astar', 'optimized')
        """
        self.env = env
        self.x, self.y = 0, 0
        self.cleaned = 0
        self.epsilon = max(1.0, epsilon)  # ε ≥ 1
        self.battery = Battery()
        self.visited = set()
        self.path = []
        self.strategy = strategy
        self.metrics = PerformanceMetrics()
        self.charger_pos = (env.size - 1, env.size - 1)  # Bottom-right corner

    def clean(self):
        """Clean current cell if dirty."""
        if self.env.grid[self.y][self.x] == 1:
            self.env.grid[self.y][self.x] = 0
            self.cleaned += 1
            self.metrics.record_cleaning(self.strategy)
        self.visited.add((self.x, self.y))

    def step(self):
        """Perform one simulation step based on strategy."""
        # Check battery and charging needs
        if self.battery.needs_charging() and self.strategy != "random":
            self._handle_low_battery()
            return

        # Execute strategy
        if self.strategy == "random":
            self._random_step()
        elif self.strategy == "astar":
            self._astar_step()
        elif self.strategy == "optimized":
            self._optimized_step()

        # Record metrics
        self.metrics.record_step(
            (self.x, self.y), self.battery.current, "move", self.strategy
        )

        # Clean current position
        self.clean()

    def _random_step(self):
        """Random movement strategy."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        dx, dy = random.choice(directions)
        new_x, new_y = self.x + dx, self.y + dy

        if (
            0 <= new_x < self.env.size
            and 0 <= new_y < self.env.size
            and self.env.grid[new_y][new_x] != -1
        ):
            self.x, self.y = new_x, new_y
            self.battery.consume()

    def _astar_step(self):
        """A* pathfinding strategy."""
        if not self.path:
            dirty_cells = self.env.get_dirty_cells()
            if dirty_cells:
                nearest = self.get_nearest_dirty(dirty_cells)
                self.path = self.a_star((self.x, self.y), nearest)

        if self.path:
            next_cell = self.path.pop(0)
            self.x, self.y = next_cell
            self.battery.consume()

    def _optimized_step(self):
        """Optimized strategy with battery awareness."""
        if self.battery.current < 30:  # Conserve energy
            # Only clean nearby dirt
            nearby_dirt = self._get_nearby_dirt(radius=2)
            if nearby_dirt:
                if not self.path or self.path[-1] != nearby_dirt[0]:
                    self.path = self.a_star((self.x, self.y), nearby_dirt[0])
        else:
            self._astar_step()

    def _handle_low_battery(self):
        """Return to charger when battery is low."""
        if (self.x, self.y) == self.charger_pos:
            self.battery.charge()
            self.metrics.record_step(
                (self.x, self.y), self.battery.current, "charging", self.strategy
            )
        else:
            # Navigate to charger
            if not self.path or self.path[-1] != self.charger_pos:
                self.path = self.a_star((self.x, self.y), self.charger_pos)

            if self.path:
                next_cell = self.path.pop(0)
                self.x, self.y = next_cell
                self.battery.consume()

    def _get_nearby_dirt(self, radius=2):
        """Find dirt within specified radius."""
        nearby = []
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                nx, ny = self.x + dx, self.y + dy
                if (
                    0 <= nx < self.env.size
                    and 0 <= ny < self.env.size
                    and self.env.grid[ny][nx] == 1
                ):
                    nearby.append((nx, ny))
        return sorted(nearby, key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))

    def get_nearest_dirty(self, dirty_cells):
        """Return the closest dirty cell based on Manhattan distance."""
        return min(dirty_cells, key=lambda c: abs(c[0] - self.x) + abs(c[1] - self.y))

    def a_star(self, start, goal):
        """Perform A* pathfinding from start to goal avoiding obstacles."""
        grid = self.env.grid
        size = self.env.size
        open_set = []
        heapq.heappush(open_set, (0 + self.heuristic(start, goal), 0, start, [start]))
        visited = set()

        while open_set:
            f, g, current, path = heapq.heappop(open_set)
            if current == goal:
                return path[1:]
            if current in visited:
                continue
            visited.add(current)
            x, y = current

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < size and 0 <= ny < size and grid[ny][nx] != -1:
                    neighbor = (nx, ny)
                    if neighbor not in visited:
                        g_new = g + 1
                        f_new = g_new + self.epsilon * self.heuristic(neighbor, goal)
                        heapq.heappush(
                            open_set, (f_new, g_new, neighbor, path + [neighbor])
                        )

        return []

    def heuristic(self, a, b):
        """Compute Manhattan distance heuristic between points a and b."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
