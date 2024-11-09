# Required imports
import pygame
import math
import time
from typing import List, Tuple
from ..config.constants import (SCREEN_WIDTH, SCREEN_HEIGHT, FPS, CELL_SIZE,
                              MAZE_WIDTH, MAZE_HEIGHT, SCOREBOARD_HEIGHT, CellType)
from ..config.maze_layouts import LEVEL_1
from ..environment.maze import Maze
from ..agents.pacman import PacmanAgent
from ..agents.ghost import GhostAgent
from ..utils.sound_manager import SoundManager


# Initialize Pygame
pygame.init()

class Game:
    def __init__(self):
        """Initialize the game state"""
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PACMAN AI")
        

        # Initialize pygame and sound
        pygame.init()
        pygame.mixer.init()
        
        # Initialize display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("PACMAN AI")
        
        # Initialize sound manager
        self.sound_manager = SoundManager()
        try:
            self.sound_manager.load_sounds()
            print("Sound system initialized successfully")
        except Exception as e:
            print(f"Warning: Sound initialization failed: {e}")
        
        # Play start sound
        try:
            self.sound_manager.play_sound('game_start')
        except Exception as e:
            print(f"Warning: Could not play start sound: {e}")

        # Initialize fonts
        pygame.font.init()
        self.font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 30)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.DARK_BLUE = (0, 0, 139)
        self.NAVY_BLUE = (0, 0, 128)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.PURPLE = (128, 0, 128)
        self.GRAY = (128, 128, 128)
        
        # Visual effects
        self.pellet_animation = 0
        self.bg_animation = 0
        self.flash_timer = 0
        
        # Initialize game state
        self.reset_game()

        self.sound_manager = SoundManager()
        self.sound_manager.load_sounds()


    def _count_initial_pellets(self) -> int:
        """Count initial number of pellets and power pellets"""
        count = 0
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                if cell in [CellType.PELLET, CellType.POWER_PELLET]:
                    count += 1
        return count

    def reset_game(self):
        """Reset the game state"""
        # Initialize maze
        self.maze = Maze(MAZE_WIDTH, MAZE_HEIGHT)
        self.maze.load_layout(LEVEL_1)
        
        # Initialize Pacman
        pacman_x, pacman_y = self.maze.pacman_start
        self.pacman = PacmanAgent(pacman_x, pacman_y)
        
        # Initialize ghosts with different colors
        self.ghosts = []
        ghost_colors = [
            (255, 0, 0),    # Blinky (red)
            (255, 182, 255), # Pinky (pink)
            (0, 255, 255),   # Inky (cyan)
            (255, 182, 85)   # Clyde (orange)
        ]
        ghost_corners = [
            (MAZE_WIDTH-1, 0),        # Top-right
            (0, 0),                   # Top-left
            (MAZE_WIDTH-1, MAZE_HEIGHT-1),  # Bottom-right
            (0, MAZE_HEIGHT-1)        # Bottom-left
        ]
        
        for (x, y), color, corner in zip(self.maze.ghost_starts, ghost_colors, ghost_corners):
            ghost = GhostAgent(x, y, color)
            ghost.set_home_corner(corner)
            self.ghosts.append(ghost)
        
        # Game state
        self.is_game_over = False
        self.game_won = False
        self.score = 0
        self.total_pellets = self._count_initial_pellets()
        self.final_message = ""
        
        # Time tracking
        self.start_time = time.time()
        self.time_elapsed = 0
        
        # Ghost mode timing
        self.ghost_mode_timer = 0
        self.ghost_mode_scatter = True

        self.sound_manager.play_sound('game_start')


    
    def draw(self):
        """Draw the current game state"""
        # Draw background and maze base
        self.screen.fill(self.BLACK)
        self.draw_maze_background()
        
        # Draw scoreboard with gradient
        scoreboard_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCOREBOARD_HEIGHT)
        self.draw_gradient_rect(scoreboard_rect, self.DARK_BLUE, self.NAVY_BLUE)
        
        # Draw game info
        score_text = self.font.render(f'Score: {self.score}', True, self.WHITE)
        self.screen.blit(score_text, (20, 10))
        
        pellets_text = self.font.render(
            f'Pellets: {self.count_pellets()}/{self.total_pellets}', 
            True, self.WHITE)
        pellets_rect = pellets_text.get_rect()
        self.screen.blit(pellets_text, (SCREEN_WIDTH - pellets_rect.width - 20, 10))
        
        # Draw time with pulsing effect
        time_color = (255, 
                     255 - int(abs(math.sin(time.time() * 2)) * 100), 
                     255 - int(abs(math.sin(time.time() * 2)) * 100))
        time_text = self.small_font.render(
            f'Time: {self.time_elapsed}s', True, time_color)
        self.screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 20))
        
        # Draw maze content
        maze_offset_y = SCOREBOARD_HEIGHT
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell_rect = pygame.Rect(
                    x * CELL_SIZE, 
                    y * CELL_SIZE + maze_offset_y, 
                    CELL_SIZE, 
                    CELL_SIZE
                )
                
                cell = self.maze.grid[y][x]
                if cell == CellType.WALL:
                    # Draw walls with gradient
                    wall_rect = pygame.Rect(
                        x * CELL_SIZE + 1, 
                        y * CELL_SIZE + maze_offset_y + 1, 
                        CELL_SIZE - 2, 
                        CELL_SIZE - 2
                    )
                    self.draw_gradient_rect(wall_rect, self.BLUE, self.DARK_BLUE)
                elif cell == CellType.PELLET:
                    # Animated pellets
                    size = 4 + math.sin(self.pellet_animation + x * 0.5 + y * 0.5)
                    pygame.draw.circle(
                        self.screen,
                        self.WHITE,
                        (x * CELL_SIZE + CELL_SIZE // 2,
                         y * CELL_SIZE + CELL_SIZE // 2 + maze_offset_y),
                        size
                    )
                elif cell == CellType.POWER_PELLET:
                    # Pulsing power pellets
                    size = 8 + math.sin(self.pellet_animation * 2) * 2
                    color = (255, 255, int(128 + math.sin(self.pellet_animation) * 127))
                    pygame.draw.circle(
                        self.screen,
                        color,
                        (x * CELL_SIZE + CELL_SIZE // 2,
                         y * CELL_SIZE + CELL_SIZE // 2 + maze_offset_y),
                        size
                    )
        
        self.pellet_animation += 0.1
        
        # Draw ghosts with shadows
        for ghost in self.ghosts:
            # Draw ghost shadow
            shadow_pos = (
                int(ghost.x * CELL_SIZE + CELL_SIZE // 2) + 4,
                int(ghost.y * CELL_SIZE + CELL_SIZE // 2) + maze_offset_y + 4
            )
            shadow_radius = int(CELL_SIZE * 0.8 // 2)
            shadow_surface = pygame.Surface((shadow_radius * 2, shadow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(shadow_surface, (0, 0, 0, 64), 
                             (shadow_radius, shadow_radius), shadow_radius)
            self.screen.blit(shadow_surface, 
                           (shadow_pos[0] - shadow_radius, shadow_pos[1] - shadow_radius))
            
            ghost.draw(self.screen, maze_offset_y)
        
        # Draw Pacman
        if self.pacman.is_powered_up:
            # Add glow effect when powered up
            glow_radius = int(CELL_SIZE * 1.2)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            center = (glow_radius, glow_radius)
            for i in range(10):
                alpha = int(25 * (1 - i/10))
                pygame.draw.circle(glow_surface, (255, 255, 0, alpha), center, glow_radius - i * 2)
            glow_pos = (
                int(self.pacman.x * CELL_SIZE + CELL_SIZE // 2) - glow_radius,
                int(self.pacman.y * CELL_SIZE + CELL_SIZE // 2) + maze_offset_y - glow_radius
            )
            self.screen.blit(glow_surface, glow_pos)
            
        self.pacman.draw(self.screen, maze_offset_y)
        
        # Draw game over screen
        if self.is_game_over:
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(self.BLACK)
            overlay.set_alpha(128)
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over message with animation
            color = self.GREEN if self.game_won else self.RED
            scale = 1 + math.sin(time.time() * 4) * 0.1
            text = self.font.render(self.final_message, True, color)
            scaled_text = pygame.transform.scale(
                text, 
                (int(text.get_width() * scale), 
                 int(text.get_height() * scale))
            )
            text_rect = scaled_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(scaled_text, text_rect)
            
            # Draw restart instruction with fade effect
            alpha = int(abs(math.sin(time.time() * 2)) * 255)
            restart_text = self.small_font.render('Press SPACE to restart or ESC to quit', 
                                                True, self.WHITE)
            restart_surface = pygame.Surface(restart_text.get_size(), pygame.SRCALPHA)
            restart_surface.blit(restart_text, (0, 0))
            restart_surface.set_alpha(alpha)
            restart_rect = restart_surface.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
            )
            self.screen.blit(restart_surface, restart_rect)
            
            # Draw final stats
            stats_text = self.small_font.render(
                f'Pellets: {self.count_pellets()}/{self.total_pellets} | Time: {self.time_elapsed}s', 
                True, self.WHITE)
            stats_rect = stats_text.get_rect(
                center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)
            )
            self.screen.blit(stats_text, stats_rect)
        
        pygame.display.flip()

    def draw_gradient_rect(self, rect, color1, color2, vertical=True):
        """Draw a rectangle with a gradient between two colors"""
        if vertical:
            for i in range(rect.height):
                factor = i / rect.height
                color = (
                    int(color1[0] * (1 - factor) + color2[0] * factor),
                    int(color1[1] * (1 - factor) + color2[1] * factor),
                    int(color1[2] * (1 - factor) + color2[2] * factor)
                )
                pygame.draw.line(self.screen, color, 
                               (rect.x, rect.y + i), 
                               (rect.x + rect.width, rect.y + i))
        else:
            for i in range(rect.width):
                factor = i / rect.width
                color = (
                    int(color1[0] * (1 - factor) + color2[0] * factor),
                    int(color1[1] * (1 - factor) + color2[1] * factor),
                    int(color1[2] * (1 - factor) + color2[2] * factor)
                )
                pygame.draw.line(self.screen, color, 
                               (rect.x + i, rect.y), 
                               (rect.x + i, rect.y + rect.height))

    def draw_maze_background(self):
        """Draw animated maze background"""
        for y in range(0, SCREEN_HEIGHT, 20):
            for x in range(0, SCREEN_WIDTH, 20):
                offset = math.sin((x + y + self.bg_animation) / 30) * 2
                size = 10 + offset
                pygame.draw.rect(self.screen, self.NAVY_BLUE,
                               (x, y + SCOREBOARD_HEIGHT, size, size))
        self.bg_animation = (self.bg_animation + 1) % 360

    def _check_collision(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        """Check if two positions are close enough to count as a collision"""
        distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return distance < 0.7

    def count_pellets(self) -> int:
        """Count current number of pellets"""
        count = 0
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                if cell in [CellType.PELLET, CellType.POWER_PELLET]:
                    count += 1
        return count

    def check_win_condition(self) -> bool:
        """Check if all pellets have been collected"""
        return self.count_pellets() == 0

    def update(self):
        """Update game state"""
        if not self.is_game_over:
            # Get ghost positions for Pacman AI
            ghost_positions = [(int(round(ghost.x)), int(round(ghost.y))) 
                            for ghost in self.ghosts]
            
            # Update Pacman
            self.pacman.update(self.maze, ghost_positions)
            pacman_pos = (int(round(self.pacman.x)), int(round(self.pacman.y)))
            
            # Update ghosts
            for ghost in self.ghosts:
                ghost.update(self.maze, pacman_pos)
                ghost_pos = (int(round(ghost.x)), int(round(ghost.y)))
                
                # Check for collisions
                if self._check_collision(pacman_pos, ghost_pos):
                    if ghost.is_frightened:
                        # Ghost gets eaten
                        ghost.x, ghost.y = self.maze.ghost_starts[0]
                        self.pacman.score += 200
                        self.sound_manager.play_sound('ghost_eat')
                    else:
                        # Pacman gets caught
                        self.is_game_over = True
                        self.game_won = False
                        self.final_message = f"Game Over! Score: {self.pacman.score}"
                        self.sound_manager.play_sound('death')
            
            # Check for win condition
            if self.check_win_condition():
                self.is_game_over = True
                self.game_won = True
                self.final_message = f"You Win! Final Score: {self.pacman.score}"
                self.sound_manager.play_sound('win')
            
            # Update score
            self.score = self.pacman.score
            
            # Handle power pellet effects
            if self.pacman.is_powered_up:
                for ghost in self.ghosts:
                    if not ghost.is_frightened:
                        ghost.make_frightened()
                        self.sound_manager.play_sound('power_pellet')

    def handle_events(self) -> bool:
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_SPACE and self.is_game_over:
                    self.reset_game()
                elif event.key == pygame.K_t:  # Toggle AI/Manual control
                    self.pacman.toggle_control_mode()
        
        return True


    def handle_pellet_collection(self, is_power_pellet):
        """Handle pellet collection and sounds"""
        if is_power_pellet:
            self.sound_manager.play_sound('power_pellet')
            self.score += 50
        else:
            self.sound_manager.play_sound('chomp')
            self.score += 10