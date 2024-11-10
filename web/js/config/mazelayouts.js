// mazelayouts.js
export const MazeSymbols = {
    WALL: 'W',
    PATH: 'P',
    PELLET: '.',
    POWER_PELLET: 'o',
    PACMAN_START: 'S',
    GHOST_START: 'G',
    EMPTY: ' '
};

export const LEVEL_1 = [
   "WWWWWWWWWWWWWWWWWWWW",  // Row 0  (20 chars)
    "W........W..........",  // Row 1  (20 chars)
    "W.WW.WWW.W.WWW.WW.W.",  //Row 2  (20 chars)
    "WoW....GG........oW.",  // Row 3  (20 chars)
    "W.W.WW.WWWW.WW.W.W..",  //Row 4  (20 chars)
    "W.....W....W.....W..",  // Row 5  (20 chars)
    "W.WWW.WWWW.WWW.W.W..",  // Row 6  (20 chars)
    "W.WWW.W....WWW.W.W..",  // Row 7  (20 chars)
    "W.....W..........W..",  // Row 8  (20 chars)
    "W.WWW.WSSSW.WWW.W...", // Row 9  (20 chars)
    "W.....W....W.....W..",  // Row 10 (20 chars)
    "W.W.WW.WWWW.WW.W.W..",  // Row 11 (20 chars)
    "WoW....GG.....W..oW.",  // Row 12 (20 chars)
    "W.WW.WWW.W.WWW.WW.W.",  
    "W........W..........",  
    "WWWWWWWWWWWWWWWWWWW."   
];

class MazeValidator {
    static validateDimensions(layout) {
        if (!layout || layout.length === 0) {
            throw new Error("Empty maze layout");
        }

        const width = layout[0].length;
        const height = layout.length;

        // Check if all rows have the same width
        layout.forEach((row, i) => {
            if (row.length !== width) {
                throw new Error(`Row ${i} has inconsistent width: ${row.length} (expected ${width})`);
            }
        });

        console.log(`Maze dimensions: ${width}x${height}`);
    }

    static validateSymbols(layout) {
        const validSymbols = new Set(Object.values(MazeSymbols));
        
        layout.forEach((row, y) => {
            [...row].forEach((symbol, x) => {
                if (!validSymbols.has(symbol)) {
                    throw new Error(`Invalid symbol '${symbol}' at position (${x}, ${y})`);
                }
            });
        });
    }

    static validateBoundaries(layout) {
        // Check top row
        if (![...layout[0]].every(cell => cell === MazeSymbols.WALL)) {
            throw new Error('Maze must be enclosed by walls on top');
        }

        // Check bottom row
        if (![...layout[layout.length - 1]].every(cell => cell === MazeSymbols.WALL)) {
            throw new Error('Maze must be enclosed by walls on bottom');
        }

        // Check side walls
        for (let y = 0; y < layout.length; y++) {
            if (layout[y][0] !== MazeSymbols.WALL || 
                layout[y][layout[y].length - 1] !== MazeSymbols.WALL) {
                throw new Error(`Row ${y} must be enclosed by walls on sides`);
            }
        }
    }

    static validateRequiredElements(layout) {
        let hasPacman = false;
        let ghostCount = 0;
        let pelletCount = 0;

        layout.forEach(row => {
            [...row].forEach(symbol => {
                if (symbol === MazeSymbols.PACMAN_START) hasPacman = true;
                if (symbol === MazeSymbols.GHOST_START) ghostCount++;
                if (symbol === MazeSymbols.PELLET || symbol === MazeSymbols.POWER_PELLET) pelletCount++;
            });
        });

        if (!hasPacman) throw new Error('Maze must have a Pacman start position');
        if (ghostCount === 0) throw new Error('Maze must have at least one ghost start position');
        if (pelletCount === 0) throw new Error('Maze must have at least one pellet');

        console.log(`Found: Pacman: ${hasPacman}, Ghosts: ${ghostCount}, Pellets: ${pelletCount}`);
    }

    static validate(layout) {
        console.log('Starting maze validation...');
        
        try {
            this.validateDimensions(layout);
            this.validateSymbols(layout);
            this.validateBoundaries(layout);
            this.validateRequiredElements(layout);
            
            console.log('Maze validation successful!');
            return true;
        } catch (error) {
            console.error('Maze validation failed:', error.message);
            throw error;
        }
    }
}

// Validate maze layout when module is loaded
try {
    MazeValidator.validate(LEVEL_1);
} catch (error) {
    console.error('Error in maze layout:', error.message);
    throw error;
}

export { MazeValidator };