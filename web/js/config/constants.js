// Game dimensions
export const CELL_SIZE = 30;
export const MAZE_WIDTH = 20;
export const MAZE_HEIGHT = 16;
export const SCOREBOARD_HEIGHT = 60;
export const SCREEN_WIDTH = MAZE_WIDTH * CELL_SIZE;
export const SCREEN_HEIGHT = MAZE_HEIGHT * CELL_SIZE + SCOREBOARD_HEIGHT;

// Game settings
export const PACMAN_SPEED = 0.20;
export const GHOST_SPEED = 0.08;
export const FPS = 60;

// Cell Types
export const CellType = {
    WALL: 0,
    PATH: 1,
    PELLET: 2,
    POWER_PELLET: 3,
    EMPTY: 4
};

// Directions with vectors
export const Direction = {
    UP: { x: 0, y: -1 },
    DOWN: { x: 0, y: 1 },
    LEFT: { x: -1, y: 0 },
    RIGHT: { x: 1, y: 0 }
};

// Game settings object (for organization)
export const GAME_CONFIG = {
    CELL: {
        SIZE: CELL_SIZE,
        TYPE: CellType
    },
    MAZE: {
        WIDTH: MAZE_WIDTH,
        HEIGHT: MAZE_HEIGHT
    },
    SCREEN: {
        WIDTH: SCREEN_WIDTH,
        HEIGHT: SCREEN_HEIGHT,
        SCOREBOARD_HEIGHT: SCOREBOARD_HEIGHT
    },
    SPEED: {
        PACMAN: PACMAN_SPEED,
        GHOST: GHOST_SPEED,
        FPS: FPS
    },
    DIRECTION: Direction,
    SCORE: {
        PELLET: 10,
        POWER_PELLET: 50,
        GHOST: 200
    }
};

// Export all constants as a group as well
export default {
    CELL_SIZE,
    MAZE_WIDTH,
    MAZE_HEIGHT,
    SCOREBOARD_HEIGHT,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PACMAN_SPEED,
    GHOST_SPEED,
    FPS,
    CellType,
    Direction,
    GAME_CONFIG
};