from typing import List, Tuple
from ..config.constants import CellType
from ..config.maze_layouts import MazeSymbols

class Maze:
    def __init__(self, width: int, height: int):
        print(f"Initializing maze with dimensions: {width}x{height}")
        self.width = width
        self.height = height
        self.grid = self._create_empty_maze()
        self.pacman_start = (1, 1)  # Default start position
        self.ghost_starts = []
        
    def _create_empty_maze(self) -> List[List[CellType]]:
        return [[CellType.EMPTY for _ in range(self.width)] 
                for _ in range(self.height)]
    
    def load_layout(self, layout: List[str]):
        """Load maze from a text-based layout"""
        print(f"Loading layout with dimensions: {len(layout[0])}x{len(layout)}")
        self.height = len(layout)
        self.width = len(layout[0])
        self.grid = []
        
        for y, row in enumerate(layout):
            grid_row = []
            for x, cell in enumerate(row):
                if cell == MazeSymbols.WALL:
                    grid_row.append(CellType.WALL)
                elif cell == MazeSymbols.PELLET:
                    grid_row.append(CellType.PELLET)
                elif cell == MazeSymbols.POWER_PELLET:
                    grid_row.append(CellType.POWER_PELLET)
                elif cell == MazeSymbols.PACMAN_START:
                    self.pacman_start = (x, y)
                    grid_row.append(CellType.PATH)
                elif cell == MazeSymbols.GHOST_START:
                    self.ghost_starts.append((x, y))
                    grid_row.append(CellType.PATH)
                else:
                    grid_row.append(CellType.PATH)
            self.grid.append(grid_row)
            
        print(f"Final grid dimensions: {len(self.grid)}x{len(self.grid[0])}")

    def get_cell_type(self, x: int, y: int) -> CellType:
        """Get the type of cell at the given position"""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        return CellType.WALL

    def set_cell_type(self, x: int, y: int, cell_type: CellType):
        """Set the type of cell at the given position"""
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y][x] = cell_type

    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is valid and not a wall"""
        return (0 <= x < self.width and 
                0 <= y < self.height and 
                self.grid[y][x] != CellType.WALL)
    
    def eat_pellet(self, x: int, y: int) -> bool:
        """Eat a pellet at the given position and return True if it was a power pellet"""
        if 0 <= x < self.width and 0 <= y < self.height:
            cell_type = self.grid[y][x]
            if cell_type in [CellType.PELLET, CellType.POWER_PELLET]:
                is_power_pellet = cell_type == CellType.POWER_PELLET
                self.grid[y][x] = CellType.PATH
                return is_power_pellet
        return False
    
    def count_remaining_pellets(self) -> int:
        """Count the number of remaining pellets in the maze"""
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] in [CellType.PELLET, CellType.POWER_PELLET]:
                    count += 1
        return count