import { CellType } from '../config/constants.js';
import { MazeSymbols } from '../config/mazelayouts.js';

export class Maze {
    constructor(width, height) {
        console.log(`Initializing maze with dimensions: ${width}x${height}`);
        this.width = width;
        this.height = height;
        this.grid = this._createEmptyMaze();
        this.pacmanStart = { x: 1, y: 1 };
        this.ghostStarts = [];
    }

    _createEmptyMaze() {
        return Array(this.height).fill()
            .map(() => Array(this.width).fill(CellType.EMPTY));
    }

    loadLayout(layout) {
        console.log(`Loading layout with dimensions: ${layout[0].length}x${layout.length}`);
        this.height = layout.length;
        this.width = layout[0].length;
        this.grid = [];
        
        for (let y = 0; y < layout.length; y++) {
            const gridRow = [];
            for (let x = 0; x < layout[y].length; x++) {
                const cell = layout[y][x];
                switch (cell) {
                    case MazeSymbols.WALL:
                        gridRow.push(CellType.WALL);
                        break;
                    case MazeSymbols.PELLET:
                        gridRow.push(CellType.PELLET);
                        break;
                    case MazeSymbols.POWER_PELLET:
                        gridRow.push(CellType.POWER_PELLET);
                        break;
                    case MazeSymbols.PACMAN_START:
                        this.pacmanStart = { x, y };
                        gridRow.push(CellType.PATH);
                        break;
                    case MazeSymbols.GHOST_START:
                        this.ghostStarts.push({ x, y });
                        gridRow.push(CellType.PATH);
                        break;
                    default:
                        gridRow.push(CellType.PATH);
                }
            }
            this.grid.push(gridRow);
        }
        
        console.log(`Final grid dimensions: ${this.grid.length}x${this.grid[0].length}`);
    }

    getCellType(x, y) {
        if (y >= 0 && y < this.height && x >= 0 && x < this.width) {
            return this.grid[y][x];
        }
        return CellType.WALL;
    }

    setCellType(x, y, cellType) {
        if (y >= 0 && y < this.height && x >= 0 && x < this.width) {
            this.grid[y][x] = cellType;
        }
    }

    isValidPosition(x, y) {
        return (x >= 0 && x < this.width && 
                y >= 0 && y < this.height && 
                this.grid[y][x] !== CellType.WALL);
    }

    eatPellet(x, y) {
        if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
            const cellType = this.grid[y][x];
            if (cellType === CellType.PELLET || cellType === CellType.POWER_PELLET) {
                const isPowerPellet = cellType === CellType.POWER_PELLET;
                this.grid[y][x] = CellType.PATH;
                return isPowerPellet;
            }
        }
        return false;
    }

    countRemainingPellets() {
        let count = 0;
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                if (this.grid[y][x] === CellType.PELLET || 
                    this.grid[y][x] === CellType.POWER_PELLET) {
                    count++;
                }
            }
        }
        return count;
    }
    
    draw(ctx, offset = 0) {
        const cellSize = 30; // You might want to move this to constants
        
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                const cellType = this.grid[y][x];
                const pixelX = x * cellSize;
                const pixelY = y * cellSize + offset;
                
                switch (cellType) {
                    case CellType.WALL:
                        ctx.fillStyle = 'blue';
                        ctx.fillRect(pixelX, pixelY, cellSize, cellSize);
                        break;
                    case CellType.PELLET:
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(
                            pixelX + cellSize/2,
                            pixelY + cellSize/2,
                            2,
                            0,
                            Math.PI * 2
                        );
                        ctx.fill();
                        break;
                    case CellType.POWER_PELLET:
                        ctx.fillStyle = 'white';
                        ctx.beginPath();
                        ctx.arc(
                            pixelX + cellSize/2,
                            pixelY + cellSize/2,
                            6,
                            0,
                            Math.PI * 2
                        );
                        ctx.fill();
                        break;
                }
            }
        }
    }
}