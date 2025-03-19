"""
audio_processing.py

This module handles all audio-related processing.
It provides functions for generating a voiceover using gTTS and for loading background music.
All tweakable parameters (hyperparameters) are defined in one block at the start of each function.
"""

from gtts import gTTS
from moviepy.editor import AudioFileClip

def generate_voiceover(text: str, lang: str = "en", output_path: str = "voiceover.mp3", slow: bool = False) -> str:
    """
    Generates a voiceover audio file from text using Google Text-to-Speech (gTTS).

    Hyperparameters / Assumptions:
        DEFAULT_LANG = "en"      # Default language for TTS.
        DEFAULT_SLOW = False     # Speak at normal speed by default.
    
    Parameters:
        text (str): The text to convert into speech.
        lang (str): Language code for the voiceover (e.g., "en"). Default is "en".
        output_path (str): File path to save the generated audio.
        slow (bool): Whether the speech should be slow. Default is False.
        
    Returns:
        str: The path to the saved voiceover audio file.
    """
    # Create a gTTS object with the provided parameters.
    tts = gTTS(text=text, lang=lang, slow=slow)
    # Save the generated audio to output_path.
    tts.save(output_path)
    return output_path

def load_music(music_path: str, volume: float = 0.3):
    """
    Loads a background music track from a file, applies a volume adjustment, and returns an AudioFileClip.
    
    Hyperparameters / Assumptions:
        DEFAULT_MUSIC_VOLUME = 0.3  # Default volume multiplier for the background music.
    
    Parameters:
        music_path (str): The file path to the music file.
        volume (float): The volume multiplier to apply. Default is 0.3.
        
    Returns:
        AudioFileClip: An audio clip object with adjusted volume.
    """
    # Load the music file as an AudioFileClip.
    music_clip = AudioFileClip(music_path)
    # Adjust the volume.
    music_clip = music_clip.volumex(volume)
    return music_clip