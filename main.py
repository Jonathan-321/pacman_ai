import pygame
from src.core.game import Game

def main():
    pygame.init()
    
    game = Game()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        running = game.handle_events()
        
        # Update game state
        game.update()
        
        # Draw frame
        game.draw()
        
        # Control frame rate
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()