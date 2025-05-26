"""
audio_processing.py

This module handles all audio-related processing.
It provides functions for generating a voiceover using gTTS and for loading background music.
All tweakable parameters (hyperparameters) are defined in one block at the start of each function.
"""

from gtts import gTTS
from moviepy.editor import AudioFileClip
import numpy as np
from pydub import AudioSegment
from pydub.silence import detect_nonsilence

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

def analyze_voiceover_timing(voiceover_path: str, text: str, min_silence_len=100):
    """
    Analyzes the voiceover audio to map word timings.
    
    Parameters:
        voiceover_path (str): Path to the voiceover audio file.
        text (str): The text of the voiceover.
        min_silence_len (int): Minimum silence length in milliseconds to consider as a pause.
        
    Returns:
        list: A list of segments with their start and end times.
    """
    # Load the audio file
    audio = AudioSegment.from_file(voiceover_path)
    
    # Detect non-silent chunks
    # Parameters can be adjusted based on your specific audio characteristics
    non_silent_ranges = detect_nonsilence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=-40  # dB below which is considered silence
    )
    
    # Convert milliseconds to seconds
    non_silent_ranges = [(start/1000, end/1000) for start, end in non_silent_ranges]
    
    # Split the text into segments
    words = text.split()
    segments = []
    
    # If we have very few non-silent ranges, use a simple approach
    if len(non_silent_ranges) < len(words) / 2:
        # Fallback method: divide the audio duration by the number of segments
        from visual_processing import split_text_into_word_chunks
        chunks = split_text_into_word_chunks(text)
        
        total_duration = audio.duration_seconds
        segment_duration = total_duration / len(chunks)
        
        for i, chunk in enumerate(chunks):
            start_time = i * segment_duration
            end_time = (i + 1) * segment_duration
            segments.append({
                'text': chunk,
                'start': start_time,
                'end': end_time,
                'duration': segment_duration
            })
    else:
        # More sophisticated approach: map words to audio segments
        chunks = []
        current_chunk = []
        word_count = 0
        
        for word in words:
            current_chunk.append(word)
            word_count += 1
            
            if word_count == 5 or word.endswith(('.', '!', '?')):
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                word_count = 0
        
        # Add any remaining words
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        # Map chunks to audio segments
        chunk_count = len(chunks)
        audio_segment_count = len(non_silent_ranges)
        
        # Distribute non-silent ranges among chunks
        chunk_timings = []
        
        if chunk_count <= audio_segment_count:
            # Simple 1:1 mapping if we have enough audio segments
            for i in range(chunk_count):
                chunk_timings.append(non_silent_ranges[i])
        else:
            # Combine adjacent non-silent ranges if we have more chunks than audio segments
            ratio = chunk_count / audio_segment_count
            for i in range(chunk_count):
                audio_idx = int(i / ratio)
                audio_idx = min(audio_idx, audio_segment_count - 1)
                chunk_timings.append(non_silent_ranges[audio_idx])
        
        # Create segments
        for i, chunk in enumerate(chunks):
            start_time, end_time = chunk_timings[i]
            segments.append({
                'text': chunk,
                'start': start_time,
                'end': end_time,
                'duration': end_time - start_time
            })
    
    return segments