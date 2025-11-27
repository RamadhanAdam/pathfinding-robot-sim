import random

"""
grid.py
--------
Defines the Environment class that represents the vacuum cleaner's world.

The environment is a grid (2D matrix) where:
  0 = clean/empty cell
  1 = dirty cell
 -1 = obstacle/wall
  2 = charging station (future use)
"""


class Environment:
    def __init__(self, size=5, dirt_prob=0.2):
        """
        Initialize a grid environment.

        Args:
            size (int): Dimension of the square grid.
            dirt_prob (float): Probability that a given cell starts with dirt.
        """
        self.size = size
        self.grid = [
            [0 if random.random() > dirt_prob else 1 for _ in range(size)]
            for _ in range(size)
        ]

        # Defining special cells
        self.grid[0][0] = 0  # starting cell (clean)
        self.grid[size - 1][size - 1] = 2  # charging station
        self.grid[2][2] = -1  # example obstacle

    def show(self):
        """Printing the grid to the console"""
        for row in self.grid:
            print(row)
        print()

    def get_dirty_cells(self):
        """Return list of coordinates of all dirty cells."""
        dirty = []
        for y in range(self.size):
            for x in range(self.size):
                if self.grid[y][x] == 1:
                    dirty.append((x, y))
        return dirty
