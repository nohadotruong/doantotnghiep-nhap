from abc import ABC, abstractmethod
from environment.grid_map import GridMap
from typing import List, Optional, Tuple


class BasePlanner(ABC):
    def __init__(self, grid: GridMap) -> None:
        self.grid = grid

    @abstractmethod
    def plan(self) -> Optional[List[Tuple[int, int]]]:
        pass
