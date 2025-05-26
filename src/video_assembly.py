import os
import shutil
import tempfile
import random
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip,ColorClip , concatenate_videoclips , concatenate_audioclips
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---------------------------
# BACKGROUND CLIP FUNCTIONS
# ---------------------------

def download_background_clip(keywords: list, config: dict, temp_dir: str = None, index: int = 0) -> str:
    """
    Downloads a background video clip from the internet that matches the given keywords.
    
    Parameters:
      keywords (list): List of thematic keywords for the search query.
      config (dict): Configuration dictionary.
      temp_dir (str): Directory to save the downloaded video (creates a new one if None).
      index (int): Index number for the temp file name.
      
    Returns:
      str: File path to the downloaded video clip.
    """
    # Create a query string from keywords, or use a default
    query = "+".join(keywords[:3]) if keywords else "nature"
    
    # List of video sources to try - can be expanded with more sources
    video_sources = config.get("video_sources", [
        f"https://pixabay.com/api/videos/?key={config.get('pixabay_api_key', '')}&q={query}&per_page=3",
        f"https://api.pexels.com/videos/search?query={query}&per_page=3",
        "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"  # Fallback
    ])
    
    # Create temporary directory if not provided
    if temp_dir is None:
        temp_dir = tempfile.mkdtemp(prefix="background_")
    
    temp_video_path = os.path.join(temp_dir, f"background_{index}.mp4")
    
    # Try each video source until successful
    for source in video_sources:
        try:
            # If source is a direct file URL (like the fallback)
            if source.endswith('.mp4'):
                video_url = source
            # If source is an API endpoint
            elif 'pixabay.com/api' in source:
                response = requests.get(source)
                response.raise_for_status()
                data = response.json()
                if data.get('hits') and len(data['hits']) > 0:
                    random_index = random.randint(0, min(2, len(data['hits'])-1))
                    video_url = data['hits'][random_index]['videos']['medium']['url']
                else:
                    continue  # Try next source if no videos found
            elif 'pexels.com/videos' in source:
                headers = {"Authorization": config.get('pexels_api_key', '')}
                response = requests.get(source, headers=headers)
                response.raise_for_status()
                data = response.json()
                if data.get('videos') and len(data['videos']) > 0:
                    random_index = random.randint(0, min(2, len(data['videos'])-1))
                    for video_file in data['videos'][random_index]['video_files']:
                        if video_file['quality'] == 'hd' and video_file['file_type'] == 'video/mp4':
                            video_url = video_file['link']
                            break
                    else:
                        video_url = data['videos'][random_index]['video_files'][0]['link']
                else:
                    continue  # Try next source if no videos found
            else:
                continue  # Skip unknown source types
            
            # Download the video file
            logging.info(f"Downloading video from: {video_url}")
            video_response = requests.get(video_url, stream=True)
            video_response.raise_for_status()
            with open(temp_video_path, "wb") as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # If we've successfully downloaded a video, break the loop
            logging.info(f"Successfully downloaded video to {temp_video_path}")
            return temp_video_path
            
        except Exception as e:
            logging.warning(f"Failed to download video from {source}: {e}")
            continue  # Try next source
    
    # If all sources failed, raise an exception
    raise Exception("Failed to download any video from all available sources")

# This is a partial update to video_assembly.py focusing on the key changes

def preprocess_video_clip(clip_path: str, duration: float, resolution: tuple, crop_background: bool = True) -> VideoFileClip:
    """
    Prepares a video clip by trimming to desired duration and resizing.
    
    Parameters:
      clip_path (str): Path to the video file.
      duration (float): Desired duration in seconds.
      resolution (tuple): Desired resolution (width, height).
      crop_background (bool): Whether to crop the video to fill the frame (True) or stretch it (False).
      
    Returns:
      VideoFileClip: Processed video clip.
    """
    try:
        clip = VideoFileClip(clip_path)
        
        # Trim if needed
        if clip.duration > duration:
            # Take a random subclip to get some variety
            max_start = max(0, clip.duration - duration - 1)
            start_time = random.uniform(0, max_start) if max_start > 0 else 0
            clip = clip.subclip(start_time, start_time + duration)
        
        # Loop the clip if it's shorter than needed
        if clip.duration < duration:
            # Create a list of clip copies and concatenate them
            num_loops = int(duration / clip.duration) + 1
            clip_list = [clip] * num_loops
            clip = concatenate_videoclips(clip_list)
            clip = clip.subclip(0, duration)
        
        # Resize to target resolution - with cropping instead of stretching
        if crop_background:
            # Calculate the aspect ratio of the clip and the target
            clip_ratio = clip.w / clip.h
            target_ratio = resolution[0] / resolution[1]
            
            # Determine whether to crop width or height
            if clip_ratio > target_ratio:
                # Clip is wider than target, crop the width
                new_width = int(clip.h * target_ratio)
                x_center = clip.w // 2
                crop_x1 = max(0, x_center - new_width // 2)
                crop_x2 = min(clip.w, x_center + new_width // 2)
                clip = clip.crop(x1=crop_x1, x2=crop_x2)
            else:
                # Clip is taller than target, crop the height
                new_height = int(clip.w / target_ratio)
                y_center = clip.h // 2
                crop_y1 = max(0, y_center - new_height // 2)
                crop_y2 = min(clip.h, y_center + new_height // 2)
                clip = clip.crop(y1=crop_y1, y2=crop_y2)
            
            # Resize to exact dimensions
            clip = clip.resize(newsize=resolution)
        else:
            # Traditional stretch resize
            clip = clip.resize(newsize=resolution)
        
        return clip
    
    except Exception as e:
        raise Exception(f"Error processing video clip at '{clip_path}': {e}")

def assemble_video(background_clip_path: str, text_clip, voiceover_path: str, music_file: str, config: dict):
    """
    Assembles a final video using a single background clip, overlay text, voiceover, and background music.
    
    Parameters:
      background_clip_path (str): Path to a background video clip.
      text_clip: MoviePy clip for text overlay.
      voiceover_path (str): Path to the voiceover audio file.
      music_file (str): Path to the background music file.
      config (dict): Configuration dictionary.
      
    Returns:
      CompositeVideoClip: The final composite video clip.
    """
    video_duration = config.get("video_duration", 30)
    resolution = tuple(config.get("resolution", (1080, 1920)))
    crop_background = config.get("crop_background", True)
    
    try:
        # Process background clip
        background_clip = preprocess_video_clip(background_clip_path, video_duration, resolution, crop_background)
    except Exception as e:
        raise Exception(f"Error processing background clip: {e}")
    
    try:
        voiceover_audio = AudioFileClip(voiceover_path)
    except Exception as e:
        raise Exception(f"Error loading voiceover audio from '{voiceover_path}': {e}")
    
    try:
        music_volume = config.get("music_volume", 0.3)
        music_audio = music_file  # Use the already loaded and adjusted clip
        # Loop music if needed
        if music_audio.duration < video_duration:
            num_loops = int(video_duration / music_audio.duration) + 1
            music_audio = concatenate_audioclips([music_audio] * num_loops).subclip(0, video_duration)
        else:
            music_audio = music_audio.subclip(0, video_duration)
    except Exception as e:
        raise Exception(f"Error loading music file from '{music_file}': {e}")
    
    combined_audio = CompositeAudioClip([music_audio, voiceover_audio.set_start(0)])
    final_clip = CompositeVideoClip([background_clip, text_clip]).set_audio(combined_audio)
    final_clip.duration = video_duration
    return final_clip

def assemble_multi_background_video(sentence_data: list, voiceover_path: str, music_file: str, config: dict):
    """
    Assembles a video by dynamically fetching background clips for each sentence and overlaying
    corresponding text clips. The voiceover and background music are applied over the full video.
    
    Parameters:
      sentence_data (list): List of dictionaries with keys:
                            - 'text': text of the sentence
                            - 'keywords': keywords for this sentence
                            - 'duration': duration of this sentence in seconds
      voiceover_path (str): Path to the full voiceover audio file.
      music_file (str): Path to the background music file.
      config (dict): Configuration dictionary.
      
    Returns:
      CompositeVideoClip: The final composite video clip.
    """
    resolution = tuple(config.get("resolution", (1080, 1920)))
    background_segments = []
    segment_text_clips = []
    crop_background = config.get("crop_background", True)
    
    # Create a temporary directory for all downloaded clips
    temp_dir = tempfile.mkdtemp(prefix="multi_background_")
    logging.info(f"Created temporary directory: {temp_dir}")
    
    try:
        current_start = 0
        
        # Process each sentence segment
        for i, segment in enumerate(sentence_data):
            keywords = segment['keywords']
            duration = segment['duration']
            text = segment['text']
            
            # Dynamically download a background clip for this sentence
            try:
                clip_path = download_background_clip(keywords, config, temp_dir, i)
                clip = preprocess_video_clip(clip_path, duration, resolution, crop_background)
                background_segments.append(clip)
            except Exception as e:
                logging.error(f"Error fetching background for sentence {i+1}: {e}")
                # Fallback: use a solid color clip
                clip = ColorClip(resolution, color=(40, 40, 40), duration=duration)
                background_segments.append(clip)
            
            # Create a text clip for this sentence
            from moviepy.editor import TextClip
            # Apply highlights to random words if enabled
            if config.get("highlight_enabled", True):
                from visual_processing import highlight_key_words
                text = highlight_key_words(text, config.get("text_highlight_color", "#FFD700"))
            
            text_clip = TextClip(
                txt=text,
                fontsize=config.get("font_size", 90),
                font=config.get("font", "Impact"),
                color=config.get("text_color", "white"),
                stroke_color=config.get("text_outline_color", "black"),
                stroke_width=config.get("text_outline_width", 5),
                method="caption",
                size=(resolution[0] * 0.8, resolution[1] * 0.8)
            )
            
            # Position text at bottom third of the screen
            bottom_third_position = ("center", resolution[1] * 0.7)
            
            # Position and time the text clip
            text_clip = text_clip.set_position(bottom_third_position).set_start(current_start).set_duration(duration)
            segment_text_clips.append(text_clip)
            
            current_start += duration
            time.sleep(0.8) # small delay to avoid rate limiting, i get 100 calls per minute
        
        # Concatenate background clips
        full_background = concatenate_videoclips(background_segments, method="compose")
        
        # Combine all text clips into one composite
        composite_text = CompositeVideoClip(segment_text_clips, size=resolution)
        
        # Load audio components
        voiceover_audio = AudioFileClip(voiceover_path)
        music_volume = config.get("music_volume", 0.3)
        music_audio = AudioFileClip(music_file).volumex(music_volume)
        
        # Loop music if needed
        total_duration = sum(segment['duration'] for segment in sentence_data)
        if music_audio.duration < total_duration:
            num_loops = int(total_duration / music_audio.duration) + 1
            music_segments = [music_audio] * num_loops
            music_audio = concatenate_audioclips(music_segments).subclip(0, total_duration)
        else:
            music_audio = music_audio.subclip(0, total_duration)
        
        combined_audio = CompositeAudioClip([music_audio, voiceover_audio.set_start(0)])
        
        # Compose final video with spliced background and text overlay
        final_clip = CompositeVideoClip([full_background, composite_text]).set_audio(combined_audio)
        final_clip.duration = total_duration
        
        return final_clip
    
    finally:
        # Clean up temporary directory after we're done
        try:
            shutil.rmtree(temp_dir)
            logging.info(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            logging.warning(f"Failed to clean up temporary directory {temp_dir}: {e}")





def save_video(video_clip, output_path: str, fps: int = 24):
    """
    Renders and saves the final video clip to the specified output path.
    
    Parameters:
      video_clip: Composite video clip object.
      output_path (str): Destination file path for the final video.
      fps (int): Frames per second (default 24).
    """
    video_clip.write_videofile(output_path, fps=fps)