class PacmanGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.loadingScreen = document.getElementById('loadingScreen');
        this.loadingStatus = document.getElementById('loadingStatus');
        
        // Set canvas size
        this.canvas.width = 600;
        this.canvas.height = 400;
        
        // Game state
        this.gameState = {
            score: 0,
            mode: 'AI',
            status: 'Running'
        };

        // Game elements
        this.pacman = {
            x: 300,
            y: 200,
            radius: 15,
            mouthOpen: 0
        };

        this.init();
    }

    async init() {
        try {
            this.setupGame();
            this.startGameLoop();
            this.hideLoadingScreen();
        } catch (error) {
            console.error('Error initializing game:', error);
            this.showError('Failed to initialize game: ' + error.message);
        }
    }

    setupGame() {
        // Set initial canvas state
        this.ctx.fillStyle = 'black';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Setup event listeners
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
        
        // Set up game controls
        document.getElementById('toggleAI').addEventListener('click', () => this.toggleAI());
        document.getElementById('toggleSound').addEventListener('click', () => this.toggleSound());
        document.getElementById('restartGame').addEventListener('click', () => this.restartGame());
    }

    startGameLoop() {
        const loop = () => {
            this.update();
            this.draw();
            requestAnimationFrame(loop);
        };
        requestAnimationFrame(loop);
    }

    update() {
        // Update Pacman mouth animation
        this.pacman.mouthOpen = (this.pacman.mouthOpen + 0.1) % Math.PI;
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = 'black';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw game border
        this.ctx.strokeStyle = 'blue';
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw Pacman
        this.ctx.beginPath();
        this.ctx.fillStyle = 'yellow';
        this.ctx.arc(
            this.pacman.x,
            this.pacman.y,
            this.pacman.radius,
            this.pacman.mouthOpen,
            2 * Math.PI - this.pacman.mouthOpen
        );
        this.ctx.lineTo(this.pacman.x, this.pacman.y);
        this.ctx.fill();
        this.ctx.closePath();
    }

    handleKeyPress(event) {
        const speed = 5;
        switch(event.key) {
            case 'ArrowUp':
                this.pacman.y -= speed;
                break;
            case 'ArrowDown':
                this.pacman.y += speed;
                break;
            case 'ArrowLeft':
                this.pacman.x -= speed;
                break;
            case 'ArrowRight':
                this.pacman.x += speed;
                break;
            case 't':
                this.toggleAI();
                break;
            case 'm':
                this.toggleSound();
                break;
        }
    }

    toggleAI() {
        this.gameState.mode = this.gameState.mode === 'AI' ? 'Manual' : 'AI';
        document.getElementById('gameMode').textContent = this.gameState.mode;
    }

    toggleSound() {
        // Implement sound toggle
        console.log('Sound toggled');
    }

    restartGame() {
        // Reset game state
        this.pacman.x = 300;
        this.pacman.y = 200;
        this.gameState.score = 0;
        document.getElementById('score').textContent = '0';
    }

    hideLoadingScreen() {
        if (this.loadingScreen) {
            this.loadingScreen.style.display = 'none';
        }
    }

    showError(message) {
        if (this.loadingScreen) {
            this.loadingScreen.innerHTML = `
                <h2>Error</h2>
                <p>${message}</p>
                <button onclick="location.reload()">Retry</button>
            `;
        }
    }
}

// Initialize game when document is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.game = new PacmanGame();
});