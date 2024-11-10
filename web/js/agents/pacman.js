import { BaseAgent } from './baseAgent.js';
import { PACMAN_SPEED, CELL_SIZE, Direction, CellType } from '../config/constants.js';
import { AStarSearch } from '../core/pathfinding.js';

export class Pacman extends BaseAgent {
    constructor(x, y) {
        super(x, y);
        this.score = 0;
        this.isPoweredUp = false;
        this.powerTimer = 0;
        this.mouthAngle = 0;
        this.mouthSpeed = 5;
        this.openingMouth = true;
        this.speed = PACMAN_SPEED;
        
        // AI components
        this.currentPath = [];
        this.searchAlgorithm = new AStarSearch();
        this.autonomousMode = true;
        this.dangerThreshold = 3;
        this.pathUpdateCooldown = 0;
        this.stuckDetectionThreshold = 10;
        this.lastPosition = { x, y };
        this.noMovementCounter = 0;
        this.color = '#FFFF00';
        this.direction = Direction.RIGHT; // Default direction
    }

    reset() {
        this.resetSpeed();
        this.currentPath = [];
        this.pathUpdateCooldown = 0;
        this.noMovementCounter = 0;
        this.lastPosition = { x: this.x, y: this.y };
        this.isPoweredUp = false;
        this.powerTimer = 0;
        this.direction = Direction.RIGHT;
        this.score = 0;
    }

    handleInput(key) {
        if (!this.autonomousMode) {
            const directionMap = {
                'ArrowUp': Direction.UP,
                'ArrowDown': Direction.DOWN,
                'ArrowLeft': Direction.LEFT,
                'ArrowRight': Direction.RIGHT
            };
            
            if (directionMap[key]) {
                const nextX = Math.round(this.x) + directionMap[key].x;
                const nextY = Math.round(this.y) + directionMap[key].y;
                if (this.maze && this.maze.isValidPosition(nextX, nextY)) {
                    this.direction = directionMap[key];
                }
            }
        }
    }

    isStuck() {
        const currentPos = { x: Math.round(this.x), y: Math.round(this.y) };
        
        if (Math.abs(currentPos.x - this.lastPosition.x) < 0.1 && 
            Math.abs(currentPos.y - this.lastPosition.y) < 0.1) {
            this.noMovementCounter++;
        } else {
            this.noMovementCounter = 0;
        }

        this.lastPosition = { ...currentPos };
        return this.noMovementCounter > this.stuckDetectionThreshold;
    }

    calculateGhostDanger(pos, ghostPositions) {
        if (!ghostPositions.length) return Infinity;
        
        return Math.min(...ghostPositions.map(ghost => 
            Math.abs(pos.x - ghost.x) + Math.abs(pos.y - ghost.y)
        ));
    }

    findBestPellet(pellets, ghostPositions, maze) {
        if (!pellets.length) return null;

        return pellets.reduce((best, pellet) => {
            const ghostDanger = this.calculateGhostDanger(pellet, ghostPositions);
            const distanceToMe = Math.abs(pellet.x - this.x) + Math.abs(pellet.y - this.y);
            const escapeRoutes = this.countEscapeRoutes(pellet.x, pellet.y, maze);
            const isPowerPellet = maze.getCellType(pellet.x, pellet.y) === CellType.POWER_PELLET;
            
            const score = (ghostDanger * 2) - (distanceToMe * 0.5) + 
                         (escapeRoutes * 0.3) + (isPowerPellet ? 10 : 0);
            
            if (!best || score > best.score) {
                return { pellet, score };
            }
            return best;
        }, null).pellet;
    }

    getPelletPositions(maze) {
        const pellets = [];
        for (let y = 0; y < maze.height; y++) {
            for (let x = 0; x < maze.width; x++) {
                const cellType = maze.getCellType(x, y);
                if (cellType === CellType.PELLET || cellType === CellType.POWER_PELLET) {
                    pellets.push({ x, y });
                }
            }
        }
        return pellets;
    }

    findEscapeDirection(currentPos, ghostPositions, maze) {
        let bestDirection = this.direction;
        let maxSafety = -Infinity;

        for (const direction of Object.values(Direction)) {
            const nextX = currentPos.x + direction.x;
            const nextY = currentPos.y + direction.y;

            if (!maze.isValidPosition(nextX, nextY)) continue;

            const ghostDistance = this.calculateGhostDanger(
                { x: nextX, y: nextY }, 
                ghostPositions
            );
            const escapeRoutes = this.countEscapeRoutes(nextX, nextY, maze);
            const hasPowerPellet = maze.getCellType(nextX, nextY) === CellType.POWER_PELLET;

            const safetyScore = (ghostDistance * 2.5) + 
                              (escapeRoutes * 1.5) + 
                              (hasPowerPellet ? 8 : 0) +
                              (this.isOppositeDirection(direction) ? -2 : 0);

            if (safetyScore > maxSafety) {
                maxSafety = safetyScore;
                bestDirection = direction;
            }
        }

        return bestDirection;
    }

    isOppositeDirection(newDir) {
        return newDir.x === -this.direction.x && newDir.y === -this.direction.y;
    }

    countEscapeRoutes(x, y, maze) {
        return Object.values(Direction).filter(dir => 
            maze.isValidPosition(x + dir.x, y + dir.y)
        ).length;
    }

    findAlternativePath(maze, ghostPositions) {
        const currentPos = { x: Math.round(this.x), y: Math.round(this.y) };
        const validMoves = Object.values(Direction).filter(dir => {
            const nextX = currentPos.x + dir.x;
            const nextY = currentPos.y + dir.y;
            return maze.isValidPosition(nextX, nextY);
        });

        const safestMove = validMoves.reduce((best, move) => {
            const nextX = currentPos.x + move.x;
            const nextY = currentPos.y + move.y;
            const ghostDanger = this.calculateGhostDanger(
                { x: nextX, y: nextY }, 
                ghostPositions
            );
            
            if (!best || ghostDanger > best.danger) {
                return { move, danger: ghostDanger };
            }
            return best;
        }, null);

        return safestMove ? safestMove.move : this.direction;
    }

    isNearTarget() {
        if (!this.currentPath.length) return true;
        
        const target = this.currentPath[0];
        const distance = Math.sqrt(
            Math.pow(this.x - target.x, 2) + 
            Math.pow(this.y - target.y, 2)
        );
        return distance < 0.3;
    }

    update(maze, ghostPositions) {
        const currentPos = { x: Math.round(this.x), y: Math.round(this.y) };
        let nextDirection = this.direction;

        if (this.autonomousMode) {
            if (this.isStuck()) {
                nextDirection = this.findAlternativePath(maze, ghostPositions);
                this.pathUpdateCooldown = 0;
                this.currentPath = [];
                console.debug('Pacman unstuck: new direction', nextDirection);
            } else {
                const ghostDanger = this.calculateGhostDanger(currentPos, ghostPositions);
                const inDanger = ghostDanger < this.dangerThreshold;

                if (this.pathUpdateCooldown <= 0) {
                    if (inDanger && !this.isPoweredUp) {
                        nextDirection = this.findEscapeDirection(currentPos, ghostPositions, maze);
                        this.currentPath = [];
                        this.pathUpdateCooldown = 2;
                    } else {
                        if (!this.currentPath.length || this.isNearTarget()) {
                            const pellets = this.getPelletPositions(maze);
                            const bestPellet = this.findBestPellet(pellets, ghostPositions, maze);
                            
                            if (bestPellet) {
                                this.currentPath = this.searchAlgorithm.findPath(
                                    currentPos,
                                    [bestPellet],
                                    maze
                                );
                            }
                        }

                        if (this.currentPath.length) {
                            const target = this.currentPath[0];
                            const dx = target.x - this.x;
                            const dy = target.y - this.y;
                            
                            if (Math.abs(dx) > Math.abs(dy)) {
                                nextDirection = dx > 0 ? Direction.RIGHT : Direction.LEFT;
                            } else {
                                nextDirection = dy > 0 ? Direction.DOWN : Direction.UP;
                            }
                        }
                        this.pathUpdateCooldown = 5;
                    }
                } else {
                    this.pathUpdateCooldown--;
                }
            }
        }

        const nextX = this.x + nextDirection.x * this.speed;
        const nextY = this.y + nextDirection.y * this.speed;
        const roundedX = Math.round(nextX);
        const roundedY = Math.round(nextY);

        if (maze.isValidPosition(roundedX, roundedY)) {
            if (!this.autonomousMode || this.isPoweredUp || 
                !this.isUnsafePosition(roundedX, roundedY, ghostPositions)) {
                this.x = nextX;
                this.y = nextY;
                this.direction = nextDirection;

                if (this.currentPath.length && this.isNearTarget()) {
                    this.currentPath.shift();
                }

                if (Math.abs(this.x - roundedX) < 0.3 && Math.abs(this.y - roundedY) < 0.3) {
                    const isPowerPellet = maze.eatPellet(roundedX, roundedY);
                    if (isPowerPellet) {
                        this.isPoweredUp = true;
                        this.powerTimer = 600;
                        this.score += 50;
                    } else {
                        this.score += 10;
                    }
                }
            }
        }

        if (this.isPoweredUp) {
            this.powerTimer--;
            if (this.powerTimer <= 0) {
                this.isPoweredUp = false;
            }
        }

        this.updateMouthAnimation();
    }

    isUnsafePosition(x, y, ghostPositions) {
        return ghostPositions.some(ghost => 
            Math.abs(x - ghost.x) + Math.abs(y - ghost.y) < 2
        );
    }

    draw(ctx, offset = 0) {
        const centerX = Math.round(this.x * CELL_SIZE + CELL_SIZE / 2);
        const centerY = Math.round(this.y * CELL_SIZE + CELL_SIZE / 2) + offset;
        const radius = Math.round(CELL_SIZE * 0.8 / 2);

        let rotationAngle = 0;
        if (this.direction === Direction.UP) rotationAngle = -90;
        else if (this.direction === Direction.DOWN) rotationAngle = 90;
        else if (this.direction === Direction.LEFT) rotationAngle = 180;

        ctx.save();
        ctx.translate(centerX, centerY);
        ctx.rotate(rotationAngle * Math.PI / 180);
        ctx.translate(-centerX, -centerY);

        ctx.beginPath();
        ctx.fillStyle = this.isPoweredUp ? 
            `hsl(60, 100%, ${50 + Math.sin(Date.now() / 100) * 20}%)` : 
            this.color;
        
        ctx.arc(
            centerX, 
            centerY, 
            radius,
            (this.mouthAngle * Math.PI / 180),
            (360 - this.mouthAngle) * Math.PI / 180
        );
        ctx.lineTo(centerX, centerY);
        ctx.fill();

        if (this.autonomousMode && this.currentPath.length) {
            ctx.restore();
            ctx.strokeStyle = 'rgba(255, 0, 0, 0.5)';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            
            this.currentPath.forEach(pos => {
                const pathX = pos.x * CELL_SIZE + CELL_SIZE / 2;
                const pathY = pos.y * CELL_SIZE + CELL_SIZE / 2 + offset;
                ctx.lineTo(pathX, pathY);
            });
            
            ctx.stroke();
            return;
        }

        ctx.restore();
    }

    updateMouthAnimation() {
        if (this.openingMouth) {
            this.mouthAngle = Math.min(45, this.mouthAngle + this.mouthSpeed);
            if (this.mouthAngle >= 45) this.openingMouth = false;
        } else {
            this.mouthAngle = Math.max(0, this.mouthAngle - this.mouthSpeed);
            if (this.mouthAngle <= 0) this.openingMouth = true;
        }
    }

    toggleControlMode() {
        this.autonomousMode = !this.autonomousMode;
        this.currentPath = [];
        this.pathUpdateCooldown = 0;
        this.noMovementCounter = 0;
        console.log(`Control mode: ${this.autonomousMode ? 'AI' : 'Manual'}`);
    }

    getPosition() {
        return { x: Math.round(this.x), y: Math.round(this.y) };
    }
}