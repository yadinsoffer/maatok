import os
from openai import OpenAI
import json
from metadata_extractor import get_video_duration
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_prompt(video_path):
    # Get the duration of the video
    duration = get_video_duration(video_path)
    duration_str = f"{duration:.2f}"

    return f"""
Prompt:

You are to generate a short TikTok voiceover script that has maximum 102 words. It should not be more than 20 seconds when read out loud. Max 102 words. 
Here is an example of a great script, it should always resmseble that one: 
"You have got to check out this new concept of creative workshops in this Manhattan loft.  The loft is located in Hudson Yards and own by Maayan Adin, a designer and owner of her multidisciplinary creative studio. She has designed high-end hotels and restaurants and now is sharing her love for art, hospitality and creativity through those one-of-a-kind exclusive magical artistic workshops. Recently she had the Mixology Workshop and currently running the Mosaic Pottery workshop. Spots are limited so follow her to know when she drops a new one and buy tickets in the link in her bio before they sell out!"

"""


def generate_script(video_path):
    try:
        prompt = get_prompt(video_path)
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using GPT-4 for high-quality script generation
            messages=[
                {"role": "system", "content": "You are a professional TikTok script writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Balanced between creativity and consistency
            max_tokens=500,   # Enough for a long script
        )
        
        # Extract the generated script from the response
        script = response.choices[0].message.content.strip()
        return script
    
    except Exception as e:
        print(f"Error generating script: {str(e)}")
        return None

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a script based on video duration")
    parser.add_argument("video_path", help="Path to the video file")
    
    args = parser.parse_args()
    
    # Generate and print a script
    script = generate_script(args.video_path)
    if script:
        print("\nGenerated Script:")
        print("-" * 80)
        print(script)
        print("-" * 80) 