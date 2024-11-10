class PriorityQueue {
    constructor() {
        this.values = [];
    }

    enqueue(val, priority) {
        this.values.push({ val, priority });
        this.sort();
    }

    dequeue() {
        return this.values.shift();
    }

    sort() {
        this.values.sort((a, b) => a.priority - b.priority);
    }

    isEmpty() {
        return this.values.length === 0;
    }
}

export class SearchAlgorithm {
    findPath(start, goals, maze) {
        throw new Error('Method not implemented');
    }
}

export class BreadthFirstSearch extends SearchAlgorithm {
    findPath(start, goals, maze) {
        if (!goals || goals.length === 0) return [];

        // Convert goals to a Set for O(1) lookup
        const goalSet = new Set(goals.map(goal => `${goal.x},${goal.y}`));

        // Queue stores [position, path]
        const queue = [[start, [start]]];
        const visited = new Set([`${start.x},${start.y}`]);

        // Possible movements (up, right, down, left)
        const directions = [
            { x: 0, y: -1 }, { x: 1, y: 0 },
            { x: 0, y: 1 }, { x: -1, y: 0 }
        ];

        while (queue.length > 0) {
            const [current, path] = queue.shift();
            const currentKey = `${current.x},${current.y}`;

            if (goalSet.has(currentKey)) {
                return path.slice(1); // Exclude start position
            }

            for (const dir of directions) {
                const nextX = current.x + dir.x;
                const nextY = current.y + dir.y;
                const nextPos = { x: nextX, y: nextY };
                const nextKey = `${nextX},${nextY}`;

                if (!visited.has(nextKey) && maze.isValidPosition(nextX, nextY)) {
                    visited.add(nextKey);
                    queue.push([nextPos, [...path, nextPos]]);
                }
            }
        }

        return []; // No path found
    }
}

export class AStarSearch extends SearchAlgorithm {
    heuristic(pos, goal) {
        return Math.abs(pos.x - goal.x) + Math.abs(pos.y - goal.y);
    }

    findPath(start, goals, maze) {
        if (!goals || goals.length === 0) return [];

        // Find nearest goal using Manhattan distance
        const nearestGoal = goals.reduce((nearest, current) => 
            this.heuristic(start, current) < this.heuristic(start, nearest) 
                ? current 
                : nearest
        , goals[0]);

        // Priority queue stores [fScore, position, path]
        const openSet = new PriorityQueue();
        openSet.enqueue(start, 0);

        // Track gScores (cost from start to node)
        const gScores = new Map();
        gScores.set(`${start.x},${start.y}`, 0);

        // Track paths
        const cameFrom = new Map();

        // Track fScores
        const fScores = new Map();
        fScores.set(`${start.x},${start.y}`, this.heuristic(start, nearestGoal));

        // Possible movements
        const directions = [
            { x: 0, y: -1 }, { x: 1, y: 0 },
            { x: 0, y: 1 }, { x: -1, y: 0 }
        ];

        while (!openSet.isEmpty()) {
            const current = openSet.dequeue().val;
            const currentKey = `${current.x},${current.y}`;

            if (current.x === nearestGoal.x && current.y === nearestGoal.y) {
                // Reconstruct path
                const path = [];
                let currentPos = current;
                while (cameFrom.has(`${currentPos.x},${currentPos.y}`)) {
                    path.unshift(currentPos);
                    currentPos = cameFrom.get(`${currentPos.x},${currentPos.y}`);
                }
                return path;
            }

            for (const dir of directions) {
                const nextX = current.x + dir.x;
                const nextY = current.y + dir.y;
                const neighbor = { x: nextX, y: nextY };
                const neighborKey = `${nextX},${nextY}`;

                if (!maze.isValidPosition(nextX, nextY)) continue;

                const tentativeGScore = gScores.get(currentKey) + 1;

                if (!gScores.has(neighborKey) || tentativeGScore < gScores.get(neighborKey)) {
                    cameFrom.set(neighborKey, current);
                    gScores.set(neighborKey, tentativeGScore);
                    const fScore = tentativeGScore + this.heuristic(neighbor, nearestGoal);
                    fScores.set(neighborKey, fScore);
                    openSet.enqueue(neighbor, fScore);
                }
            }
        }

        return []; // No path found
    }
}

export class UniformCostSearch extends SearchAlgorithm {
    findPath(start, goals, maze) {
        if (!goals || goals.length === 0) return [];

        // Convert goals to Set for O(1) lookup
        const goalSet = new Set(goals.map(goal => `${goal.x},${goal.y}`));

        // Priority queue stores [cost, position, path]
        const queue = new PriorityQueue();
        queue.enqueue(start, 0);

        // Track visited nodes and their costs
        const visited = new Map();
        visited.set(`${start.x},${start.y}`, 0);

        // Track paths
        const cameFrom = new Map();

        // Possible movements
        const directions = [
            { x: 0, y: -1 }, { x: 1, y: 0 },
            { x: 0, y: 1 }, { x: -1, y: 0 }
        ];

        while (!queue.isEmpty()) {
            const current = queue.dequeue();
            const currentPos = current.val;
            const currentKey = `${currentPos.x},${currentPos.y}`;
            const cost = current.priority;

            if (goalSet.has(currentKey)) {
                // Reconstruct path
                const path = [];
                let currentNode = currentPos;
                while (cameFrom.has(`${currentNode.x},${currentNode.y}`)) {
                    path.unshift(currentNode);
                    currentNode = cameFrom.get(`${currentNode.x},${currentNode.y}`);
                }
                return path;
            }

            for (const dir of directions) {
                const nextX = currentPos.x + dir.x;
                const nextY = currentPos.y + dir.y;
                const neighbor = { x: nextX, y: nextY };
                const neighborKey = `${nextX},${nextY}`;

                if (!maze.isValidPosition(nextX, nextY)) continue;

                const newCost = cost + 1;

                if (!visited.has(neighborKey) || newCost < visited.get(neighborKey)) {
                    visited.set(neighborKey, newCost);
                    cameFrom.set(neighborKey, currentPos);
                    queue.enqueue(neighbor, newCost);
                }
            }
        }

        return []; // No path found
    }
}