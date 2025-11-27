"""
battery.py
-----------
Battery management system for the vacuum cleaner.
Handles power consumption, charging, and battery-aware decision making.
"""


class Battery:
    def __init__(self, capacity=100, drain_rate=1, charge_rate=5):
        """
        Initializing battery system.

        Args:
            capacity (int): Maximum battery capacity
            drain_rate (int): Power consumed per move
            charge_rate (int): Power gained per charge step
        """
        self.capacity = capacity
        self.current = capacity
        self.drain_rate = drain_rate
        self.charge_rate = charge_rate
        self.total_consumed = 0
        self.charge_cycles = 0

    def consume(self, amount=None):
        """Consume battery power for an action."""
        if amount is None:
            amount = self.drain_rate
        self.current = max(0, self.current - amount)
        self.total_consumed += amount
        return self.current > 0

    def charge(self):
        """Charge the battery at charging station."""
        old_level = self.current
        self.current = min(self.capacity, self.current + self.charge_rate)

        if old_level < self.capacity and self.current == self.capacity:
            self.charge_cycles += 1

    def needs_charging(self, threshold=20):
        """Check if battery needs charging."""
        return self.current <= threshold

    def is_empty(self):
        """Check if battery is depleted."""
        return self.current <= 0

    def get_percentage(self):
        """Get battery percentage."""
        return (self.current / self.capacity) * 100

    def __str__(self):
        return f"Battery: {self.current}/{self.capacity} ({self.get_percentage():.1f}%)"
