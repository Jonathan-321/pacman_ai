import { BaseAgent } from './baseAgent.js';
import { GHOST_SPEED, CELL_SIZE, Direction } from '../config/constants.js';

export class Ghost extends BaseAgent {
    constructor(x, y, color) {
        super(x, y);
        this.color = color;
        this.speed = GHOST_SPEED;
        this.isFrightened = false;
        this.frightenedTimer = 0;
        this.frightenedColor = '#0000FF'; // Blue when frightened
        this.scatterMode = false;
        this.scatterTimer = 0;
        this.homeCorner = null;
        this.stuckCounter = 0;
        this.lastPosition = { x, y };
        this.directionChangeCooldown = 0;
        this.lastValidDirection = null;
    }

    setHomeCorner(corner) {
        this.homeCorner = corner;
    }

    isOppositeDirection(dir1, dir2) {
        return dir1.x === -dir2.x && dir1.y === -dir2.y;
    }

    getValidMoves(maze, excludeReverse = true) {
        let validMoves = Object.values(Direction).filter(dir => {
            if (excludeReverse && this.direction && 
                this.isOppositeDirection(dir, this.direction)) {
                return false;
            }

            const nextX = Math.round(this.x) + dir.x;
            const nextY = Math.round(this.y) + dir.y;
            return maze.isValidPosition(nextX, nextY);
        });

        if (validMoves.length === 0 && excludeReverse) {
            return this.getValidMoves(maze, false);
        }

        return validMoves;
    }

    chooseDirection(maze, pacmanPos) {
        const currentX = Math.round(this.x);
        const currentY = Math.round(this.y);

        // If movement is locked, continue in current direction if possible
        if (this.directionChangeCooldown > 0) {
            this.directionChangeCooldown--;
            if (this.isValidMove(maze, this.direction)) {
                return this.direction;
            }
        }

        // Get valid moves
        const validMoves = this.getValidMoves(maze);
        if (validMoves.length === 0) {
            return this.direction;
        }

        // If frightened, move randomly but smartly
        if (this.isFrightened) {
            const safeMoves = validMoves.filter(move => {
                const nextX = currentX + move.x;
                const nextY = currentY + move.y;
                const distance = Math.abs(nextX - pacmanPos.x) + 
                               Math.abs(nextY - pacmanPos.y);
                return distance > 3;
            });

            this.direction = safeMoves.length > 0 ? 
                safeMoves[Math.floor(Math.random() * safeMoves.length)] :
                validMoves[Math.floor(Math.random() * validMoves.length)];

            this.directionChangeCooldown = 2;
            return this.direction;
        }

        // Choose target based on mode
        const target = this.scatterMode ? this.homeCorner : pacmanPos;

        // Calculate scores for each valid move
        const moveScores = validMoves.map(move => {
            const nextX = currentX + move.x;
            const nextY = currentY + move.y;

            // Base score on distance to target
            let score = -(Math.abs(nextX - target.x) + Math.abs(nextY - target.y));

            // Prefer continuing in same direction
            if (move === this.direction) {
                score += 0.5;
            }

            // Avoid going back and forth
            if (this.lastValidDirection && 
                this.isOppositeDirection(move, this.lastValidDirection)) {
                score -= 1;
            }

            return { move, score };
        });

        // Choose best move
        const bestMove = moveScores.reduce((best, current) => 
            current.score > best.score ? current : best
        );

        this.direction = bestMove.move;
        this.lastValidDirection = this.direction;
        this.directionChangeCooldown = 2;

        return this.direction;
    }

    update(maze, pacmanPos) {
        // Update timers
        if (this.isFrightened) {
            this.frightenedTimer--;
            if (this.frightenedTimer <= 0) {
                this.isFrightened = false;
                this.speed = GHOST_SPEED;
            }
        }

        if (this.scatterMode) {
            this.scatterTimer--;
            if (this.scatterTimer <= 0) {
                this.scatterMode = false;
            }
        }

        // Check if stuck
        const currentPos = this.getPosition();
        if (currentPos.x === this.lastPosition.x && 
            currentPos.y === this.lastPosition.y) {
            this.stuckCounter++;
            if (this.stuckCounter > 5) {
                const validMoves = this.getValidMoves(maze, false);
                if (validMoves.length > 0) {
                    this.direction = validMoves[
                        Math.floor(Math.random() * validMoves.length)
                    ];
                }
                this.stuckCounter = 0;
            }
        } else {
            this.stuckCounter = 0;
        }
        this.lastPosition = { ...currentPos };

        // Choose new direction
        this.direction = this.chooseDirection(maze, pacmanPos);

        // Update position
        const nextX = this.x + this.direction.x * this.speed;
        const nextY = this.y + this.direction.y * this.speed;

        if (maze.isValidPosition(Math.round(nextX), Math.round(nextY))) {
            this.x = nextX;
            this.y = nextY;
        }
    }

    makeFrightened() {
        this.isFrightened = true;
        this.frightenedTimer = 600; // 10 seconds
        this.speed = GHOST_SPEED * 0.5; // Slower when frightened
    }

    enterScatterMode() {
        this.scatterMode = true;
        this.scatterTimer = 420; // 7 seconds
    }

    draw(ctx, offset = 0) {
        const centerX = Math.round(this.x * CELL_SIZE + CELL_SIZE / 2);
        const centerY = Math.round(this.y * CELL_SIZE + CELL_SIZE / 2) + offset;
        const radius = Math.round(CELL_SIZE * 0.8 / 2);

        const color = this.isFrightened ? this.frightenedColor : this.color;

        // Draw ghost body
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, Math.PI, 0, false);
        
        // Draw ghost skirt
        ctx.lineTo(centerX + radius, centerY + radius);
        for (let i = 0; i < 3; i++) {
            const wave = radius / 1.5;
            ctx.quadraticCurveTo(
                centerX + radius - (wave * i),
                centerY + wave / 2,
                centerX + radius - (wave * (i + 0.5)),
                centerY + radius
            );
            ctx.quadraticCurveTo(
                centerX + radius - (wave * (i + 1)),
                centerY + wave * 1.5,
                centerX + radius - (wave * (i + 1)),
                centerY + radius
            );
        }
        ctx.lineTo(centerX - radius, centerY);
        ctx.fill();

        // Draw eyes
        if (!this.isFrightened) {
            // White part of eyes
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(centerX - radius/3, centerY - radius/4, radius/4, 0, Math.PI * 2);
            ctx.arc(centerX + radius/3, centerY - radius/4, radius/4, 0, Math.PI * 2);
            ctx.fill();

            // Pupils
            ctx.fillStyle = 'black';
            ctx.beginPath();
            ctx.arc(centerX - radius/3, centerY - radius/4, radius/8, 0, Math.PI * 2);
            ctx.arc(centerX + radius/3, centerY - radius/4, radius/8, 0, Math.PI * 2);
            ctx.fill();
        } else {
            // Frightened eyes
            ctx.fillStyle = 'white';
            ctx.beginPath();
            ctx.arc(centerX - radius/3, centerY - radius/4, radius/6, 0, Math.PI * 2);
            ctx.arc(centerX + radius/3, centerY - radius/4, radius/6, 0, Math.PI * 2);
            ctx.fill();
        }
    }
}