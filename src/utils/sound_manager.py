import numpy
import pygame
import os
from pathlib import Path

class SoundManager:
    def __init__(self):
        """Initialize the sound manager"""
        pygame.mixer.init(44100, -16, 2, 2048)
        self.sounds = {}
        self.sound_enabled = True
        self.current_music = None
        
        # Define sound types and their volumes
        self.sound_config = {
            'chomp': 0.5,        # Pellet eating sound
            'power_pellet': 0.7,  # Power pellet sound
            'ghost_eat': 0.8,     # Eating ghost sound
            'death': 0.7,         # Pacman death sound
            'game_start': 0.6,    # Game start sound
            'win': 0.7           # Victory sound
        }
        
        self.load_sounds()
    
    def load_sounds(self):
        """Load all game sounds"""
        sounds_dir = Path("assets/sounds")
        
        for sound_name, volume in self.sound_config.items():
            sound_path = sounds_dir / f"{sound_name}.wav"
            try:
                if sound_path.exists():
                    sound = pygame.mixer.Sound(str(sound_path))
                    sound.set_volume(volume)
                    self.sounds[sound_name] = sound
                    print(f"Loaded sound: {sound_name}")
                else:
                    print(f"Warning: Sound file not found: {sound_path}")
            except Exception as e:
                print(f"Error loading sound {sound_name}: {e}")
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if self.sound_enabled and sound_name in self.sounds:
            try:
                channel = self.sounds[sound_name].play()
                if sound_name == 'chomp':
                    # Don't play overlapping chomp sounds
                    if channel and channel.get_busy():
                        return
                elif sound_name in ['power_pellet', 'ghost_eat', 'death', 'win']:
                    # Stop any ongoing chomp sounds for important effects
                    self.stop_sound('chomp')
            except Exception as e:
                print(f"Error playing sound {sound_name}: {e}")
    
    def stop_sound(self, sound_name):
        """Stop a specific sound"""
        if sound_name in self.sounds:
            self.sounds[sound_name].stop()
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds"""
        pygame.mixer.stop()
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound_enabled = not self.sound_enabled
        if not self.sound_enabled:
            self.stop_all_sounds()
        return self.sound_enabled
    
    # In sound_manager.py, add this method
    def create_placeholder_sounds(self):
        """Create simple placeholder sounds for testing"""
        sample_rate = 44100
        duration = 0.1  # seconds
        
        # Create simple tones for each sound type
        for sound_name, frequency in {
            'chomp': 440,        # A4 note
            'power_pellet': 880,  # A5 note
            'ghost_eat': 660,    # E5 note
            'death': 220,        # A3 note
            'game_start': 550,   # C#5 note
            'win': 770          # G5 note
        }.items():
            t = numpy.linspace(0, duration, int(sample_rate * duration))
            wave = numpy.sin(2 * numpy.pi * frequency * t)
            sound_array = numpy.int16(wave * 32767)
            self.sounds[sound_name] = pygame.sndarray.make_sound(sound_array)