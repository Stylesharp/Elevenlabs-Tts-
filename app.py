import os
import streamlit as st
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="ElevenLabs TTS", 
    page_icon="🎙️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---- Custom CSS for a better look ----
st.markdown("""
    <style>
    .stTextArea textarea {
        font-size: 16px !important;
        border-radius: 8px;
    }
    .stButton>button {
        font-size: 18px !important;
        border-radius: 8px;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .main-header {
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 0px;
    }
    .sub-header {
        color: #616161;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# ---- Sidebar for API Key ----
with st.sidebar:
    st.header("🔑 Authentication")
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        api_key = st.text_input("ElevenLabs API Key", type="password", placeholder="sk_...")
        st.caption("Don't have an API key? Get one at [ElevenLabs](https://elevenlabs.io).")
        if not api_key:
            st.warning("⚠️ Please provide an API key to continue.")
            st.stop()
    else:
        st.success("✅ API Key loaded from environment")

    st.divider()
    st.markdown("### ℹ️ About")
    st.markdown("This app converts text into highly realistic speech using the ElevenLabs API.")

# ---- Initialize Client ----
try:
    client = ElevenLabs(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing client: {e}")
    st.stop()

# ---- Fetch Voices ----
@st.cache_data(show_spinner=False)
def get_voices(_client_key):
    temp_client = ElevenLabs(api_key=_client_key)
    try:
        response = temp_client.voices.get_all()
        return {v.name: v.voice_id for v in response.voices}
    except Exception as e:
        return {"Rachel (Fallback)": "21m00Tcm4TlvDq8ikWAM", "Clyde (Fallback)": "2EiwWnXFnvU5JabPnv8n"}

voice_dict = get_voices(api_key)
voice_names = list(voice_dict.keys())

default_index = 0
for i, name in enumerate(voice_names):
    if "Rachel" in name:
        default_index = i
        break

# ---- Main Layout ----
st.markdown("<h1 class='main-header'>🎙️ AI Text-to-Speech Studio</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Transform your text into lifelike speech. Fine-tune the voice settings below to get the perfect delivery.</p>", unsafe_allow_html=True)

col_input, col_settings = st.columns([2, 1], gap="large")

with col_settings:
    st.subheader("🎛️ Voice Controls")
    selected_voice_name = st.selectbox("🗣️ Select Voice", voice_names, index=default_index)
    selected_model = st.selectbox("🧠 Select Model", [
        "eleven_multilingual_v2", 
        "eleven_monolingual_v1", 
        "eleven_turbo_v2",
        "eleven_multilingual_v1"
    ], index=0)
    
    st.divider()
    
    with st.expander("⚙️ Advanced Voice Settings", expanded=True):
        st.caption("ElevenLabs doesn't use a 'pitch' slider, but these settings control the delivery, emotion, and tone.")
        stability = st.slider(
            "Stability", 
            min_value=0.0, max_value=1.0, value=0.5, step=0.01, 
            help="Increasing stability makes the voice more consistent between generations, but slightly more monotone. Lowering it makes it more expressive but potentially unstable."
        )
        similarity = st.slider(
            "Similarity Boost", 
            min_value=0.0, max_value=1.0, value=0.75, step=0.01, 
            help="Higher values make the output closer to the original voice sample. Lower values allow the AI to introduce its own characteristics."
        )
        style = st.slider(
            "Style Exaggeration", 
            min_value=0.0, max_value=1.0, value=0.0, step=0.01, 
            help="Exaggerates the style of the voice. Higher values can cause instability."
        )
        speaker_boost = st.checkbox(
            "Use Speaker Boost", 
            value=True, 
            help="Boosts the similarity to the original speaker's acoustic characteristics."
        )

with col_input:
    st.subheader("📝 Input Text")
    text_input = st.text_area(
        "Text to narrate", 
        height=300, 
        placeholder="Type or paste your script here...",
        label_visibility="collapsed"
    )
    
    # Text statistics
    char_count = len(text_input.strip())
    st.caption(f"**Characters:** {char_count} | Estimated audio length: ~{max(1, char_count // 15)} seconds")
    
    if st.button("✨ Generate Audio", type="primary", use_container_width=True):
        if not text_input.strip():
            st.error("⚠️ Please enter some text to generate speech.")
        else:
            with st.spinner(f"🎙️ Generating speech using voice '{selected_voice_name}'..."):
                try:
                    voice_id = voice_dict[selected_voice_name]
                    
                    audio_generator = client.text_to_speech.convert(
                        text=text_input,
                        voice_id=voice_id,
                        model_id=selected_model,
                        output_format="mp3_44100_128",
                        voice_settings=VoiceSettings(
                            stability=stability,
                            similarity_boost=similarity,
                            style=style,
                            use_speaker_boost=speaker_boost
                        )
                    )
                    
                    audio_bytes = b"".join(list(audio_generator))
                    
                    st.success("✅ Audio generated successfully!")
                    
                    st.audio(audio_bytes, format="audio/mp3")
                    
                    st.download_button(
                        label="⬇️ Download MP3",
                        data=audio_bytes,
                        file_name=f"{selected_voice_name.lower().replace(' ', '_')}_tts.mp3",
                        mime="audio/mp3",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ An error occurred: {e}")
