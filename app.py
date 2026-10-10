import os
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# ----------------------------------------------------
# Configuration & Setup
# ----------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="ElevenLabs AI Audio Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []

if "script_text" not in st.session_state:
    st.session_state.script_text = (
        "Welcome to the AI Audio Studio. This application converts written text into "
        "hyper-realistic voiceovers with nuanced pacing, tone, and emotional inflection. "
        "Select your preferred voice and try fine-tuning the controls!"
    )

# ----------------------------------------------------
# Custom Styling
# ----------------------------------------------------
st.markdown("""
<style>
    /* Card-like containers */
    .metric-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 12px;
        background-color: #e0f2fe;
        color: #0369a1;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .badge-accent {
        background-color: #fef3c7;
        color: #b45309;
    }
    .stTextArea textarea {
        font-size: 15px !important;
        line-height: 1.6 !important;
        border-radius: 8px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E88E5 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# Sidebar: Authentication & Account Quota
# ----------------------------------------------------
with st.sidebar:
    st.markdown("### 🔑 Authentication")
    env_key = os.getenv("ELEVENLABS_API_KEY")
    
    # Priority: env variable if valid, otherwise sidebar input
    if env_key and env_key != "your_elevenlabs_api_key_here":
        api_key = env_key
        st.success("✅ Connected via environment key")
        # Optional override
        with st.expander("Change API Key"):
            custom_key = st.text_input("Enter alternate key", type="password", placeholder="sk_...")
            if custom_key:
                api_key = custom_key
    else:
        api_key = st.text_input("ElevenLabs API Key", type="password", placeholder="sk_...")
        st.caption("Get your key at [elevenlabs.io](https://elevenlabs.io).")
        if not api_key:
            st.warning("⚠️ Enter an API key starting with `sk_` to begin.")
            st.stop()

    # Initialize client
    try:
        client = ElevenLabs(api_key=api_key)
    except Exception as e:
        st.error(f"Authentication Error: {e}")
        st.stop()

    st.divider()

    # Quota & Subscription Monitor
    st.markdown("### 📊 Account Quota")
    try:
        sub = client.user.subscription.get()
        tier_name = sub.tier.capitalize() if getattr(sub, "tier", None) else "Active"
        char_used = getattr(sub, "character_count", 0)
        char_limit = getattr(sub, "character_limit", 10000)
        usage_pct = min(1.0, char_used / max(1, char_limit))

        st.caption(f"**Plan Tier:** `{tier_name}`")
        st.progress(usage_pct)
        st.caption(f"Used **{char_used:,}** / **{char_limit:,}** characters ({(usage_pct*100):.1f}%)")
        remaining = max(0, char_limit - char_used)
        st.caption(f"🟢 **{remaining:,}** characters remaining")
    except Exception:
        st.info("ℹ️ Account details unavailable (custom or restricted key).")

    st.divider()
    st.markdown("### 💡 Narration Tips")
    st.caption("• Use `...` or `—` (em-dash) for natural dramatic pauses.")
    st.caption("• Capitalize words to add vocal emphasis.")
    st.caption("• Adjust **Pacing/Speed** for audiobooks vs. commercials.")

# ----------------------------------------------------
# Helper Functions: Voices Catalog & Caching
# ----------------------------------------------------
@st.cache_data(show_spinner=False, ttl=300)
def get_voice_catalog(_key):
    temp_client = ElevenLabs(api_key=_key)
    try:
        response = temp_client.voices.get_all()
        catalog = {}
        for v in response.voices:
            catalog[v.name] = {
                "voice_id": v.voice_id,
                "category": getattr(v, "category", "premade") or "premade",
                "labels": getattr(v, "labels", {}) or {},
                "description": getattr(v, "description", None),
                "preview_url": getattr(v, "preview_url", None)
            }
        return catalog
    except Exception:
        # Fallback catalog if fetch fails
        return {
            "Rachel": {
                "voice_id": "21m00Tcm4TlvDq8ikWAM",
                "category": "premade",
                "labels": {"accent": "american", "gender": "female", "age": "young", "descriptive": "calm"},
                "description": "Calm, warm, conversational female voice.",
                "preview_url": None
            },
            "Clyde": {
                "voice_id": "2EiwWnXFnvU5JabPnv8n",
                "category": "premade",
                "labels": {"accent": "american", "gender": "male", "age": "middle-aged", "descriptive": "war veteran"},
                "description": "Deep, resonant, authoritative male voice.",
                "preview_url": None
            },
            "Domi": {
                "voice_id": "AZnzlk1XvdvUeBnXmlld",
                "category": "premade",
                "labels": {"accent": "american", "gender": "female", "age": "young", "descriptive": "strong"},
                "description": "Engaging, emphatic female voice.",
                "preview_url": None
            }
        }

catalog = get_voice_catalog(api_key)
voice_names = list(catalog.keys())

# Default selection index
default_idx = 0
for i, name in enumerate(voice_names):
    if "Rachel" in name:
        default_idx = i
        break

# ----------------------------------------------------
# Main Header
# ----------------------------------------------------
st.markdown("<div class='main-title'>🎙️ AI Text-to-Speech Studio</div>", unsafe_allow_html=True)
st.markdown("Produce lifelike, studio-grade voiceovers with comprehensive pacing, emotion, and acoustic tuning.")
st.write("")

# ----------------------------------------------------
# Main Tabs
# ----------------------------------------------------
tab_studio, tab_audition, tab_history = st.tabs([
    "🎛️ Studio Generator", 
    "👥 Voice Catalog & Auditions", 
    f"📜 Session History ({len(st.session_state.history)})"
])

# ----------------------------------------------------
# TAB 1: Studio Generator
# ----------------------------------------------------
with tab_studio:
    col_editor, col_controls = st.columns([1.6, 1.2], gap="large")

    with col_editor:
        st.subheader("📝 Script & Content")

        # Quick Script Presets
        with st.expander("✨ Load Sample Script Presets", expanded=False):
            col_p1, col_p2, col_p3 = st.columns(3)
            with col_p1:
                if st.button("🎙️ Podcast Intro", use_container_width=True):
                    st.session_state.script_text = (
                        "Hey everyone, welcome back to the podcast. In today's episode, "
                        "we are breaking down the latest breakthroughs in artificial intelligence, "
                        "and what they mean for the future of creative work. Grab a cup of coffee and let's dive in!"
                    )
                if st.button("📰 News Broadcast", use_container_width=True):
                    st.session_state.script_text = (
                        "Good evening. In our top story tonight, researchers have unveiled a revolutionary "
                        "new climate model that could transform renewable energy forecasting worldwide. "
                        "Here is what you need to know."
                    )
            with col_p2:
                if st.button("📖 Audiobook / Story", use_container_width=True):
                    st.session_state.script_text = (
                        "The ancient forest was impossibly still. Beneath the canopy of silver pines, "
                        "a faint luminescence danced across the moss. Kael paused, holding his breath, "
                        "knowing that one wrong step would shatter the illusion forever."
                    )
                if st.button("🚀 Tech Launch", use_container_width=True):
                    st.session_state.script_text = (
                        "Today, we are thrilled to introduce a groundbreaking leap forward. "
                        "Faster, more intuitive, and designed seamlessly around your workflow. "
                        "Say hello to the future of voice technology."
                    )
            with col_p3:
                if st.button("🧘 Meditation Guide", use_container_width=True):
                    st.session_state.script_text = (
                        "Take a deep, gentle breath in through your nose... and slowly exhale. "
                        "Allow your shoulders to soften. Feel the quiet stillness in the room, "
                        "and let every distraction drift away."
                    )
                if st.button("🎮 Game NPC", use_container_width=True):
                    st.session_state.script_text = (
                        "Halt, traveler! The road ahead is perilous, plagued by shadow beasts and fickle weather. "
                        "If you seek passage into the Citadel, you will need more than just courage."
                    )

        # File uploader for scripts
        uploaded_file = st.file_uploader("📂 Or import script from a .txt file:", type=["txt"])
        if uploaded_file is not None:
            try:
                uploaded_content = uploaded_file.read().decode("utf-8")
                st.session_state.script_text = uploaded_content
                st.success("File imported successfully!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

        # Text input area
        user_script = st.text_area(
            "Script text",
            value=st.session_state.script_text,
            height=280,
            placeholder="Type, paste, or load a script to synthesize...",
            label_visibility="collapsed"
        )
        st.session_state.script_text = user_script

        # Real-time Metrics
        text_chars = len(user_script.strip())
        text_words = len(user_script.strip().split()) if text_chars > 0 else 0
        est_seconds = max(1, round(text_words / 2.5)) if text_words > 0 else 0

        st.caption(
            f"📊 **Characters:** `{text_chars:,}` | **Words:** `{text_words:,}` | "
            f"⏱️ **Estimated Duration:** `~{est_seconds}s`"
        )

        st.write("")
        generate_clicked = st.button("🚀 Synthesize Speech", type="primary", use_container_width=True)

    with col_controls:
        st.subheader("🎛️ Voice & Acoustic Settings")

        # Voice Selector
        selected_voice_name = st.selectbox(
            "🗣️ Speaker Voice",
            voice_names,
            index=default_idx,
            help="Choose from the voices available on your ElevenLabs account."
        )

        selected_voice_info = catalog.get(selected_voice_name, {})
        voice_id = selected_voice_info.get("voice_id", "21m00Tcm4TlvDq8ikWAM")

        # Voice Details & Audition
        labels = selected_voice_info.get("labels", {})
        if labels:
            badges_html = "".join([
                f"<span class='badge'>{k.capitalize()}: {v}</span>" for k, v in labels.items()
            ])
            st.markdown(badges_html, unsafe_allow_html=True)

        if selected_voice_info.get("preview_url"):
            st.caption("🎧 Voice Sample Preview:")
            st.audio(selected_voice_info["preview_url"], format="audio/mp3")

        st.divider()

        # Model and Audio Format
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            selected_model = st.selectbox(
                "🧠 Model Engine",
                [
                    "eleven_multilingual_v2",
                    "eleven_turbo_v2",
                    "eleven_monolingual_v1",
                    "eleven_multilingual_v1"
                ],
                index=0,
                help="Multilingual V2 supports 29 languages with highest quality. Turbo V2 offers lowest latency."
            )
        with col_m2:
            selected_format = st.selectbox(
                "🎵 Audio Quality",
                [
                    "mp3_44100_128",
                    "mp3_44100_192",
                    "mp3_24000_48",
                    "pcm_16000"
                ],
                index=0,
                help="mp3_44100_128 is ideal for standard high-fidelity audio."
            )

        # Style & Delivery Presets
        st.markdown("#### 🎭 Tone & Delivery Presets")
        preset_choice = st.selectbox(
            "Quick Delivery Presets",
            [
                "Custom / Manual",
                "Natural & Conversational",
                "Dramatic & Cinematic",
                "Audiobook & News Anchor",
                "Fast & Energetic"
            ]
        )

        # Dynamic slider defaults based on preset
        if preset_choice == "Natural & Conversational":
            default_stability, default_similarity, default_style, default_speed = 0.50, 0.75, 0.00, 1.00
        elif preset_choice == "Dramatic & Cinematic":
            default_stability, default_similarity, default_style, default_speed = 0.28, 0.85, 0.45, 0.92
        elif preset_choice == "Audiobook & News Anchor":
            default_stability, default_similarity, default_style, default_speed = 0.80, 0.75, 0.00, 1.00
        elif preset_choice == "Fast & Energetic":
            default_stability, default_similarity, default_style, default_speed = 0.40, 0.80, 0.20, 1.18
        else:
            default_stability, default_similarity, default_style, default_speed = 0.50, 0.75, 0.00, 1.00

        # Fine-Tuning Sliders
        with st.expander("⚙️ Fine-Tune Acoustic Controls", expanded=True):
            speed_val = st.slider(
                "⚡ Pacing / Speed",
                min_value=0.70,
                max_value=1.30,
                value=float(default_speed),
                step=0.02,
                help="Controls narration tempo. Lower values provide a deliberate, slower pace; higher values deliver faster speech."
            )

            stability_val = st.slider(
                "⚖️ Stability",
                min_value=0.0,
                max_value=1.0,
                value=float(default_stability),
                step=0.01,
                help="Higher values make speech uniform and steady; lower values introduce emotional variety and inflection."
            )

            similarity_val = st.slider(
                "🎯 Similarity Boost",
                min_value=0.0,
                max_value=1.0,
                value=float(default_similarity),
                step=0.01,
                help="Adherence to the original speaker's distinctive timber and acoustic profile."
            )

            style_val = st.slider(
                "🎨 Style Exaggeration",
                min_value=0.0,
                max_value=1.0,
                value=float(default_style),
                step=0.01,
                help="Exaggerates speaking style and expressiveness."
            )

            speaker_boost = st.checkbox(
                "🔊 Use Speaker Boost",
                value=True,
                help="Amplifies acoustic clarity matching the speaker profile."
            )

    # ----------------------------------------------------
    # Audio Generation Execution
    # ----------------------------------------------------
    if generate_clicked:
        if not user_script.strip():
            st.error("⚠️ Please provide text in the script area before generating.")
        else:
            with st.spinner(f"🎙️ Synthesizing speech using **{selected_voice_name}**..."):
                start_time = time.time()
                try:
                    audio_generator = client.text_to_speech.convert(
                        text=user_script.strip(),
                        voice_id=voice_id,
                        model_id=selected_model,
                        output_format=selected_format,
                        voice_settings=VoiceSettings(
                            stability=stability_val,
                            similarity_boost=similarity_val,
                            style=style_val,
                            use_speaker_boost=speaker_boost,
                            speed=speed_val
                        )
                    )

                    audio_bytes = b"".join(list(audio_generator))
                    elapsed = round(time.time() - start_time, 2)

                    st.success(f"✅ Generated in **{elapsed}s**! Listen below:")

                    # Audio Player
                    audio_mime = "audio/wav" if "pcm" in selected_format or "wav" in selected_format else "audio/mp3"
                    file_ext = "wav" if "pcm" in selected_format or "wav" in selected_format else "mp3"
                    
                    st.audio(audio_bytes, format=audio_mime)

                    # Download Button
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_name = f"{selected_voice_name.lower().replace(' ', '_')}_{timestamp_str}.{file_ext}"

                    st.download_button(
                        label=f"⬇️ Download Audio ({file_ext.upper()})",
                        data=audio_bytes,
                        file_name=file_name,
                        mime=audio_mime,
                        use_container_width=True
                    )

                    # Save to Session History
                    st.session_state.history.insert(0, {
                        "id": timestamp_str,
                        "timestamp": datetime.now().strftime("%H:%M:%S"),
                        "voice": selected_voice_name,
                        "text": user_script[:120] + ("..." if len(user_script) > 120 else ""),
                        "chars": len(user_script),
                        "model": selected_model,
                        "speed": speed_val,
                        "audio": audio_bytes,
                        "mime": audio_mime,
                        "filename": file_name
                    })

                except Exception as e:
                    st.error(f"❌ Synthesis Error: {e}")

# ----------------------------------------------------
# TAB 2: Voice Catalog & Auditions
# ----------------------------------------------------
with tab_audition:
    st.subheader("👥 Available Voice Library")
    st.write("Browse and preview all voices available on your account:")

    search_query = st.text_input("🔍 Search voices by name or accent:", placeholder="e.g. Rachel, British, Calm...")

    filtered_voices = [
        name for name in voice_names 
        if search_query.lower() in name.lower() or 
           any(search_query.lower() in str(v).lower() for v in catalog[name].get("labels", {}).values())
    ]

    col_grid = st.columns(3)
    for idx, v_name in enumerate(filtered_voices):
        col = col_grid[idx % 3]
        v_data = catalog[v_name]
        with col:
            with st.container(border=True):
                st.markdown(f"**🗣️ {v_name}**")
                v_desc = v_data.get("description")
                if v_desc:
                    st.caption(v_desc)

                v_labels = v_data.get("labels", {})
                if v_labels:
                    b_html = "".join([f"<span class='badge'>{k}: {v}</span>" for k, v in v_labels.items()])
                    st.markdown(b_html, unsafe_allow_html=True)

                if v_data.get("preview_url"):
                    st.audio(v_data["preview_url"], format="audio/mp3")
                else:
                    st.caption("*(No audio preview available)*")

# ----------------------------------------------------
# TAB 3: Generation History & Audio Vault
# ----------------------------------------------------
with tab_history:
    st.subheader(f"📜 Session History & Audio Vault ({len(st.session_state.history)})")

    if not st.session_state.history:
        st.info("No audio clips synthesized yet during this session. Generate some speech in the Studio tab to see them here!")
    else:
        col_h_header, col_h_clear = st.columns([4, 1])
        with col_h_clear:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.history = []
                st.rerun()

        for item in st.session_state.history:
            with st.container(border=True):
                col_info, col_player = st.columns([1.4, 1.6])
                with col_info:
                    st.markdown(f"**Voice:** `{item['voice']}` &nbsp;|&nbsp; ⏱️ `{item['timestamp']}`")
                    st.caption(f"**Script:** *\"{item['text']}\"*")
                    st.caption(f"**Chars:** {item['chars']} | **Speed:** {item['speed']}x | **Model:** `{item['model']}`")
                with col_player:
                    st.audio(item["audio"], format=item["mime"])
                    st.download_button(
                        label=f"⬇️ Download {item['filename']}",
                        data=item["audio"],
                        file_name=item["filename"],
                        mime=item["mime"],
                        key=f"dl_{item['id']}"
                    )
