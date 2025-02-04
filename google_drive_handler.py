import os
import tempfile
from typing import List, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from pathlib import Path

# If modifying these scopes, delete the token.pickle file
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

class GoogleDriveHandler:
    def __init__(self, service_account_file: str = 'service-account.json'):
        """
        Initialize the Google Drive handler.
        
        Args:
            service_account_file (str): Path to the service account JSON file from Google Cloud Console
        """
        self.service_account_file = service_account_file
        self.service = None
        self.temp_dir = None
        self.authenticate()
        
    def authenticate(self):
        """Authenticate with Google Drive API using service account"""
        if not os.path.exists(self.service_account_file):
            raise FileNotFoundError(
                f"Service account file not found: {self.service_account_file}\n"
                "Please download it from Google Cloud Console:\n"
                "1. Go to Console > IAM & Admin > Service Accounts\n"
                "2. Create a service account or select existing\n"
                "3. Add role 'Drive Viewer' or custom role with drive.files.read permission\n"
                "4. Create new key (JSON) and save as service-account.json"
            )
            
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.service_account_file,
                scopes=SCOPES
            )
            self.service = build('drive', 'v3', credentials=credentials)
            
            # Test the credentials with a simple API call
            self.service.files().list(pageSize=1).execute()
            
        except ValueError as e:
            raise RuntimeError(
                f"Invalid service account file: {str(e)}\n"
                "Please make sure you downloaded the correct JSON file from Google Cloud Console"
            )
        except HttpError as e:
            if e.resp.status == 403:
                raise RuntimeError(
                    "Permission denied. Please ensure:\n"
                    "1. Google Drive API is enabled in your Google Cloud project\n"
                    "2. Service account has 'Drive Viewer' role or appropriate permissions\n"
                    "3. The target folder is shared with the service account email"
                )
            raise RuntimeError(f"Google Drive API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to authenticate with service account: {str(e)}")
        
    def get_folder_id_from_url(self, folder_url: str) -> str:
        """Extract folder ID from Google Drive URL"""
        # Handle different URL formats
        if 'folders/' in folder_url:
            return folder_url.split('folders/')[-1].split('?')[0]
        elif 'id=' in folder_url:
            return folder_url.split('id=')[-1].split('&')[0]
        raise ValueError(
            "Invalid Google Drive folder URL format\n"
            "URL should be in format:\n"
            "- https://drive.google.com/drive/folders/FOLDER_ID or\n"
            "- https://drive.google.com/drive?id=FOLDER_ID"
        )
        
    def download_videos(self, folder_url: str, temp_dir: Optional[str] = None) -> List[str]:
        """
        Download all videos from a Google Drive folder to a temporary directory.
        
        Args:
            folder_url (str): URL of the Google Drive folder
            temp_dir (Optional[str]): Directory to store downloaded files. If None, creates a new temp directory
            
        Returns:
            List[str]: List of paths to downloaded video files
        """
        try:
            folder_id = self.get_folder_id_from_url(folder_url)
            
            # Create temporary directory if not provided
            if not temp_dir:
                self.temp_dir = tempfile.mkdtemp()
            else:
                self.temp_dir = temp_dir
                os.makedirs(self.temp_dir, exist_ok=True)
                
            # Query for video files in the folder
            query = f"'{folder_id}' in parents and (mimeType contains 'video/')"
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            
            items = results.get('files', [])
            if not items:
                raise ValueError(
                    f"No video files found in the folder. Please ensure:\n"
                    "1. The folder URL is correct\n"
                    "2. The folder contains video files\n"
                    "3. The folder is shared with the service account email"
                )
            
            downloaded_files = []
            for item in items:
                try:
                    file_path = os.path.join(self.temp_dir, item['name'])
                    request = self.service.files().get_media(fileId=item['id'])
                    
                    with open(file_path, 'wb') as f:
                        downloader = MediaIoBaseDownload(f, request)
                        done = False
                        while not done:
                            status, done = downloader.next_chunk()
                            
                    downloaded_files.append(file_path)
                    
                except HttpError as e:
                    print(f"Warning: Failed to download {item['name']}: {str(e)}")
                    continue
                    
            if not downloaded_files:
                raise RuntimeError("Failed to download any video files")
                
            return downloaded_files
            
        except HttpError as e:
            if e.resp.status == 404:
                raise ValueError(
                    f"Folder not found. Please ensure:\n"
                    "1. The folder URL is correct\n"
                    "2. The folder is shared with the service account email"
                )
            elif e.resp.status == 403:
                raise RuntimeError(
                    "Permission denied. Please ensure:\n"
                    "1. The folder is shared with the service account email\n"
                    "2. Service account has appropriate permissions"
                )
            raise RuntimeError(f"Google Drive API error: {str(e)}")
        
    def cleanup(self):
        """Clean up temporary directory if it exists"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir) 