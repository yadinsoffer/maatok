import os
from openai import OpenAI
import json
from metadata_extractor import get_duration
from dotenv import load_dotenv
from text_to_speech import TextToSpeech

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_prompt():
    return """
Below is a concise meta-prompt you can use to generate a similar ad copy with the same structure and length:

Meta-Prompt:

"Write a short, creative ad for an exclusive, candlelit workshop in a designer loft. Use a similar style and length as this example:

This perfect new york night out
Takes creative workshops to the next level

An exclusive candlelit evening 
in a designer loft
where you make your own craft

From mixology to mosaic pottery,
the workshops change occasionally, 
and are sold out quickly 

Become a part of the loft community and make new friends in this intimate ambience.

You can even book an exclusive workshop for your private event!

The loft owner and host Maayan Adin designed the Aman Hotels and is now sharing [his/her] artistic skills with you

Link for tickets on @maayanadin bio 
and follow her page to know when a new workshop drops!

Instructions:
	•	Keep it brief and match the original length.
	•	Slightly vary the wording while preserving the structure.
	•	Rotate the hotel brand among Park Hyatt, Ammaan, and W Hotels.
	•	Rotate hotels between: Aman, W Hotels, and Park Hyatt 
    The name should always be Maayan Adin
you can hange candelit to something else from time to time. also can replace the word designer
also change "her artisitic experience" to something else sometimes 

This prompt should help generate ad copies that are concise, similarly structured, and maintain the inviting, creative tone of the original."
"""

def generate_script_and_audio(output_dir: str = "output_videos"):
    """
    Generate script and convert it to audio, returning both the script and audio duration
    
    Args:
        output_dir (str): Directory to save the output files
        
    Returns:
        tuple: (script text, audio file path, audio duration in seconds)
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate the script
        prompt = get_prompt()
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a professional TikTok script writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500,
        )
        
        script = response.choices[0].message.content.strip()
        
        # Generate audio from script
        tts = TextToSpeech()
        audio_path = os.path.join(output_dir, "script_audio.mp3")
        tts.convert_text_to_speech(script, audio_path)
        
        # Get audio duration
        audio_duration = get_duration(audio_path)  # Now using get_duration instead of get_video_duration
        
        return script, audio_path, audio_duration
    
    except Exception as e:
        print(f"Error generating script and audio: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        script, audio_path, duration = generate_script_and_audio()
        print("\nGenerated Script:")
        print("-" * 80)
        print(script)
        print("-" * 80)
        print(f"\nAudio saved to: {audio_path}")
        print(f"Audio duration: {duration:.2f} seconds")
    except Exception as e:
        print(f"Error in main function: {str(e)}") 