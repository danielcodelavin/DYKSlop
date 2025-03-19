# Did You Know? Viral Fact Video Generator

## Table of Contents
- [Project Overview](#project-overview)
- [Assumptions and Goals](#assumptions-and-goals)
- [Architecture and Data Flow](#architecture-and-data-flow)
- [Directory Structure](#directory-structure)
- [Configuration](#configuration)
- [Modules and Their Responsibilities](#modules-and-their-responsibilities)
  - [main.py](#mainpy)
  - [fact_retrieval.py](#fact_retrievalpy)
  - [audio_processing.py](#audio_processingpy)
  - [visual_processing.py](#visual_processingpy)
  - [video_assembly.py](#video_assemblypy)
- [Dependencies](#dependencies)
- [Installation and Setup](#installation-and-setup)
- [Usage Instructions](#usage-instructions)
- [Customization and Hyperparameters](#customization-and-hyperparameters)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Project Overview

This project is designed to generate short, engaging “Did You Know?” videos optimized for platforms like TikTok and Instagram Shorts. Each video presents an interesting fact using dynamic visuals, text overlays, AI-generated voiceover, and background music. The system is fully automated in Python with a modular, function-based architecture (no classes), ensuring ease of maintenance and extensibility.

**Key Features:**
- **Fact Retrieval:** Fetches a fact from an external API (or local database).
- **Thematic Visual Matching:** Extracts keywords from the fact and selects a background video clip that matches the theme for each sentence. Multiple short clips are spliced together based on the timing of different sentences.
- **Voiceover Generation:** Converts the fact text into speech via a TTS engine.
- **Background Music Integration:** Loads and adjusts the volume of background music.
- **Text Overlay Creation:** Generates dynamic text overlays for each sentence.
- **Video Assembly:** Merges multiple background clips (one per sentence) with corresponding text overlays and audio into a final video.
- **Automated Downloads:** If local background assets are insufficient, the system will automatically download stock videos matching the thematic keywords to splice together.
- **Configurability:** All parameters are managed via a configuration file, with options to override via command-line arguments.

---

## Assumptions and Goals

- **Engagement Focus:**  
  Videos must capture attention within the first 3 seconds and maintain viewer interest throughout by aligning visuals with each sentence’s content (e.g., “he was sent to prison” paired with a stock clip of someone entering a prison).

- **Modularity and Simplicity:**  
  The project is divided into small, function-based modules—each handling a distinct task (fact retrieval, audio processing, visual processing, video assembly)—for clarity and ease of debugging.

- **Dynamic and Thematic Visuals:**  
  Background visuals are not static; the system is designed to automatically download multiple short clips that match the thematic keywords extracted from different sentences, then splice them together in a sequence.

- **Configurability and Reproducibility:**  
  All parameters (video duration, resolution, fonts, volume levels, etc.) are stored in a JSON configuration file (without comments, as standard JSON does not allow them). This file, along with command-line arguments, controls the behavior of the video generator.

- **Minimal External Dependencies:**  
  The solution leverages widely used libraries (e.g., `requests`, `gTTS`, `moviepy`, `Pillow`) for stability and ease of installation.

---

## Architecture and Data Flow

1. **Input Stage:**
   - **Seed/Keyword Input:** A user-provided seed or keyword initializes the process.
   - **Fact Retrieval:** A fact is fetched via an API using the URL provided in the configuration.

2. **Processing Stage:**
   - **Keyword Extraction:** Simple NLP extracts key terms from the fact text.
   - **Sentence Segmentation:** The fact is split into sentences to determine timing for splicing different background clips.
   - **Voiceover Generation:** The TTS engine converts the entire fact (or each sentence, if desired) into audio narration.
   - **Visual Matching:** For each sentence, the system uses the extracted keywords to select (or automatically download) a background video clip that is thematically appropriate.
   - **Text Overlay Creation:** For each sentence, a text overlay clip is created with dynamic styling.

3. **Assembly Stage:**
   - **Splicing Backgrounds:** Multiple background clips are trimmed to match the duration of their corresponding sentence segments.
   - **Audio & Visual Synchronization:** The clips are spliced together in sequence, with the text overlays and voiceover synchronized to the timeline.
   - **Audio Integration:** The background music and voiceover are mixed, with configurable volume controls.

4. **Output Stage:**
   - **Rendering:** The composite video is rendered as an MP4 file.
   - **Logging:** Metadata (fact text, keywords, selected assets, configuration parameters) is logged for reproducibility.

---

## Directory Structure

/viral_fact_videos
│
├── assets/
│   ├── backgrounds/       # Local background video clips/images (optional)
│   └── music/             # Background music files
│
├── output/                # Generated videos and logs
│
├── config.json            # Configuration file (parameters for the project)
├── main.py                # Main script that orchestrates the process
├── fact_retrieval.py      # Module for retrieving and processing facts
├── audio_processing.py    # Module for audio generation and processing
├── visual_processing.py   # Module for selecting backgrounds and creating text overlays
├── video_assembly.py      # Module for assembling, splicing, and saving the final video
└── README.md              # This detailed documentation file

---

## Configuration

The `config.json` file defines all adjustable parameters. Although JSON does not allow comments, below are explanations for each parameter:

- **video_duration:** Duration of the final video in seconds.
- **resolution:** Array `[width, height]` defining the output video resolution.
- **font:** Font file name (or path) for text overlays.
- **font_size:** Font size (in points) for the text overlays.
- **text_color:** Color of the text overlays (e.g., "white" or "#FFFFFF").
- **text_position:** Position for text overlays (e.g., "center", "top", "bottom", or coordinates).
- **transition_duration:** Duration (in seconds) for transition effects between segments.
- **audio_language:** Language code for the TTS engine (e.g., "en").
- **api_url:** API endpoint URL to fetch a fact.
- **background_music:** File path to the background music track.
- **backgrounds_dir:** Directory for local background clips/images.
- **music_volume:** Volume multiplier for background music (e.g., 0.3 means 30% volume).
- **fps:** Frames per second for the final video.
- **sample_background_url:** (Optional) A fallback URL for downloading a background clip if no local clip is available.

Example `config.json` (without comments):
```json
{
  "video_duration": 30,
  "resolution": [1080, 1920],
  "font": "Arial-Bold.ttf",
  "font_size": 70,
  "text_color": "white",
  "text_position": "center",
  "transition_duration": 1.5,
  "audio_language": "en",
  "api_url": "http://numbersapi.com/random/trivia",
  "background_music": "assets/music/trending.mp3",
  "backgrounds_dir": "assets/backgrounds/",
  "music_volume": 0.3,
  "fps": 24,
  "sample_background_url": "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
}



⸻

Modules and Their Responsibilities

main.py
	•	Role: Orchestrates the entire workflow.
	•	Operations:
	•	Loads configuration from config.json and applies command-line overrides.
	•	Retrieves fact and extracts keywords.
	•	Splits fact text into sentences (for background splicing).
	•	Generates voiceover.
	•	Uses get_background_clip (from visual_processing) to select or download background clips per sentence.
	•	Creates text overlays for each sentence.
	•	Calls functions in video_assembly.py to splice all background clips, align them with overlays and audio, and produce the final video.
	•	Saves the final video to a specified output directory.

fact_retrieval.py
	•	Role: Retrieves a fact from an API and extracts thematic keywords.
	•	Functions:
	•	get_fact(api_url: str) -> str
	•	extract_keywords(fact_text: str) -> list

audio_processing.py
	•	Role: Generates audio components.
	•	Functions:
	•	generate_voiceover(text: str, lang: str, output_path: str, slow: bool) -> str
	•	load_music(music_path: str, volume: float)

visual_processing.py
	•	Role: Handles visual asset processing.
	•	Functions:
	•	select_background(keywords: list, config: dict) -> str
	•	Note: In our new design, this function is now extended by get_background_clip to dynamically download clips if necessary.
	•	get_background_clip(keywords: list, config: dict) -> str
	•	create_text_clip(text: str, config: dict)
	•	Additional Processing: (Potentially splitting the fact into sentences and matching each sentence to a clip – either done here or in main.py)

video_assembly.py
	•	Role: Assembles the final video.
	•	Functions:
	•	download_background_clip(keywords: list, config: dict) -> str
	•	Downloads a stock video from the internet as a fallback.
	•	assemble_video(background_clip_path: str, text_clip, voiceover_path: str, music_file: str, config: dict)
	•	Layers the background clip, text overlay, voiceover, and music.
	•	save_video(video_clip, output_path: str, fps: int)
	•	New Addition: Ability to splice together multiple background clips corresponding to each sentence.
	•	The main script should gather a list of background clip paths (one per sentence) and a list of corresponding text overlays, then call a new function (or extend assemble_video) to splice them together sequentially.

⸻

Dependencies

The project depends on:
	•	requests – for HTTP requests (fact retrieval and video downloads).
	•	gTTS – for text-to-speech voiceover generation.
	•	moviepy – for video editing, splicing, and assembly.
	•	Pillow – for any image processing (if needed).
	•	numpy – for randomization and numerical operations.
	•	argparse – for command-line argument parsing.
	•	Standard modules: os, json, random, tempfile.

Install them via pip:

pip install requests gTTS moviepy Pillow numpy

Note: MoviePy requires FFmpeg to be installed and in your system PATH.

⸻

Installation and Setup
	1.	Clone the Repository:
Download all files (main.py, fact_retrieval.py, audio_processing.py, visual_processing.py, video_assembly.py, config.json, etc.) into a project folder.
	2.	Prepare Assets:
	•	Create an assets folder with subfolders:
	•	backgrounds/ for local background clips (optional; if absent or empty, fallback download is used).
	•	music/ for background music files.
	•	Place your desired stock video clips and music files accordingly.
	3.	Configure the Project:
	•	Edit config.json with your desired parameters.
	•	Ensure file paths are correct relative to your project structure.
	4.	Install Dependencies:
Run the pip install command above. Also, ensure FFmpeg is installed and configured.

⸻

Usage Instructions
	•	Run the Main Script:
In the terminal, navigate to your project root and run:

python main.py --config config.json --output_dir output --video_duration 30

This loads the configuration, retrieves the fact, processes audio and visuals, splices multiple background clips (if necessary) with text overlays, and assembles the final video.

	•	Command-Line Overrides:
Use argparse to override parameters (e.g., video duration) without modifying config.json.
	•	Final Output:
The generated video is saved in the specified output directory. Check logs (if implemented) for metadata.

⸻

Customization and Hyperparameters
	•	Config File:
All parameters (video duration, resolution, fonts, colors, volumes, etc.) are defined in config.json.
	•	Inline Defaults:
Each module defines its own default values at the top of functions for ease of tweaking.
	•	Dynamic Adjustments:
The system supports dynamic background selection and automatic downloads if local assets are missing.
	•	Sentence-Level Matching:
Future enhancements may include advanced NLP to precisely match each sentence with a specific video clip; the current design splits the fact text into sentences and allows splicing multiple clips accordingly.

⸻

Troubleshooting
	•	FileNotFoundError for Backgrounds Directory:
Ensure that the directory specified in backgrounds_dir exists. If not, the system will automatically download a fallback video clip.
	•	Empty Sequence Errors:
If no background clips match the keywords in your local directory, the system falls back to downloading a default clip.
	•	FFmpeg Issues:
Verify that FFmpeg is installed and in your system PATH; MoviePy depends on FFmpeg for video processing.
	•	Network/API Errors:
Ensure your internet connection is stable for API calls and video downloads.
	•	TTS Errors:
Confirm that the language code is supported by gTTS and that the text is properly formatted.

⸻

Future Enhancements
	•	Advanced Sentence Matching:
Improve NLP to match each sentence more accurately with a corresponding thematic background clip.
	•	Multiple Background Splicing:
Develop a function to splice multiple background clips (one per sentence) seamlessly.
	•	Enhanced Visual Effects:
Add transitions, animations, and effects that further polish the video.
	•	User Feedback Loop:
Implement a mechanism for manual review or automated vetting of facts before video generation.
	•	GUI for Configuration:
Build a user-friendly interface to adjust settings and preview videos.

⸻

License🦗

Lice 🦗