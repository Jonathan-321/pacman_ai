from abc import ABC, abstractmethod
from typing import Tuple, List
from ..config.constants import Direction, CellType

class BaseAgent(ABC):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction = Direction.RIGHT

    def get_position(self) -> Tuple[int, int]:
        return (int(round(self.x)), int(round(self.y)))