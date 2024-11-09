import random
import pygame
import math
from typing import Tuple, List
from ..config.constants import Direction, CELL_SIZE, PACMAN_SPEED, CellType
from .base_agent import BaseAgent
from ..algorithms.search import AStarSearch, BreadthFirstSearch, UniformCostSearch

class PacmanAgent(BaseAgent):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.score = 0
        self.is_powered_up = False
        self.power_timer = 0
        self.mouth_angle = 0
        self.mouth_speed = 5
        self.opening_mouth = True
        
        # AI components
        self.current_path = []
        self.search_algorithm = AStarSearch()
        self.autonomous_mode = True
        self.stuck_timer = 0
        self.last_position = (x, y)
        self.no_movement_counter = 0
        
        # Colors
        self.YELLOW = (255, 255, 0)
        self.BLACK = (0, 0, 0)
    
    def get_pellet_positions(self, maze) -> List[Tuple[int, int]]:
        """Get positions of all pellets in the maze"""
        pellets = []
        for y in range(maze.height):
            for x in range(maze.width):
                cell_type = maze.get_cell_type(x, y)
                if cell_type in [CellType.PELLET, CellType.POWER_PELLET]:
                    pellets.append((x, y))
        return pellets
    
    def get_next_move(self, maze) -> Direction:
        """Get the next move based on AI or manual control"""
        if not self.autonomous_mode:
            return self._get_manual_input()
        
        return self._get_ai_move(maze)
    
    def _get_manual_input(self) -> Direction:
        """Handle manual keyboard input"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_UP]:
            return Direction.UP
        elif keys[pygame.K_DOWN]:
            return Direction.DOWN
        elif keys[pygame.K_LEFT]:
            return Direction.LEFT
        elif keys[pygame.K_RIGHT]:
            return Direction.RIGHT
        elif keys[pygame.K_SPACE]:
            self.toggle_control_mode()
        
        return self.direction
    
    def _get_ai_move(self, maze, ghost_positions: List[Tuple[int, int]]) -> Direction:
        """Calculate next move using AI with ghost avoidance"""
        current_pos = (int(round(self.x)), int(round(self.y)))
        
        # Check if we're in danger (too close to ghosts)
        in_danger = False
        for ghost_pos in ghost_positions:
            distance = abs(current_pos[0] - ghost_pos[0]) + abs(current_pos[1] - ghost_pos[1])
            if distance < 3:  # Danger threshold
                in_danger = True
                break
        
        # If in danger, focus on escaping
        if in_danger and not self.is_powered_up:
            # Find direction that maximizes distance from all ghosts
            best_direction = self.direction
            max_min_distance = -1
            
            for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN]:
                next_x = current_pos[0] + direction.value[0]
                next_y = current_pos[1] + direction.value[1]
                
                if maze.is_valid_position(next_x, next_y):
                    # Calculate minimum distance to any ghost from this position
                    min_ghost_distance = min(
                        abs(next_x - gx) + abs(next_y - gy)
                        for gx, gy in ghost_positions
                    )
                    
                    if min_ghost_distance > max_min_distance:
                        max_min_distance = min_ghost_distance
                        best_direction = direction
            
            self.current_path = []  # Clear current path when in danger
            return best_direction
        
        # Normal pathfinding to pellets when safe
        if not self.current_path or self._is_near_target():
            pellets = self.get_pellet_positions(maze)
            if pellets:
                # Find the safest pellet to target
                safest_pellet = max(pellets, key=lambda p: min(
                    abs(p[0] - gx) + abs(p[1] - gy)
                    for gx, gy in ghost_positions
                ))
                self.current_path = self.search_algorithm.find_path(
                    current_pos, [safest_pellet], maze)
        
        # If we have a path, follow it
        if self.current_path:
            target = self.current_path[0]
            dx = target[0] - self.x
            dy = target[1] - self.y
            
            if abs(dx) > abs(dy):
                return Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                return Direction.DOWN if dy > 0 else Direction.UP
        
        # If no path, find a safe direction
        valid_directions = []
        for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN]:
            next_x = current_pos[0] + direction.value[0]
            next_y = current_pos[1] + direction.value[1]
            if maze.is_valid_position(next_x, next_y):
                # Check if this direction is safe from ghosts
                min_ghost_distance = min(
                    abs(next_x - gx) + abs(next_y - gy)
                    for gx, gy in ghost_positions
                )
                if min_ghost_distance >= 2:  # Safe distance threshold
                    valid_directions.append(direction)
        
        if valid_directions:
            return random.choice(valid_directions)
        
        # If no safe direction, keep current direction if valid
        next_x = current_pos[0] + self.direction.value[0]
        next_y = current_pos[1] + self.direction.value[1]
        if maze.is_valid_position(next_x, next_y):
            return self.direction
            
        # Last resort: any valid direction
        for direction in [Direction.RIGHT, Direction.LEFT, Direction.UP, Direction.DOWN]:
            next_x = current_pos[0] + direction.value[0]
            next_y = current_pos[1] + direction.value[1]
            if maze.is_valid_position(next_x, next_y):
                return direction
                
        return self.direction
    
    def _is_near_target(self) -> bool:
        """Check if Pacman is near the next target in the path"""
        if not self.current_path:
            return True
            
        target = self.current_path[0]
        distance = math.sqrt((self.x - target[0])**2 + (self.y - target[1])**2)
        return distance < 0.3  # Increased threshold
    
    def update(self, maze, ghost_positions: List[Tuple[int, int]]):
        """Update Pacman's position and state"""
        # Get next move from AI or manual control
        if self.autonomous_mode:
            next_direction = self._get_ai_move(maze, ghost_positions)
        else:
            next_direction = self._get_manual_input()
        
        # Calculate next position
        next_x = self.x + next_direction.value[0] * PACMAN_SPEED
        next_y = self.y + next_direction.value[1] * PACMAN_SPEED
        
        # Round positions for better grid alignment
        cell_x = int(round(next_x))
        cell_y = int(round(next_y))
        
        # Check if the move is valid
        if maze.is_valid_position(cell_x, cell_y):
            # Check if move is safe from ghosts
            if self.autonomous_mode and not self.is_powered_up:
                too_close_to_ghost = any(
                    abs(cell_x - gx) + abs(cell_y - gy) < 2
                    for gx, gy in ghost_positions
                )
                if too_close_to_ghost:
                    return  # Don't make the move if it's too dangerous
            
            self.x = next_x
            self.y = next_y
            self.direction = next_direction
            
            # Remove reached positions from path
            if self.current_path and self._is_near_target():
                self.current_path.pop(0)
            
            # Check for pellet collection
            cell_x = int(round(self.x))
            cell_y = int(round(self.y))
            
            if (abs(self.x - cell_x) < 0.3 and abs(self.y - cell_y) < 0.3):
                is_power_pellet = maze.eat_pellet(cell_x, cell_y)
                if is_power_pellet:
                    self.is_powered_up = True
                    self.power_timer = 600
                    self.score += 50
                else:
                    self.score += 10
        
        # Update power-up timer
        if self.is_powered_up:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.is_powered_up = False
        
        # Update mouth animation
        if self.opening_mouth:
            self.mouth_angle = min(45, self.mouth_angle + self.mouth_speed)
            if self.mouth_angle >= 45:
                self.opening_mouth = False
        else:
            self.mouth_angle = max(0, self.mouth_angle - self.mouth_speed)
            if self.mouth_angle <= 0:
                self.opening_mouth = True
    
    def draw(self, screen, offset_y=0):
        """Draw Pacman with vertical offset"""
        # Calculate center position
        center_x = int(self.x * CELL_SIZE + CELL_SIZE // 2)
        center_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        
        direction_angle = {
            Direction.RIGHT: 0,
            Direction.UP: 90,
            Direction.LEFT: 180,
            Direction.DOWN: 270
        }[self.direction]
        
        # Draw Pacman body
        pygame.draw.circle(screen, self.YELLOW, (center_x, center_y), 
                         int(CELL_SIZE * 0.8 // 2))
        
        # Draw mouth
        if self.mouth_angle > 0:
            start_angle = math.radians(direction_angle - self.mouth_angle)
            end_angle = math.radians(direction_angle + self.mouth_angle)
            
            pygame.draw.arc(screen, self.BLACK, 
                          (center_x - CELL_SIZE//2, 
                           center_y - CELL_SIZE//2,
                           CELL_SIZE, CELL_SIZE),
                           start_angle, end_angle, 3)
        
        # Draw the planned path
        if self.autonomous_mode and self.current_path:
            for x, y in self.current_path:
                path_center_x = int(x * CELL_SIZE + CELL_SIZE // 2)
                path_center_y = int(y * CELL_SIZE + CELL_SIZE // 2) + offset_y
                pygame.draw.circle(screen, (255, 0, 0), 
                                (path_center_x, path_center_y), 2)
    
    def toggle_control_mode(self):
        """Toggle between AI and manual control"""
        self.autonomous_mode = not self.autonomous_mode
        self.current_path = []
        print(f"Control mode: {'AI' if self.autonomous_mode else 'Manual'}")