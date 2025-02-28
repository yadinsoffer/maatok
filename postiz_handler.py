import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import urllib3
import ssl
import certifi
import json
from datetime import datetime, timedelta

load_dotenv()

class PostizHandler:
    def __init__(self):
        self.api_key = os.getenv('POSTIZ_API_KEY')
        if not self.api_key:
            raise ValueError("POSTIZ_API_KEY not found in environment variables")
            
        self.base_url = "https://api.postiz.com/public/v1"
        self.headers = {
            "Authorization": self.api_key,
            "Accept": "application/json"
        }
        
        # Configure session
        self.session = requests.Session()
        self.session.verify = certifi.where()
        
        # Configure retries
        retry = urllib3.util.Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "DELETE"]
        )
        adapter = requests.adapters.HTTPAdapter(
            max_retries=retry,
            pool_connections=3,
            pool_maxsize=10
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def get_integrations(self):
        """Get all available social media integrations"""
        try:
            response = self.session.get(
                f"{self.base_url}/integrations",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error getting integrations: {str(e)}")
            raise

    def upload_media(self, file_path):
        """
        Upload a media file to Postiz
        
        Args:
            file_path (str): Path to the media file
            
        Returns:
            dict: Response containing the uploaded file details
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            # Prepare the file for upload
            with open(file_path, 'rb') as file:
                files = {
                    'file': (Path(file_path).name, file, 'video/mp4')
                }
                
                print(f"Uploading file: {file_path}")
                response = self.session.post(
                    f"{self.base_url}/upload",
                    headers=self.headers,
                    files=files
                )
                response.raise_for_status()
                result = response.json()
                print("Upload Response:", json.dumps(result, indent=2))
                return result
                
        except Exception as e:
            print(f"Error uploading media: {str(e)}")
            raise

    def schedule_post(self, media_id, caption="", schedule_time=None):
        """
        Schedule a post with uploaded media
        
        Args:
            media_id (str): ID of the uploaded media file
            caption (str): Caption for the post
            schedule_time (datetime): When to schedule the post (default: 5 minutes from now)
            
        Returns:
            dict: Response containing the scheduled post details
        """
        try:
            # Default to 5 minutes from now if no time specified
            if schedule_time is None:
                schedule_time = datetime.now() + timedelta(minutes=5)
            
            # Create post data
            post_data = {
                "type": "schedule",
                "date": schedule_time.isoformat(),
                "shortLink": False,
                "tags": [],
                "posts": [{
                    "integration": {
                        "id": self.get_tiktok_integration_id()
                    },
                    "value": [{
                        "content": caption,
                        "media": media_id
                    }]
                }]
            }
            
            print("Scheduling post with data:", json.dumps(post_data, indent=2))
            response = self.session.post(
                f"{self.base_url}/posts",
                headers={**self.headers, "Content-Type": "application/json"},
                json=post_data
            )
            
            print("Schedule Response Status:", response.status_code)
            print("Schedule Response Headers:", dict(response.headers))
            print("Schedule Response Body:", response.text)
            
            response.raise_for_status()
            result = response.json()
            
            # Handle both array and object responses
            if isinstance(result, list):
                return result[0]
            return result
            
        except Exception as e:
            print(f"Error scheduling post: {str(e)}")
            raise

    def get_tiktok_integration_id(self):
        """Get the TikTok integration ID from available integrations"""
        integrations = self.get_integrations()
        for integration in integrations:
            if integration.get('identifier') == 'tiktok':
                return integration.get('id')
        raise ValueError("No TikTok integration found. Please add TikTok in Postiz settings.")

    def check_post_status(self, post_id):
        """
        Check the status of a specific post
        
        Args:
            post_id (str): The ID of the post to check
            
        Returns:
            dict: Response containing the post status
        """
        try:
            response = self.session.get(
                f"{self.base_url}/posts/{post_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error checking post status: {str(e)}")
            raise
