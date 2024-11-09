import numpy as np
import wave
import struct
import os

def generate_test_sound(filename, frequency, duration=0.2):
    """Generate a simple test sound wave file"""
    # Parameters
    sample_rate = 44100
    amplitude = 32767
    num_samples = int(sample_rate * duration)
    
    # Generate samples
    t = np.linspace(0, duration, num_samples)
    samples = amplitude * np.sin(2.0 * np.pi * frequency * t)
    
    # Convert to integer format
    samples = samples.astype(np.int16)
    
    # Create WAV file
    with wave.open(filename, 'w') as wav_file:
        # Set parameters
        nchannels = 1
        sampwidth = 2
        
        # Set WAV file parameters
        wav_file.setnchannels(nchannels)
        wav_file.setsampwidth(sampwidth)
        wav_file.setframerate(sample_rate)
        
        # Write the samples
        for sample in samples:
            wav_file.writeframes(struct.pack('h', sample))

def main():
    # Create sounds directory if it doesn't exist
    os.makedirs('assets/sounds', exist_ok=True)
    
    # Generate test sounds with different frequencies
    sounds = {
        'chomp': 440,        # A4
        'power_pellet': 880, # A5
        'ghost_eat': 660,    # E5
        'death': 220,        # A3
        'game_start': 550,   # C#5
        'win': 770          # G5
    }
    
    for name, freq in sounds.items():
        filename = f'assets/sounds/{name}.wav'
        generate_test_sound(filename, freq)
        print(f"Generated {filename}")

if __name__ == "__main__":
    main()