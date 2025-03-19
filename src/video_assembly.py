import os
import tempfile
import random
import requests
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip

def download_background_clip(keywords: list, config: dict) -> str:
    """
    Downloads a background video clip from the internet that matches the given keywords.
    For demonstration purposes, this function downloads a sample video from a preset URL.
    In production, you could integrate with a video search API (e.g., Pexels, Pixabay) using the keywords.

    Hyperparameters / Assumptions:
        - DEFAULT_SAMPLE_VIDEO_URL: URL of the fallback video.
          (Default: "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4")
        - The video will be trimmed to the duration specified in config["video_duration"].

    Parameters:
        keywords (list): List of thematic keywords (currently not used for dynamic query).
        config (dict): Configuration dictionary with at least "video_duration".

    Returns:
        str: File path to the downloaded (and trimmed) background video clip.
    """
    DEFAULT_SAMPLE_VIDEO_URL = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
    video_url = config.get("sample_background_url", DEFAULT_SAMPLE_VIDEO_URL)

    # Create a temporary directory for the background clip.
    temp_dir = tempfile.mkdtemp(prefix="background_")
    temp_video_path = os.path.join(temp_dir, "background.mp4")
    
    # Download the video from the URL.
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(temp_video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        raise Exception(f"Failed to download background video from {video_url}: {e}")
    
    # Trim the video to the desired duration.
    video_duration = config.get("video_duration", 30)
    try:
        clip = VideoFileClip(temp_video_path)
        if clip.duration > video_duration:
            trimmed_clip = clip.subclip(0, video_duration)
            # Overwrite the temporary file with the trimmed version.
            trimmed_clip.write_videofile(temp_video_path, fps=clip.fps, codec="libx264", audio_codec="aac", verbose=False, logger=None)
            trimmed_clip.close()
        clip.close()
    except Exception as e:
        raise Exception(f"Error trimming background video: {e}")

    return temp_video_path

def get_background_clip(keywords: list, config: dict) -> str:
    """
    Selects a background clip from a local directory if available. If the directory does not exist
    or is empty, it falls back to dynamically downloading a background clip.

    Hyperparameters / Assumptions:
        - backgrounds_dir is defined in the config (default: "assets/backgrounds/").
        - If backgrounds_dir exists and contains files, select one based on keywords (case-insensitive match).
        - If no files match or the directory is missing/empty, call download_background_clip().

    Parameters:
        keywords (list): List of thematic keywords for matching.
        config (dict): Configuration dictionary with keys such as "backgrounds_dir" and "video_duration".

    Returns:
        str: File path to the selected or downloaded background video clip.
    """
    backgrounds_dir = config.get("backgrounds_dir", "assets/backgrounds/")
    
    # Check if the local backgrounds directory exists and is not empty.
    if os.path.exists(backgrounds_dir):
        try:
            background_files = os.listdir(backgrounds_dir)
        except Exception as e:
            raise Exception(f"Error reading backgrounds directory '{backgrounds_dir}': {e}")
        # Filter for video files (simple check: endswith .mp4, .mov, etc.)
        video_files = [file for file in background_files if file.lower().endswith(('.mp4', '.mov', '.avi'))]
        if video_files:
            # Look for files matching any of the keywords.
            matching_files = []
            for file in video_files:
                file_lower = file.lower()
                for keyword in keywords:
                    if keyword.lower() in file_lower:
                        matching_files.append(file)
                        break  # Found a match for this file.
            # Select a file: if matching files exist, use them; otherwise, choose a random video.
            selected_file = random.choice(matching_files) if matching_files else random.choice(video_files)
            return os.path.join(backgrounds_dir, selected_file)
        else:
            # Directory exists but contains no video files.
            print(f"Warning: Backgrounds directory '{backgrounds_dir}' is empty. Downloading fallback video.")
    else:
        print(f"Warning: Backgrounds directory '{backgrounds_dir}' not found. Downloading fallback video.")
    
    # Fallback: download a background video clip.
    return download_background_clip(keywords, config)

def assemble_video(background_clip_path: str, text_clip, voiceover_path: str, music_file: str, config: dict):
    """
    Assembles the final video by layering the background clip, text overlay, and combining the voiceover with background music.

    Parameters:
        background_clip_path (str): File path to the background video clip.
        text_clip: A MoviePy clip object containing the text overlay.
        voiceover_path (str): File path to the generated voiceover audio.
        music_file (str): File path to the background music file.
        config (dict): Configuration dictionary with keys like "video_duration", "resolution", and "music_volume".

    Returns:
        CompositeVideoClip: The final composite video clip.
    """
    video_duration = config.get("video_duration", 30)
    resolution = tuple(config.get("resolution", (1080, 1920)))
    
    # Load and trim the background clip.
    try:
        background_clip = VideoFileClip(background_clip_path).subclip(0, video_duration)
        background_clip = background_clip.resize(newsize=resolution)
    except Exception as e:
        raise Exception(f"Error processing background clip at '{background_clip_path}': {e}")
    
    # Load audio components.
    try:
        voiceover_audio = AudioFileClip(voiceover_path)
    except Exception as e:
        raise Exception(f"Error loading voiceover audio from '{voiceover_path}': {e}")
    
    try:
        music_volume = config.get("music_volume", 0.3)
        music_audio = AudioFileClip(music_file).volumex(music_volume)
    except Exception as e:
        raise Exception(f"Error loading music file from '{music_file}': {e}")
    
    # Combine audio tracks.
    combined_audio = CompositeAudioClip([music_audio, voiceover_audio.set_start(0)])
    
    # Create final composite clip.
    final_clip = CompositeVideoClip([background_clip, text_clip])
    final_clip = final_clip.set_audio(combined_audio)
    final_clip.duration = video_duration
    return final_clip

def save_video(video_clip, output_path: str, fps: int = 24):
    """
    Renders and saves the final video clip to the specified output path.

    Parameters:
        video_clip: The composite video clip object to be saved.
        output_path (str): Destination file path for the final video.
        fps (int): Frames per second for the final video (default is 24).
    """
    video_clip.write_videofile(output_path, fps=fps)