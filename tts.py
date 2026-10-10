import os
import argparse
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save, VoiceSettings

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key or api_key == "your_elevenlabs_api_key_here":
        print("Error: ELEVENLABS_API_KEY environment variable not set or invalid.")
        print("Please copy .env.example to .env and add your valid ElevenLabs API key.")
        return

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="ElevenLabs Text-to-Speech CLI")
    parser.add_argument("text", type=str, help="The text to convert to speech")
    parser.add_argument("--voice", type=str, default="Rachel", help="The name of the voice to use (default: Rachel)")
    parser.add_argument("--output", type=str, default="output.mp3", help="Output file path (default: output.mp3)")
    parser.add_argument("--model", type=str, default="eleven_multilingual_v2", help="ElevenLabs model to use (default: eleven_multilingual_v2)")
    parser.add_argument("--speed", type=float, default=1.0, help="Pacing/speed multiplier between 0.7 and 1.3 (default: 1.0)")
    parser.add_argument("--stability", type=float, default=0.5, help="Voice stability between 0.0 and 1.0 (default: 0.5)")
    parser.add_argument("--similarity", type=float, default=0.75, help="Similarity boost between 0.0 and 1.0 (default: 0.75)")
    parser.add_argument("--style", type=float, default=0.0, help="Style exaggeration between 0.0 and 1.0 (default: 0.0)")
    
    args = parser.parse_args()

    try:
        # Initialize the client
        client = ElevenLabs(api_key=api_key)

        print(f"Generating speech...")
        print(f"Text: '{args.text}'")
        print(f"Voice: {args.voice}")
        print(f"Speed: {args.speed}x | Stability: {args.stability} | Similarity: {args.similarity}")
        
        # Resolve voice name to voice_id
        voice_id = args.voice
        try:
            voices_response = client.voices.get_all()
            for v in voices_response.voices:
                if v.name.lower() == args.voice.lower():
                    voice_id = v.voice_id
                    break
        except Exception as e:
            print(f"Warning: Could not fetch voices to resolve name. Using '{args.voice}' as voice_id. ({e})")
        
        # Generate audio
        audio = client.text_to_speech.convert(
            text=args.text,
            voice_id=voice_id,
            model_id=args.model,
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(
                stability=args.stability,
                similarity_boost=args.similarity,
                style=args.style,
                use_speaker_boost=True,
                speed=args.speed
            )
        )

        # Save audio to file
        save(audio, args.output)
        print(f"Successfully saved audio to {args.output}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
