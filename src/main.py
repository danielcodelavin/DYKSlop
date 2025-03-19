import os
import json
import argparse

# Import functions from the other modules (to be implemented separately)
from fact_retrieval import get_fact, extract_keywords
from audio_processing import generate_voiceover, load_music
from visual_processing import select_background, create_text_clip
from video_assembly import assemble_video, save_video

def load_config(config_path: str) -> dict:
    """
    Loads the configuration from a JSON file.
    """
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def main():
    # Parse command-line arguments to override certain hyperparameters.
    
    config = 'config.json'
    output_dir = './output/'
    video_duration = 60 # seconds
    # You can add more command-line hyperparameters as needed.
    

    # Load configuration from file
    config = load_config(config)

    # Override config parameters with any hyperparameters provided on the command line.
    if video_duration is not None:
        config['video_duration'] = video_duration

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # === Stage 1: Fact Retrieval and Processing ===
    # Retrieve a fact using the API URL specified in the config (a string)
    fact_text: str = get_fact(config['api_url'])
    # Extract key thematic words from the fact for visual matching (returns a list of strings)
    keywords: list = extract_keywords(fact_text)

    # === Stage 2: Audio Generation and Music Loading ===
    # Generate voiceover audio from the fact text.
    # The function returns a file path (string) where the audio is saved.
    voiceover_path: str = generate_voiceover(
        text=fact_text,
        lang=config.get("audio_language", "en"),
        output_path=os.path.join(output_dir, "voiceover.mp3")
    )
    # Load the background music file and set its volume.
    # This function should return either an audio file path or an audio clip object.
    music_file = load_music(
        music_path=config["background_music"],
        volume=config.get("music_volume", 0.3)
    )

    # === Stage 3: Visual Content and Thematic Matching ===
    # Select a background video clip that matches the theme, based on extracted keywords.
    # The function returns a file path to the selected background clip.
    background_clip_path: str = select_background(keywords, config)
    # Create a text overlay clip (e.g., using MoviePy's TextClip) that displays a header and the fact.
    # The function returns a video clip object.
    text_clip = create_text_clip(
        text="Did You Know?\n" + fact_text,
        config=config
    )
    video_name = fact_text[:20].replace(' ', '_')
    video_name = video_name.replace('?', '')
    video_name = video_name.replace('!', '')
    video_name = video_name.replace('.', '')
    video_name = video_name.replace(',', '')
    video_name = video_name.replace(':', '')
    video_name = video_name.replace(';', '')
    video_name = video_name.replace('(', '')
    video_name = video_name.replace(')', '')
    

    # === Stage 4: Video Assembly ===
    # Combine the background clip, text overlay, voiceover, and background music.
    # The assemble_video function is expected to return a final composite video clip (e.g., a MoviePy CompositeVideoClip).
    final_video_clip = assemble_video(
        background_clip_path=background_clip_path,
        text_clip=text_clip,
        voiceover_path=voiceover_path,
        music_file=music_file,
        config=config
    )

    # Define the output filename for the final video, e.g., "viral_fact_video.mp4".
    output_filename = os.path.join(output_dir, video_name + ".mp4")

    # === Stage 5: Output ===
    # Save the final assembled video to the specified output folder.
    save_video(
        video_clip=final_video_clip,
        output_path=output_filename,
        fps=config.get("fps", 32)
    )

    print("Video successfully generated and saved to:", output_filename)

if __name__ == "__main__":
    main()