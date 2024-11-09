# src/config/maze_layouts.py

# Column numbers for reference
# 01234567890123456789
LEVEL_1 = [
    "WWWWWWWWWWWWWWWWWWWW",  # Row 0  (20 chars)
    "W........W..........",  # Row 1  (20 chars)
    "W.WW.WWW.W.WWW.WW.W.",  # Row 2  (20 chars)
    "WoW....GG........oW.",  # Row 3  (20 chars)
    "W.W.WW.WWWW.WW.W.W..",  # Row 4  (20 chars)
    "W.....W....W.....W..",  # Row 5  (20 chars)
    "W.WWW.WWWW.WWW.W.W..",  # Row 6  (20 chars)
    "W.WWW.W....WWW.W.W..",  # Row 7  (20 chars)
    "W.....W..........W..",  # Row 8  (20 chars)
    "W.WWW.WSSSW.WWW.W...",  # Row 9  (20 chars)
    "W.....W....W.....W..",  # Row 10 (20 chars)
    "W.W.WW.WWWW.WW.W.W..",  # Row 11 (20 chars)
    "WoW....GG.....W..oW.",  # Row 12 (20 chars)
    "W.WW.WWW.W.WWW.WW.W.",  # Row 13 (20 chars)
    "W........W..........",  # Row 14 (20 chars)
    "WWWWWWWWWWWWWWWWWWW."   # Row 15 (20 chars)
]

class MazeSymbols:
    WALL = 'W'
    PATH = 'P'
    PELLET = '.'
    POWER_PELLET = 'o'
    PACMAN_START = 'S'
    GHOST_START = 'G'
    EMPTY = ' '

def verify_maze_layout(layout):
    """Verify that the maze layout is consistent"""
    if not layout:
        raise ValueError("Empty maze layout")
    
    width = len(layout[0])
    print(f"Expected width: {width}")
    
    for i, row in enumerate(layout):
        current_width = len(row)
        print(f"Row {i}: length = {current_width}, content = '{row}'")
        if current_width != width:
            raise ValueError(f"Inconsistent row length at row {i}: expected {width}, got {current_width}")
    
    print(f"Maze layout verified: {width}x{len(layout)}")

# Verify the layout when this module is imported
verify_maze_layout(LEVEL_1)