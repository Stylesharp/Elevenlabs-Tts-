# 🎙️ ElevenLabs AI Text-to-Speech Studio

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B.svg)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-API%20v2-black.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A feature-rich, studio-grade Text-to-Speech web application and CLI built with **Streamlit** and the **ElevenLabs Python SDK (v2)**.

---

## ✨ Features & Capabilities

### 🎛️ 1. Studio Voice Generator
- **Multi-Model Engine:** Choose from `eleven_multilingual_v2` (29 languages), `eleven_turbo_v2` (ultra-low latency), and specialized monolingual models.
- **⚡ Pacing & Speed Control:** Adjust speech tempo dynamically from `0.70x` (deliberate & slow) to `1.30x` (fast & energetic).
- **🎚️ Advanced Acoustic Tuning:**
  - **Stability:** Balance between uniform steadiness and expressive emotional variation.
  - **Similarity Boost:** Lock in voice identity and timbre fidelity.
  - **Style Exaggeration:** Amplify vocal drama and expressive flair.
  - **Speaker Boost:** Enhance acoustic resonance matching the speaker profile.
- **🎭 Quick Delivery Presets:** One-click presets for *Natural Conversational*, *Dramatic & Cinematic*, *Audiobook & News Anchor*, and *Fast & Energetic*.
- **🎵 Multiple Audio Formats:** Synthesize in standard MP3 (128kbps / 192kbps) or uncompressed WAV/PCM.

### 📝 2. Script Presets & Import
- **Instant Script Presets:** Quick-load scripts for Podcast Intros, News Broadcasts, Audiobook Stories, Tech Launches, Meditation Guides, and Video Game NPCs.
- **File Upload:** Import any `.txt` script file directly into the studio.
- **Real-Time Word & Timing Metrics:** Live character count, word count, and estimated narration duration.

### 👥 3. Voice Catalog & Auditions
- Browse all voices linked to your ElevenLabs account with category tags, accents, gender, and descriptions.
- Search voices by name, accent, or style.
- **Interactive Audio Previews:** Listen to sample auditions directly before synthesizing your custom text.

### 📜 4. Session Audio Vault & History
- Keeps track of all audio generated during your active session.
- Side-by-side comparison of different voices, speeds, and models.
- Instant replay and direct MP3/WAV download buttons for every clip.

### 📊 5. Real-Time Account Quota Monitor
- Live query of your ElevenLabs account tier.
- Progress bar displaying character count used, monthly limit, and characters remaining.

---

## 🚀 Deployment (Streamlit Community Cloud)

This app is optimized for zero-config deployment on **[Streamlit Community Cloud](https://share.streamlit.io/)**:

1. Fork or push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and create a **New app**.
3. Select your repository (`Stylesharp/Elevenlabs-Tts-`), branch `main`, and main file `app.py`.
4. Open **Advanced settings** -> **Secrets** and add your ElevenLabs API key:
   ```toml
   ELEVENLABS_API_KEY = "sk_your_actual_elevenlabs_api_key_here"
   ```
5. Click **Deploy**!

---

## 💻 Local Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/Stylesharp/Elevenlabs-Tts-.git
cd Elevenlabs-Tts-
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your API Key
Copy the `.env.example` file to `.env`:
```bash
cp .env.example .env
```
Open `.env` and paste your secret key (must start with `sk_`):
```env
ELEVENLABS_API_KEY=sk_your_elevenlabs_api_key_here
```

### 4. Run the Web Studio
```bash
python -m streamlit run app.py
```

### 5. Or use the Command-Line Interface (CLI)
You can also generate speech directly from your terminal:
```bash
# Basic generation
python tts.py "Hello, this is a test of the ElevenLabs API." --voice "Rachel"

# Advanced CLI options (with speed & tuning)
python tts.py "Welcome back to the podcast." --voice "Clyde" --speed 1.05 --stability 0.60 --output "podcast_intro.mp3"
```

---

## 🛠️ Tech Stack
- **Python 3.8+**
- **Streamlit** for the interactive reactive frontend
- **ElevenLabs Python SDK (v2)** for voice synthesis and account management
- **python-dotenv** for secure credential handling