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

You are to generate a short TikTok voiceover script that has maximum 102 words. The script must promote a unique concept of creative workshops hosted in a Manhattan loft and should include the following key points:
	1.	Concept Introduction:
	•	Introduce the innovative idea: "You have got to check out this new concept of creative workshops in this Manhattan loft."
	2.	Location:
	•	Mention that the loft is located in Hudson Yards.
	3.	Ownership and Background:
	•	State that the loft is owned by Maayan Adin, a designer who also owns a multidisciplinary creative studio.
	•	Include that Maayan Adin has designed high-end hotels and restaurants.
	4.	Workshop Details:
	•	Emphasize that she is sharing her love for art, hospitality, and creativity through exclusive, one-of-a-kind magical artistic workshops.
	•	Reference the recent Mixology Workshop and the current Mosaic Pottery workshop.
	5.	Call to Action:
	•	Inform the audience that spots are limited.
	•	Encourage viewers to follow her to know when new workshops are announced and to buy tickets through the link in her bio before they sell out.

Additional Requirements:
	•	The script must vary slightly in wording each time it is generated, while still covering all of the above points.
	•	Ensure the script reads naturally for a voiceover and engages the listener.
	•	Do not include any tone directives or annotations.
	•	The final output should be a cohesive and energetic script that fits exactly within the specified maximum 102 words.

Your output should be a complete script that a voiceover artist can read, ensuring all essential details are clearly and attractively conveyed.

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