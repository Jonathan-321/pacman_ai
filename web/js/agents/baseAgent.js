import { Direction } from '../config/constants.js';

export class BaseAgent {
    constructor(x, y) {
        this.x = x;
        this.y = y;
        this._baseSpeed = null;  // Store initial speed
        this._currentSpeed = null;
    }

    set speed(value) {
        if (this._baseSpeed === null) {
            this._baseSpeed = value;  // Store initial speed on first set
        }
        this._currentSpeed = value;
    }

    get speed() {
        return this._currentSpeed;
    }

    resetSpeed() {
        this._currentSpeed = this._baseSpeed;
    }

    getPosition() {
        return {
            x: Math.round(this.x),
            y: Math.round(this.y)
        };
    }

    distanceTo(target) {
        const pos = this.getPosition();
        return Math.abs(pos.x - target.x) + Math.abs(pos.y - target.y);
    }

    isValidMove(maze, direction) {
        const nextX = Math.round(this.x) + direction.x;
        const nextY = Math.round(this.y) + direction.y;
        return maze.isValidPosition(nextX, nextY);
    }

    getValidMoves(maze) {
        return Object.values(Direction).filter(dir => this.isValidMove(maze, dir));
    }

    update(maze) {
        // To be implemented by child classes
        throw new Error('Update method must be implemented by child classes');
    }

    draw(ctx, offset = 0) {
        // To be implemented by child classes
        throw new Error('Draw method must be implemented by child classes');
    }
}