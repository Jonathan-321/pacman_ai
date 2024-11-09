import pygame
import asyncio
from typing import Optional

class WebGameAdapter:
    def __init__(self, canvas_id: str):
        self.canvas = document.getElementById(canvas_id)
        self.ctx = self.canvas.getContext('2d')
        self.width = self.canvas.width
        self.height = self.canvas.height
        
        # Initialize Pygame for web
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Setup event handling
        self._setup_events()
    
    def _setup_events(self):
        """Setup web event handlers"""
        def handle_keydown(event):
            # Convert web keycode to Pygame key
            key_mapping = {
                'ArrowUp': pygame.K_UP,
                'ArrowDown': pygame.K_DOWN,
                'ArrowLeft': pygame.K_LEFT,
                'ArrowRight': pygame.K_RIGHT,
                'Space': pygame.K_SPACE,
                'Escape': pygame.K_ESCAPE,
                't': pygame.K_t,
                'm': pygame.K_m
            }
            
            if event.key in key_mapping:
                pygame_event = pygame.event.Event(
                    pygame.KEYDOWN,
                    {'key': key_mapping[event.key]}
                )
                pygame.event.post(pygame_event)
        
        # Add event listeners
        self.canvas.addEventListener('keydown', handle_keydown)
    
    def update_display(self):
        """Copy Pygame surface to canvas"""
        # Get Pygame surface data
        surface_data = pygame.surfarray.array3d(self.screen)
        
        # Convert to ImageData
        image_data = self.ctx.createImageData(self.width, self.height)
        
        # Copy pixel data
        for y in range(self.height):
            for x in range(self.width):
                i = (y * self.width + x) * 4
                r, g, b = surface_data[x][y]
                image_data.data[i] = r
                image_data.data[i + 1] = g
                image_data.data[i + 2] = b
                image_data.data[i + 3] = 255
        
        # Put image data to canvas
        self.ctx.putImageData(image_data, 0, 0)