import requests
import os
from pathlib import Path
import time
from dotenv import load_dotenv

class ZapCapHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.zapcap.ai"
        self.headers = {
            "x-api-key": self.api_key,
            "Accept": "application/json"
        }

    def upload_video(self, video_path):
        """
        Upload a video to ZapCap API
        Returns video ID for further processing
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        # Prepare the file for upload
        files = {
            'file': (Path(video_path).name, open(video_path, 'rb'), 'video/mp4')
        }

        try:
            # Upload video endpoint
            response = requests.post(
                f"{self.base_url}/videos",
                headers={"x-api-key": self.api_key},
                files=files
            )
            print("Upload Response:", response.text)  # Debug response
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error uploading video to ZapCap: {str(e)}")
            raise

    def get_templates(self):
        """
        Get available templates from the API
        """
        try:
            response = requests.get(
                f"{self.base_url}/templates",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error getting templates: {str(e)}")
            raise

    def create_task(self, video_id, template_id, language="en", top_position=30):
        """
        Create a processing task for the uploaded video
        top_position: The Y position of subtitles as percentage of video height (0-100)
        """
        try:
            # Task creation payload with render options
            data = {
                "templateId": template_id,
                "language": language,
                "renderOptions": {
                    "styleOptions": {
                        "top": top_position  # Control vertical position (0-100)
                    },
                    "subsOptions": {
                        "emoji": False,
                        "emojiAnimation": False,
                        "emphasizeKeywords": False,
                        "animation": False,
                        "punctuation": False,
                        "displayWords": 7
                    }
                }
            }
            
            print("Creating task with data:", data)  # Debug payload
            
            response = requests.post(
                f"{self.base_url}/videos/{video_id}/task",
                headers={**self.headers, "Content-Type": "application/json"},
                json=data
            )
            print("Task Creation Response:", response.text)  # Debug response
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error creating task: {str(e)}")
            raise

    def get_task_status(self, video_id, task_id):
        """
        Check the status of a video processing task
        """
        try:
            response = requests.get(
                f"{self.base_url}/videos/{video_id}/task/{task_id}",
                headers=self.headers
            )
            response.raise_for_status()
            status_data = response.json()
            print(f"Full task status response: {status_data}")  # Print full response for debugging
            return status_data

        except requests.exceptions.RequestException as e:
            print(f"Error checking task status: {str(e)}")
            raise

    def approve_transcript(self, video_id, task_id):
        """
        Approve the transcript for processing
        """
        try:
            response = requests.post(
                f"{self.base_url}/videos/{video_id}/task/{task_id}/approve-transcript",
                headers={**self.headers, "Content-Type": "application/json"},
                json={}  # Empty payload
            )
            print("Transcript Approval Response Status:", response.status_code)
            print("Transcript Approval Response Body:", response.text)  # Print response body
            response.raise_for_status()
            
            # Handle empty response
            if not response.text:
                return {"status": "approved"}
                
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error approving transcript: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    load_dotenv()
    
    API_KEY = os.getenv('ZAPCAP_API_KEY')
    if not API_KEY:
        raise ValueError("Missing ZAPCAP_API_KEY in .env file")
        
    VIDEO_PATH = "output_videos/final_output_with_voice.mp4"
    TEMPLATE_ID = "07ffd4b8-4e1a-4ee3-8921-d58802953bcd"  # Specified template ID

    handler = ZapCapHandler(API_KEY)
    
    try:
        print(f"Using template ID: {TEMPLATE_ID}")
        
        # Step 1: Upload the video
        upload_result = handler.upload_video(VIDEO_PATH)
        video_id = upload_result.get("id")
        print("Upload successful!")
        print("Video ID:", video_id)
        
        # Step 2: Create a task with template and custom position
        task_result = handler.create_task(video_id, TEMPLATE_ID, language="en", top_position=30)  # Set captions at 30% from top
        task_id = task_result.get("taskId")
        print("Task created!")
        print("Task ID:", task_id)
        
        # Step 3: Monitor task progress and handle transcript approval
        transcript_approved = False
        while True:
            task_status = handler.get_task_status(video_id, task_id)
            status = task_status.get("status")
            print(f"Task Status: {status}")
            
            if status == "transcriptionCompleted" and not transcript_approved:
                print("Approving transcript...")
                handler.approve_transcript(video_id, task_id)
                transcript_approved = True
                print("Transcript approved!")
            elif status == "completed":
                print("Video processing completed!")
                print("Download URL:", task_status.get("downloadUrl"))
                break
            elif status in ["failed", "error"]:
                print("Task failed:", task_status.get("error"))
                break
                
            time.sleep(5)  # Wait 5 seconds before checking again
            
    except Exception as e:
        print(f"Error: {str(e)}") 
