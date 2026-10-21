import math


class Node:
    def __init__(self, x, y, parent=None):
        self.x = x
        self.y = y
        self.parent = parent

    def distance_to(self, other):
        dx = self.x - other.x
        dy = self.y - other.y

        sum_squared = dx * dy + dy * dy
        sum_squared = max(0, sum_squared)

        return math.sqrt(sum_squared)

    def __reqr__(self):
        return f"Node({self.x}, {self.y})"
