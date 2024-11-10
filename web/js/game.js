import { Maze } from './web/core/maze.js';
import { Pacman } from './web/agents/pacman.js';
import { Ghost } from './web/agents/ghost.js';
import { 
    CELL_SIZE, 
    SCREEN_WIDTH, 
    SCREEN_HEIGHT, 
    SCOREBOARD_HEIGHT,
    FPS,
    MAZE_WIDTH,
    MAZE_HEIGHT,
    GAME_CONFIG
} from './config/constants.js';
import { LEVEL_1 } from './config/mazelayouts.js';

export class PacmanGame {
    constructor() {
        console.log('Initializing PacmanGame...');
        this.validateDOMElements();
        this.setupCanvas();
        this.setupGameState();
        this.setupEventListeners();
        this.init();
    }

    validateDOMElements() {
        const requiredElements = [
            'gameCanvas',
            'loadingScreen',
            'score',
            'gameMode',
            'gameStatus'
        ];

        const missingElements = requiredElements.filter(id => !document.getElementById(id));
        if (missingElements.length > 0) {
            throw new Error(`Missing required elements: ${missingElements.join(', ')}`);
        }
    }

    setupCanvas() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        
        this.canvas.width = SCREEN_WIDTH;
        this.canvas.height = SCREEN_HEIGHT;
        
        this.ctx.imageSmoothingEnabled = false;
    }

    setupGameState() {
        this.gameState = {
            score: 0,
            mode: 'AI',
            status: 'Loading',
            highScore: parseInt(localStorage.getItem('pacmanHighScore')) || 0,
            level: 1,
            lives: 3,
            paused: false
        };

        this.debug = {
            enabled: false,
            showPath: true,
            showGrid: false
        };

        this.lastFrameTime = 0;
        this.deltaTime = 0;
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        const buttons = {
            'toggleAI': () => this.toggleAI(),
            'toggleDebug': () => this.toggleDebug(),
            'restartGame': () => this.restartGame(),
            'pauseGame': () => this.togglePause()
        };

        Object.entries(buttons).forEach(([id, handler]) => {
            const button = document.getElementById(id);
            if (button) {
                button.addEventListener('click', handler.bind(this));
            }
        });
    }

    async init() {
        try {
            console.log('Starting initialization...');
            this.showLoadingScreen();
            await this.initializeGame();
            this.hideLoadingScreen();
            this.startGameLoop();
            console.log('Initialization complete!');
        } catch (error) {
            console.error('Initialization failed:', error);
            this.showError(error.message);
        }
    }

    async initializeGame() {
        // Initialize maze
        this.maze = new Maze(MAZE_WIDTH, MAZE_HEIGHT);
        await this.maze.loadLayout(LEVEL_1);

        // Initialize Pacman
        const pacmanStart = this.maze.pacmanStart;
        this.pacman = new Pacman(pacmanStart.x, pacmanStart.y);

        // Initialize ghosts
        const ghostColors = ['#FF0000', '#FFB6FF', '#00FFFF', '#FFB851'];
        const ghostCorners = [
            { x: MAZE_WIDTH - 1, y: 0 },
            { x: 0, y: 0 },
            { x: MAZE_WIDTH - 1, y: MAZE_HEIGHT - 1 },
            { x: 0, y: MAZE_HEIGHT - 1 }
        ];

        this.ghosts = this.maze.ghostStarts.map((start, index) => {
            const ghost = new Ghost(start.x, start.y, ghostColors[index]);
            ghost.setHomeCorner(ghostCorners[index]);
            return ghost;
        });

        this.gameState.status = 'Running';
    }

    startGameLoop() {
        const gameLoop = (timestamp) => {
            if (this.lastFrameTime === 0) {
                this.lastFrameTime = timestamp;
            }

            this.deltaTime = (timestamp - this.lastFrameTime) / 1000;
            this.lastFrameTime = timestamp;

            if (!this.gameState.paused && this.gameState.status === 'Running') {
                this.update();
                this.draw();
            }

            requestAnimationFrame(gameLoop);
        };

        requestAnimationFrame(gameLoop);
    }

    update() {
        // Get ghost positions for Pacman AI
        const ghostPositions = this.ghosts.map(ghost => ({
            x: Math.round(ghost.x),
            y: Math.round(ghost.y)
        }));

        // Update Pacman
        this.pacman.update(this.maze, ghostPositions);

        // Update ghosts
        const pacmanPos = {
            x: Math.round(this.pacman.x),
            y: Math.round(this.pacman.y)
        };

        this.ghosts.forEach(ghost => {
            ghost.update(this.maze, pacmanPos);

            if (this.checkCollision(ghost, this.pacman)) {
                if (this.pacman.isPoweredUp) {
                    this.eatGhost(ghost);
                } else {
                    this.handlePacmanDeath();
                }
            }
        });

        // Update score
        this.gameState.score = this.pacman.score;
        this.updateUI();

        // Check win condition
        if (this.maze.countRemainingPellets() === 0) {
            this.handleLevelComplete();
        }
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#000000';
        this.ctx.fillRect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT);

        // Draw game elements
        this.maze.draw(this.ctx, SCOREBOARD_HEIGHT);
        this.ghosts.forEach(ghost => ghost.draw(this.ctx, SCOREBOARD_HEIGHT));
        this.pacman.draw(this.ctx, SCOREBOARD_HEIGHT);

        // Draw HUD
        this.drawHUD();

        // Draw debug info if enabled
        if (this.debug.enabled) {
            this.drawDebugInfo();
        }
    }

    drawHUD() {
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '20px Arial';
        
        // Draw score
        this.ctx.fillText(`Score: ${this.gameState.score}`, 10, 30);
        this.ctx.fillText(`High Score: ${this.gameState.highScore}`, SCREEN_WIDTH / 2 - 60, 30);
        this.ctx.fillText(`Lives: ${this.gameState.lives}`, SCREEN_WIDTH - 100, 30);
    }

    drawDebugInfo() {
        if (!this.debug.enabled) return;

        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
        this.ctx.font = '12px Arial';

        // Draw FPS
        const fps = Math.round(1 / this.deltaTime);
        this.ctx.fillText(`FPS: ${fps}`, 10, SCREEN_HEIGHT - 10);

        // Draw grid if enabled
        if (this.debug.showGrid) {
            this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
            for (let x = 0; x < MAZE_WIDTH; x++) {
                for (let y = 0; y < MAZE_HEIGHT; y++) {
                    this.ctx.strokeRect(
                        x * CELL_SIZE,
                        y * CELL_SIZE + SCOREBOARD_HEIGHT,
                        CELL_SIZE,
                        CELL_SIZE
                    );
                }
            }
        }
    }

    checkCollision(entity1, entity2) {
        const dx = entity1.x - entity2.x;
        const dy = entity1.y - entity2.y;
        return Math.sqrt(dx * dx + dy * dy) < 0.7;
    }

    handlePacmanDeath() {
        this.gameState.lives--;
        if (this.gameState.lives <= 0) {
            this.gameOver();
        } else {
            this.resetPositions();
        }
    }

    handleLevelComplete() {
        this.gameState.level++;
        this.resetLevel();
    }

    gameOver() {
        this.gameState.status = 'Game Over';
        if (this.gameState.score > this.gameState.highScore) {
            this.gameState.highScore = this.gameState.score;
            localStorage.setItem('pacmanHighScore', this.gameState.highScore);
        }
        this.updateUI();
    }

    resetPositions() {
        const pacmanStart = this.maze.pacmanStart;
        this.pacman.x = pacmanStart.x;
        this.pacman.y = pacmanStart.y;

        this.ghosts.forEach((ghost, index) => {
            const start = this.maze.ghostStarts[index];
            ghost.x = start.x;
            ghost.y = start.y;
        });
    }

    resetLevel() {
        this.resetPositions();
        this.pacman.reset();
        this.ghosts.forEach(ghost => ghost.reset());
        this.maze.loadLayout(LEVEL_1);  // Could load different levels based on gameState.level
    }

    eatGhost(ghost) {
        ghost.reset();
        this.pacman.score += GAME_CONFIG.SCORE.GHOST;
        this.updateUI();
    }

    handleKeyPress(event) {
        if (this.gameState.status !== 'Running') {
            if (event.code === 'Space') {
                this.restartGame();
            }
            return;
        }

        switch (event.code) {
            case 'ArrowUp':
            case 'ArrowDown':
            case 'ArrowLeft':
            case 'ArrowRight':
                if (!this.pacman.autonomousMode) {
                    this.pacman.handleInput(event.key);
                }
                break;
            case 'KeyT':
                this.toggleAI();
                break;
            case 'KeyD':
                this.toggleDebug();
                break;
            case 'Space':
                this.togglePause();
                break;
        }
    }

    toggleAI() {
        this.pacman.toggleControlMode();
        this.gameState.mode = this.pacman.autonomousMode ? 'AI' : 'Manual';
        this.updateUI();
    }

    toggleDebug() {
        this.debug.enabled = !this.debug.enabled;
        console.log('Debug mode:', this.debug.enabled ? 'ON' : 'OFF');
    }

    togglePause() {
        this.gameState.paused = !this.gameState.paused;
        this.gameState.status = this.gameState.paused ? 'Paused' : 'Running';
        this.updateUI();
    }

    restartGame() {
        this.gameState = {
            score: 0,
            mode: 'AI',
            status: 'Running',
            highScore: this.gameState.highScore,
            level: 1,
            lives: 3,
            paused: false
        };

        this.resetLevel();
        this.updateUI();
    }

    updateUI() {
        const elements = {
            'score': this.gameState.score,
            'gameMode': this.gameState.mode,
            'gameStatus': this.gameState.status
        };

        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    showLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.style.display = 'flex';
        }
    }

    hideLoadingScreen() {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.style.display = 'none';
        }
    }

    showError(message) {
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.innerHTML = `
                <div class="error-content">
                    <h2>Error</h2>
                    <p>${message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
            loadingScreen.style.display = 'flex';
        }
    }
}

// Initialize game when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    try {
        window.game = new PacmanGame();
    } catch (error) {
        console.error('Failed to create game:', error);
        const loadingScreen = document.getElementById('loadingScreen');
        if (loadingScreen) {
            loadingScreen.innerHTML = `
                <div class="error-content">
                    <h2>Error</h2>
                    <p>Failed to initialize game: ${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }
});