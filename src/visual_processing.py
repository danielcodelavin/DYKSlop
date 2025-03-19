"""
visual_processing.py

This module handles visual content processing.
It provides functions for selecting a background clip based on thematic keywords
and for creating a text overlay clip using MoviePy.
Each function defines its own default settings (hyperparameters) at the top for easy tweaking.
"""

import os
import random
from moviepy.editor import TextClip

def select_background(keywords: list, config: dict) -> str:
    """
    Selects a background video clip file path that best matches one of the provided keywords.

    Hyperparameters / Assumptions:
        DEFAULT_BACKGROUNDS_DIR = "assets/backgrounds/"  # Default directory for background clips.
        A file is considered a match if any keyword (case-insensitive) appears in its filename.
    
    Parameters:
        keywords (list): List of extracted thematic keywords.
        config (dict): Configuration dictionary; may contain "backgrounds_dir".
        
    Returns:
        str: Full file path to the selected background clip.
    """
    # Define the backgrounds directory.
    backgrounds_dir = config.get("backgrounds_dir", "assets/backgrounds/")
    
    try:
        background_files = os.listdir(backgrounds_dir)
    except FileNotFoundError:
        raise Exception(f"Background directory '{backgrounds_dir}' not found.")
    
    # Filter files that contain any of the keywords in their filenames.
    matching_files = []
    for file in background_files:
        file_lower = file.lower()
        for keyword in keywords:
            if keyword.lower() in file_lower:
                matching_files.append(file)
                break  # Stop checking further keywords if one matches.
    
    # If no file matches, choose a random file.
    selected_file = random.choice(matching_files) if matching_files else random.choice(background_files)
    
    return os.path.join(backgrounds_dir, selected_file)

def create_text_clip(text: str, config: dict):
    """
    Creates a text overlay clip using MoviePy's TextClip.

    Hyperparameters / Defaults (if not provided in config):
        DEFAULT_FONT = "Arial-Bold.ttf"
        DEFAULT_FONT_SIZE = 70
        DEFAULT_TEXT_COLOR = "white"
        DEFAULT_TEXT_POSITION = "center"  # Can also be a tuple (e.g., ("center", "top"))
        DEFAULT_VIDEO_DURATION = 30       # Duration in seconds.
        DEFAULT_RESOLUTION = (1080, 1920)   # Width x Height.
    
    Parameters:
        text (str): The text to display.
        config (dict): Configuration dictionary with keys like "font", "font_size", "text_color",
                       "text_position", "video_duration", and "resolution".
                       
    Returns:
        TextClip: A MoviePy TextClip object with the specified styling and duration.
    """
    # Define default settings.
    DEFAULT_FONT = "Arial-Bold.ttf"
    DEFAULT_FONT_SIZE = 70
    DEFAULT_TEXT_COLOR = "white"
    DEFAULT_TEXT_POSITION = "center"
    DEFAULT_VIDEO_DURATION = 30
    DEFAULT_RESOLUTION = (1080, 1920)
    
    # Retrieve values from config (with defaults).
    font = config.get("font", DEFAULT_FONT)
    font_size = config.get("font_size", DEFAULT_FONT_SIZE)
    text_color = config.get("text_color", DEFAULT_TEXT_COLOR)
    text_position = config.get("text_position", DEFAULT_TEXT_POSITION)
    video_duration = config.get("video_duration", DEFAULT_VIDEO_DURATION)
    resolution = tuple(config.get("resolution", DEFAULT_RESOLUTION))
    
    # Create the text clip using the "caption" method for word wrapping.
    text_clip = TextClip(txt=text,
                         fontsize=font_size,
                         font=font,
                         color=text_color,
                         method="caption",
                         size=resolution)
    # Set the duration and position of the text overlay.
    text_clip = text_clip.set_duration(video_duration).set_position(text_position)
    
    return text_clip