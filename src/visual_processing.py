"""
visual_processing.py

This module handles visual content processing.
It provides functions for selecting background clips based on thematic keywords
and for creating text overlay clips using MoviePy.
"""

import os
import logging
from moviepy.editor import TextClip, ColorClip
from moviepy.video.tools.subtitles import SubtitlesClip
import nltk
import nltk.corpus
import re
import random
from typing import List, Dict, Tuple, Any

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Download necessary NLTK data on first import
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

def select_background(keywords: list, config: dict) -> str:
    """
    This function is now just a wrapper for the download_background_clip function
    in video_assembly.py. It's kept for backwards compatibility.
    
    Parameters:
        keywords (list): List of extracted thematic keywords.
        config (dict): Configuration dictionary.
        
    Returns:
        str: Full file path to the downloaded background clip.
    """
    from video_assembly import download_background_clip
    return download_background_clip(keywords, config)

def create_text_clip(text: str, config: dict):
    """
    Creates a text overlay clip using MoviePy's TextClip with enhanced styling.
    
    Parameters:
        text (str): The text to display.
        config (dict): Configuration dictionary with styling parameters.
                       
    Returns:
        TextClip: A MoviePy TextClip object with the specified styling and duration.
    """
    # Define styling settings
    font = config.get("font", "Impact")  # Updated to Impact as default
    font_size = config.get("font_size", 90)  # Increased font size
    text_color = config.get("text_color", "white")
    text_outline_color = config.get("text_outline_color", "black")
    text_outline_width = config.get("text_outline_width", 5)
    video_duration = config.get("video_duration", 30)
    resolution = tuple(config.get("resolution", (1080, 1920)))
    
    # Apply highlights to random words if enabled
    if config.get("highlight_enabled", True):
        text = highlight_key_words(text, config.get("text_highlight_color", "#FFD700"))
    
    # Create the text clip with stroke (outline)
    text_clip = TextClip(
        txt=text,
        fontsize=font_size,
        font=font,
        color=text_color,
        stroke_color=text_outline_color,
        stroke_width=text_outline_width,
        method="caption",
        size=(resolution[0] * 0.9, resolution[1] * 0.5)  # Increased width for better text fitting
    )
    
    # Position at bottom third of the screen
    bottom_third_position = ("center", resolution[1] * 0.7)
    
    # Set the duration and position of the text overlay
    text_clip = text_clip.set_duration(video_duration).set_position(bottom_third_position)
    
    return text_clip

def highlight_key_words(text: str, highlight_color: str) -> str:
    """
    Randomly highlights 1-2 key nouns/verbs in the text with a different color.
    
    Parameters:
        text (str): The text to process.
        highlight_color (str): The color to use for highlighting.
        
    Returns:
        str: Text with HTML color tags for highlighted words.
    """
    # Split the text into words
    words = text.split()
    
    # Filter out short words and common words
    common_words = {"the", "and", "a", "an", "in", "on", "at", "to", "for", "of", "with", "by", "as", "is", "are", "was", "were"}
    candidate_words = [i for i, word in enumerate(words) if len(word) > 3 and word.lower() not in common_words]
    
    # Choose 1-2 random words to highlight
    num_to_highlight = min(len(candidate_words), random.randint(1, 2))
    if num_to_highlight == 0:
        return text
    
    indices_to_highlight = random.sample(candidate_words, num_to_highlight)
    
    # Apply HTML color tags to the selected words
    for idx in sorted(indices_to_highlight, reverse=True):
        words[idx] = f'<font color="{highlight_color}">{words[idx]}</font>'
    
    return " ".join(words)

def split_text_into_word_chunks(text: str, max_words_per_chunk: int = 5) -> List[str]:
    """
    Splits text into chunks of maximum words per chunk.
    
    Parameters:
        text (str): The text to split.
        max_words_per_chunk (int): Maximum number of words per chunk.
        
    Returns:
        List[str]: List of text chunks.
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_words_per_chunk):
        chunk = " ".join(words[i:i + max_words_per_chunk])
        chunks.append(chunk)
    
    return chunks

def split_text_into_sentences(text: str) -> list:
    """
    Splits the input text into sentences using NLTK.
    
    Parameters:
        text (str): The text to split into sentences.
        
    Returns:
        list: List of sentences.
    """
    return nltk.sent_tokenize(text)

def extract_sentence_keywords(sentence: str, num_keywords: int = 3) -> list:
    """
    Extracts keywords from a sentence by removing stopwords and keeping the most relevant words.
    
    Parameters:
        sentence (str): The sentence to extract keywords from.
        num_keywords (int): Number of keywords to extract.
        
    Returns:
        list: List of extracted keywords.
    """
    # Try to download stopwords if not already available
    try:
        from nltk.corpus import stopwords
        stop_words = set(stopwords.words('english'))
    except:
        try:
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            stop_words = set(stopwords.words('english'))
        except:
            # Fallback to a simple list of common stopwords
            stop_words = {'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
                         'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
                         'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
                         'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
                         'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
                         'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                         'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                         's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'i', 'me', 'my',
                         'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
                         'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her',
                         'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs',
                         'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these',
                         'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
                         'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the',
                         'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while'}
    
    # Remove punctuation and convert to lowercase
    clean_sentence = re.sub(r'[^\w\s]', '', sentence.lower())
    
    # Split into words and remove stopwords
    words = clean_sentence.split()
    filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
    
    # Return the most frequent/important words
    # This is a simple approach; more sophisticated NLP techniques could be used
    word_freq = {}
    for word in filtered_words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [word for word, freq in sorted_words[:num_keywords]]
    
    # If we don't have enough keywords, return what we have
    return keywords if keywords else ["nature"]  # Default fallback

def estimate_sentence_duration(sentence: str, words_per_second: float = 2.5) -> float:
    """
    Estimates the duration needed to speak a sentence based on word count.
    
    Parameters:
        sentence (str): The sentence to estimate duration for.
        words_per_second (float): Average speaking rate.
        
    Returns:
        float: Estimated duration in seconds.
    """
    # Split the sentence into words and count them
    words = re.findall(r'\w+', sentence)
    word_count = len(words)
    
    # Calculate duration with a minimum of 2 seconds
    duration = max(word_count / words_per_second, 2.0)
    
    return duration

def prepare_sentence_data(fact_text: str, config: dict) -> list:
    """
    Prepares data for each sentence including text, keywords, and estimated duration.
    
    Parameters:
        fact_text (str): The full fact text to be processed.
        config (dict): Configuration dictionary.
        
    Returns:
        list: List of dictionaries with data for each sentence.
    """
    sentences = split_text_into_sentences(fact_text)
    sentence_data = []
    
    for sentence in sentences:
        keywords = extract_sentence_keywords(sentence)
        duration = estimate_sentence_duration(sentence, config.get("words_per_second", 2.5))
        
        # Split text into 5-word chunks for progressive display
        chunks = split_text_into_word_chunks(
            sentence, 
            config.get("max_words_per_segment", 5)
        )
        
        # Calculate duration for each chunk
        chunk_duration = duration / len(chunks) if chunks else duration
        
        # Create data for each chunk
        for chunk in chunks:
            sentence_data.append({
                'text': chunk,
                'keywords': keywords,
                'duration': chunk_duration
            })
    
    return sentence_data

def create_dynamic_text_clips(sentence_data: list, config: dict) -> list:
    """
    Creates text clips for each sentence chunk with transitions.
    
    Parameters:
        sentence_data (list): List of dictionaries with sentence data.
        config (dict): Configuration dictionary.
        
    Returns:
        list: List of TextClip objects.
    """
    resolution = tuple(config.get("resolution", (1080, 1920)))
    font = config.get("font", "Impact")
    font_size = config.get("font_size", 90)
    text_color = config.get("text_color", "white")
    text_outline_color = config.get("text_outline_color", "black")
    text_outline_width = config.get("text_outline_width", 5)
    highlight_color = config.get("text_highlight_color", "#FFD700")
    
    text_clips = []
    current_time = 0
    
    for segment in sentence_data:
        text = segment['text']
        duration = segment['duration']
        
        # Apply highlighting to random words
        if config.get("highlight_enabled", True):
            text = highlight_key_words(text, highlight_color)
        
        # Create text clip with outline
        text_clip = TextClip(
            txt=text,
            fontsize=font_size,
            font=font,
            color=text_color,
            stroke_color=text_outline_color,
            stroke_width=text_outline_width,
            method="caption",
            size=(resolution[0] * 0.9, resolution[1] * 0.5)
        )
        
        # Position at bottom third of the screen
        bottom_third_position = ("center", resolution[1] * 0.7)
        
        # Set position, timing, and add fade effects
        text_clip = (text_clip
                    .set_position(bottom_third_position)
                    .set_start(current_time)
                    .set_duration(duration)
                    .crossfadein(0.3)
                    .crossfadeout(0.3))
        
        text_clips.append(text_clip)
        current_time += duration
    
    return text_clips