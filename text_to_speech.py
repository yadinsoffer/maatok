import os
from dotenv import load_dotenv
from elevenlabs import generate, save, set_api_key, Voice, VoiceSettings
import argparse

# Load environment variables
load_dotenv()

# Set up API key
API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
if not API_KEY:
    raise ValueError("ELEVEN_LABS_API_KEY not found in environment variables")
set_api_key(API_KEY)

class TextToSpeech:
    def __init__(self, voice_id="8DzKSPdgEQPaK5vKG0Rs", model="eleven_multilingual_v2"):
        """
        Initialize TextToSpeech with voice and model settings
        
        Args:
            voice_id (str): ElevenLabs voice ID
            model (str): ElevenLabs model name
        """
        self.voice_id = voice_id
        self.model = model
        self.voice = Voice(
            voice_id=voice_id,
            settings=VoiceSettings(
                stability=0.5,
                similarity_boost=0.75,
                style=1.0,
                use_speaker_boost=True
            )
        )

    def convert_text_to_speech(self, input_text: str, output_file: str) -> str:
        """
        Convert text to speech and save as audio file
        
        Args:
            input_text (str): Text to convert to speech
            output_file (str): Path to save the audio file
            
        Returns:
            str: Path to the generated audio file
            
        Raises:
            Exception: If text-to-speech conversion fails
        """
        try:
            # Generate audio using ElevenLabs API
            audio = generate(
                text=input_text,
                voice=self.voice,
                model=self.model
            )
            
            # Save the audio file
            with open(output_file, 'wb') as f:
                f.write(audio)
            print(f"Successfully created audio file: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"An error occurred during text-to-speech conversion: {str(e)}")
            raise

def convert_file_to_speech(input_file: str, output_file: str) -> str:
    """
    Convenience function to convert text from a file to speech
    """
    try:
        # Read the input text file
        with open(input_file, 'r') as file:
            text = file.read()
        
        # Convert to speech
        tts = TextToSpeech()
        return tts.convert_text_to_speech(text, output_file)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Convert text file to speech using ElevenLabs API')
    parser.add_argument('input_file', help='Path to the input text file')
    parser.add_argument('--output_file', help='Path to the output audio file (default: output.mp3)', default='output.mp3')
    
    args = parser.parse_args()
    
    try:
        convert_file_to_speech(args.input_file, args.output_file)
    except Exception as e:
        print(f"Failed to convert text to speech: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main() 