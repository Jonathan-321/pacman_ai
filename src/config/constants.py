from enum import Enum

# Game dimensions
CELL_SIZE = 30
MAZE_WIDTH = 20
MAZE_HEIGHT = 16
SCOREBOARD_HEIGHT = 60  # Height of the scoreboard area
SCREEN_WIDTH = MAZE_WIDTH * CELL_SIZE
SCREEN_HEIGHT = MAZE_HEIGHT * CELL_SIZE + SCOREBOARD_HEIGHT

# Game settings
PACMAN_SPEED = 0.20
GHOST_SPEED = 0.08
FPS = 60

class CellType(Enum):
    WALL = 0
    PATH = 1
    PELLET = 2
    POWER_PELLET = 3
    EMPTY = 4

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)