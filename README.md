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
```

## Modules and Their Responsibilities

### `main.py`
- **Role**: Orchestrates the entire workflow.
- **Operations**:
  - Loads configuration from `config.json` and applies command-line overrides
  - Retrieves fact and extracts keywords
  - Splits fact text into sentences (for background splicing)
  - Generates voiceover
  - Uses `get_background_clip` (from `visual_processing`) to select/download background clips per sentence
  - Creates text overlays for each sentence
  - Calls functions in `video_assembly.py` to splice clips, align with overlays/audio, and produce final video
  - Saves final video to specified output directory

### `fact_retrieval.py`
- **Role**: Retrieves facts from API and extracts keywords
- **Functions**:
  ```python
  get_fact(api_url: str) -> str
  extract_keywords(fact_text: str) -> list
  ```

### `audio_processing.py`
- **Role**: Generates audio components
- **Functions**:
  ```python
  generate_voiceover(text: str, lang: str, output_path: str, slow: bool) -> str
  load_music(music_path: str, volume: float)
  ```

### `visual_processing.py`
- **Role**: Handles visual asset processing
- **Functions**:
  ```python
  select_background(keywords: list, config: dict) -> str
  get_background_clip(keywords: list, config: dict) -> str
  create_text_clip(text: str, config: dict)
  ```
- **Note**: Extended functionality to dynamically download clips if needed

### `video_assembly.py`
- **Role**: Assembles final video
- **Functions**:
  ```python
  download_background_clip(keywords: list, config: dict) -> str
  assemble_video(background_clip_path: str, text_clip, voiceover_path: str, music_file: str, config: dict)
  save_video(video_clip, output_path: str, fps: int)
  ```
- **New Feature**: Supports splicing multiple background clips (one per sentence)

---

## Dependencies

```bash
pip install requests gTTS moviepy Pillow numpy
```

**Required Packages**:
- `requests` - HTTP requests
- `gTTS` - Text-to-speech
- `moviepy` - Video editing
- `Pillow` - Image processing
- `numpy` - Numerical operations
- `argparse` - CLI parsing

**System Requirements**:
- FFmpeg (must be in system PATH)

---

## Installation & Setup

1. **Clone Repository**:
   ```bash
   git clone [your-repository-url]
   ```

2. **Prepare Assets**:
   ```bash
   mkdir -p assets/{backgrounds,music}
   ```

3. **Configure Project**:
   - Edit `config.json`
   - Verify file paths match your project structure

4. **Install Requirements**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

**Basic Command**:
```bash
python main.py --config config.json --output_dir output --video_duration 30
```

**Command-Line Overrides**:
| Flag | Description |
|------|-------------|
| `--config` | Configuration file path |
| `--output_dir` | Output directory |
| `--video_duration` | Target video length |

---

## Configuration

Edit `config.json` to control:
- Video resolution
- Font styles
- Audio volumes
- API endpoints
- Fallback behaviors

---

## Troubleshooting

**Common Issues**:
- **Missing FFmpeg**: Install via system package manager
- **Empty Backgrounds Directory**: System will auto-download clips
- **API Errors**: Check internet connection and endpoint URLs
- **TTS Failures**: Verify supported language codes

---

## Future Roadmap

- Advanced NLP sentence matching
- Seamless multi-clip transitions
- Dynamic visual effects
- GUI configuration interface

---

## License 🦗

