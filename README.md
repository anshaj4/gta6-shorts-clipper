# 🎮 AutoBot Clipper: Fully Automated GTA 6 Live Stream Clipper & YouTube Shorts Publisher

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-9.0%2B-green.svg)](https://ffmpeg.org/)
[![Twitch Helix API](https://img.shields.io/badge/Twitch-Helix%20API-9146FF.svg)](https://dev.twitch.tv/)
[![YouTube Data API v3](https://img.shields.io/badge/YouTube-Data%20API%20v3-FF0000.svg)](https://developers.google.com/youtube/v3)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AutoBot Clipper** is an autonomous, end-to-end AI system that automatically monitors live **GTA 6** streams across **Twitch and YouTube**, captures real-time high-energy gameplay, detects viral moments using multi-signal AI analysis, formats clips into vertical **9:16 YouTube Shorts** with animated subtitles, generates context-aware SEO metadata, and publishes them directly to your YouTube channel.

Zero manual timestamps. Zero manual video editing. Zero manual uploading.

---

## ✨ Features

- **🔴 Multi-Platform Live Discovery**:
  - Automatically identifies live GTA 6 streamers on **Twitch** (KaiCenat, Jynxzi, xQc, stableronaldo, etc.).
  - Detects live streams from top creators like **IShowSpeed** on **YouTube**.
  - Enforces English-first and UK gaming streamer prioritization.
  - Fair round-robin rotation so no single streamer dominates your uploads.

- **🧠 Multi-Modal AI Highlight Detection**:
  - **Audio Energy**: Detects sudden loudness spikes, screams, and genuine laughter using RMS and Zero Crossing Rate analysis.
  - **Speech Recognition**: Transcribes spoken dialogue with `faster-whisper`, detecting excitement keywords and swearing.
  - **Visual Action**: Analyzes video frame dynamics via OpenCV to detect vehicle crashes, police chases, gunfights, and sudden explosions.
  - **Smart Duration Snapping**: Targets **45-second clips** (42–48s) while intelligently snapping to sentence boundaries so dialogue is never cut in half.
  - **Strict Quality Filter**: Rejects calm, silent, or repetitive footage.

- **📱 Smart YouTube Shorts Video Editor**:
  - Automatically converts horizontal 16:9 gameplay to vertical **9:16 (1080 × 1920)** Shorts.
  - **Alternating Layouts**:
    - **Split-Screen Layout**: Gameplay on the upper half, streamer facecam on the lower half.
    - **Blurred Background Fill**: High-definition gameplay centered over an aesthetically blurred background.
  - **Animated Subtitles**: Burns high-contrast, yellow-highlighted captions directly into the Shorts safe area using ASS subtitles.

- **🏷️ AI Metadata & SEO Generation**:
  - Generates curiosity-driven, relatable titles based on the actual dialogue and event.
  - **Mandatory Hashtags**: Guarantees every title strictly ends with `#shorts #gtavi #gta6`.
  - Crafts UK gaming-optimized descriptions with original streamer attribution.
  - Generates 20–25 SEO tags tailored to the streamer and specific event.

- **🚀 YouTube Data API v3 Publisher**:
  - Resumable video uploads with exponential backoff retry.
  - Supports both **Public** and **Private** privacy statuses.
  - **Disk Space Protection**: Strictly enforces a **10 GB local disk limit** and auto-deletes local video files immediately after successful upload.
  - **Pacing**: Configurable random delay (8 to 10 minutes) between uploads, targeting 15 Shorts per day.
  - **Local Midnight Reset**: Automatically resets the daily upload count at 12:00 AM in your local timezone.

- **📊 Web Dashboard & Controller**:
  - Real-time Flask dashboard displaying active live streams, generated clips, scores, upload history, and disk usage.
  - Single-click controls to toggle automation loop, trigger one-off captures, or reset daily counters.

---

## 🛠️ Architecture

```text
autobot-clipper/
│
├── bot.py                     # Multi-mode CLI and automation runner
├── config.py                  # API health check and YouTube OAuth helper
├── requirements.txt           # Modern Python dependencies
├── .env                       # Twitch API credentials (git-ignored)
├── client_secrets.json        # Google OAuth desktop credentials (git-ignored)
│
├── modules/
│   ├── twitch_discovery.py    # Twitch Helix API stream & VOD discovery
│   ├── vod_downloader.py      # Streamlink & yt-dlp live capturer & disk manager
│   ├── audio_analyser.py      # RMS loudness and scream detector
│   ├── speech_analyser.py     # Faster-Whisper transcriber & sentiment analyzer
│   ├── visual_analyser.py     # OpenCV visual motion & action analyzer
│   ├── chat_analyser.py       # Twitch chat replay velocity & hype analyzer
│   ├── highlight_detector.py  # Multi-signal highlight scoring & 45s window snapper
│   ├── shorts_editor.py       # 9:16 vertical formatter (stacked facecam & blurred bg)
│   ├── subtitle_generator.py  # High-contrast ASS animated subtitles
│   ├── metadata_generator.py  # Contextual titles, tags, and mandatory hashtags
│   ├── youtube_uploader.py    # Resumable YouTube Data API v3 uploader
│   ├── scheduler.py           # Background automation loop & streamer rotation
│   ├── database.py            # SQLite database manager
│   └── dashboard.py           # Local Flask web controller
│
├── database/                  # SQLite storage for clips, status & logs
├── downloads/                 # Temporary raw captures (auto-deleted)
├── clips/                     # Rendered Shorts (auto-deleted upon upload)
└── tests/                     # Pipeline unit and integration tests
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.13)
- [FFmpeg](https://ffmpeg.org/download.html) installed and added to your system `PATH`.

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/anshaj4/gta6-shorts-clipper.git
cd gta6-shorts-clipper

python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux / macOS

pip install -r requirements.txt
```

### 3. API Configuration

1. **Twitch API**:
   Create an application on [Twitch Developer Console](https://dev.twitch.tv/console). Create a `.env` file in the project root:
   ```env
   TWITCH_CLIENT_ID=your_twitch_client_id
   TWITCH_CLIENT_SECRET=your_twitch_client_secret
   ```

2. **YouTube API**:
   - Create a Google Cloud project with the **YouTube Data API v3** enabled.
   - Configure OAuth Consent screen (Scope: `https://www.googleapis.com/auth/youtube.upload`).
   - Download the Desktop Application OAuth client credentials and save as `client_secrets.json` in the project root.
   - Run the one-time authorization:
     ```bash
     python config.py --auth
     ```

---

## 🖥️ Usage

### Run the Web Dashboard
```bash
python bot.py --mode dashboard
```
Open `http://localhost:5000` in your browser. From here you can view active live streams, monitor live storage, trigger one-click clips, and start the background automation loop.

### Run Headless Automation Loop
```bash
python bot.py --mode auto
```
Runs the continuous autonomous loop:
- Discovers live GTA 6 streamers (IShowSpeed, KaiCenat, Jynxzi, etc.).
- Rotates streamers so each creator is highlighted fairly.
- Captures 3-minute live segments and extracts the highest-scoring 45-second moment.
- Formats to 9:16 (alternating stacked facecam and blurred background).
- Publishes directly to YouTube as Public.
- Waits 8 to 10 minutes between uploads, targeting 15 Shorts per day.
- Auto-deletes local files to stay well within the 10 GB disk limit.

### Run Single Cycle
```bash
python bot.py --mode once
```

### Legacy Interactive Mode
```bash
python bot.py --mode interactive
```

---

## 🧪 Testing

Run the included automated test suite:
```bash
python -m unittest tests/test_pipeline.py
```

---

## 🔒 Security
- All sensitive files (`client_secrets.json`, `.env`, `token.json`, `credentials.txt`, `database/`, media folders) are strictly excluded via `.gitignore`.
- YouTube credentials use desktop OAuth with automatic token refresh.

---

## 📄 License
This project is licensed under the MIT License.
