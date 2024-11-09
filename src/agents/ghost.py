import pygame
import random
import math
from typing import Tuple, List
from ..config.constants import Direction, CELL_SIZE, GHOST_SPEED, CellType

class GhostAgent:
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.direction = Direction.RIGHT
        self.is_frightened = False
        self.frightened_timer = 0
        self.frightened_color = (0, 0, 255)  # Blue when frightened
        self.speed = GHOST_SPEED
        self.scatter_mode = False
        self.scatter_timer = 0
        self.home_corner = None
        self.stuck_counter = 0
        self.last_position = (x, y)
        self.direction_change_cooldown = 0
        self.last_valid_direction = None
        
    def set_home_corner(self, corner: Tuple[int, int]):
        """Set the ghost's home corner for scatter mode"""
        self.home_corner = corner
    
    def get_valid_moves(self, maze, exclude_reverse: bool = True) -> List[Direction]:
        """Get list of valid directions from current position"""
        valid_moves = []
        current_x, current_y = int(round(self.x)), int(round(self.y))
        
        for direction in Direction:
            # Don't allow reversing unless specifically allowed
            if exclude_reverse and self._is_opposite_direction(direction, self.direction):
                continue
                
            next_x = current_x + direction.value[0]
            next_y = current_y + direction.value[1]
            
            if maze.is_valid_position(next_x, next_y):
                valid_moves.append(direction)
        
        # If no valid moves and reverse was excluded, try including reverse
        if not valid_moves and exclude_reverse:
            return self.get_valid_moves(maze, exclude_reverse=False)
            
        return valid_moves
    
    def _is_opposite_direction(self, dir1: Direction, dir2: Direction) -> bool:
        """Check if two directions are opposite"""
        return (dir1.value[0] == -dir2.value[0] and 
                dir1.value[1] == -dir2.value[1])
    
    def _distance_to_target(self, x: int, y: int, target: Tuple[int, int]) -> float:
        """Calculate Manhattan distance to target"""
        return abs(x - target[0]) + abs(y - target[1])
    
    def choose_direction(self, maze, pacman_pos: Tuple[int, int]) -> Direction:
        """Choose next direction based on current mode and target"""
        current_x = int(round(self.x))
        current_y = int(round(self.y))
        current_pos = (current_x, current_y)
        
        # If movement is locked, continue in current direction if possible
        if self.direction_change_cooldown > 0:
            self.direction_change_cooldown -= 1
            if maze.is_valid_position(current_x + self.direction.value[0], 
                                    current_y + self.direction.value[1]):
                return self.direction
        
        # Get valid moves
        valid_moves = self.get_valid_moves(maze)
        if not valid_moves:
            return self.direction
            
        # If frightened, move randomly but smartly
        if self.is_frightened:
            # Prefer moves that lead away from Pacman
            safe_moves = []
            for move in valid_moves:
                next_x = current_x + move.value[0]
                next_y = current_y + move.value[1]
                if self._distance_to_target(next_x, next_y, pacman_pos) > 3:
                    safe_moves.append(move)
            
            if safe_moves:
                self.direction = random.choice(safe_moves)
            else:
                self.direction = random.choice(valid_moves)
            
            self.direction_change_cooldown = 2
            return self.direction
        
        # Choose target based on mode
        target = self.home_corner if self.scatter_mode else pacman_pos
        
        # Calculate distances to target for each valid move
        move_scores = []
        for move in valid_moves:
            next_x = current_x + move.value[0]
            next_y = current_y + move.value[1]
            
            # Base score on distance to target
            score = -self._distance_to_target(next_x, next_y, target)
            
            # Prefer continuing in same direction (reduce jitter)
            if move == self.direction:
                score += 0.5
                
            # Avoid going back and forth
            if self.last_valid_direction and self._is_opposite_direction(move, self.last_valid_direction):
                score -= 1
                
            move_scores.append((score, move))
        
        # Choose best move
        self.direction = max(move_scores, key=lambda x: x[0])[1]
        self.last_valid_direction = self.direction
        self.direction_change_cooldown = 2
        
        return self.direction
    
    def update(self, maze, pacman_pos: Tuple[int, int]):
        """Update ghost position and state"""
        # Update timers
        if self.is_frightened:
            self.frightened_timer -= 1
            if self.frightened_timer <= 0:
                self.is_frightened = False
                self.speed = GHOST_SPEED
        
        if self.scatter_mode:
            self.scatter_timer -= 1
            if self.scatter_timer <= 0:
                self.scatter_mode = False
        
        # Check if stuck
        current_pos = (int(round(self.x)), int(round(self.y)))
        if current_pos == self.last_position:
            self.stuck_counter += 1
            if self.stuck_counter > 5:  # If stuck for too long
                valid_moves = self.get_valid_moves(maze, exclude_reverse=False)
                if valid_moves:
                    self.direction = random.choice(valid_moves)
                self.stuck_counter = 0
        else:
            self.stuck_counter = 0
        self.last_position = current_pos
        
        # Choose new direction
        self.direction = self.choose_direction(maze, pacman_pos)
        
        # Update position
        next_x = self.x + self.direction.value[0] * self.speed
        next_y = self.y + self.direction.value[1] * self.speed
        
        # Check if move is valid
        if maze.is_valid_position(int(round(next_x)), int(round(next_y))):
            self.x = next_x
            self.y = next_y
    
    def make_frightened(self):
        """Make ghost frightened"""
        self.is_frightened = True
        self.frightened_timer = 600  # 10 seconds
        self.speed = GHOST_SPEED * 0.5  # Slower when frightened
    
    def enter_scatter_mode(self):
        """Enter scatter mode"""
        self.scatter_mode = True
        self.scatter_timer = 420  # 7 seconds
    
    def draw(self, screen, offset_y=0):
        """Draw ghost with vertical offset"""
        center_x = int(self.x * CELL_SIZE + CELL_SIZE // 2)
        center_y = int(self.y * CELL_SIZE + CELL_SIZE // 2) + offset_y
        
        color = self.frightened_color if self.is_frightened else self.color
        
        # Draw ghost body
        radius = int(CELL_SIZE * 0.8 // 2)
        pygame.draw.circle(screen, color, (center_x, center_y), radius)
        
        # Draw ghost skirt
        skirt_points = [
            (center_x - radius, center_y),
            (center_x - radius, center_y + radius//2),
            (center_x - radius//2, center_y),
            (center_x, center_y + radius//2),
            (center_x + radius//2, center_y),
            (center_x + radius, center_y + radius//2),
            (center_x + radius, center_y)
        ]
        pygame.draw.polygon(screen, color, skirt_points)
        
        # Draw eyes (unless frightened)
        if not self.is_frightened:
            eye_color = (255, 255, 255)  # White
            pupil_color = (0, 0, 0)      # Black
            
            # Left eye
            pygame.draw.circle(screen, eye_color, 
                             (center_x - radius//3, center_y - radius//4), radius//4)
            pygame.draw.circle(screen, pupil_color,
                             (center_x - radius//3, center_y - radius//4), radius//8)
            
            # Right eye
            pygame.draw.circle(screen, eye_color,
                             (center_x + radius//3, center_y - radius//4), radius//4)
            pygame.draw.circle(screen, pupil_color,
                             (center_x + radius//3, center_y - radius//4), radius//8)
        else:
            # Draw frightened eyes (simple white eyes)
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x - radius//3, center_y - radius//4), radius//6)
            pygame.draw.circle(screen, (255, 255, 255),
                             (center_x + radius//3, center_y - radius//4), radius//6)