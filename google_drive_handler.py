import os
import tempfile
import random
import subprocess
from typing import List, Optional, Dict, Tuple
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
        
    def get_video_duration(self, file_id: str) -> float:
        """Get video duration from Google Drive metadata"""
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="videoMediaMetadata"
            ).execute()
            
            # Duration is in milliseconds
            duration_ms = float(file.get('videoMediaMetadata', {}).get('durationMillis', 0))
            return duration_ms / 1000  # Convert to seconds
            
        except HttpError:
            return 0  # Return 0 if unable to get duration
        
    def list_folder_contents(self, folder_id: str) -> List[Dict]:
        """List all files and folders in a folder recursively with video durations"""
        try:
            # First get all subfolders
            folder_query = f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
            folders_result = self.service.files().list(
                q=folder_query,
                pageSize=100,
                fields="files(id, name)"
            ).execute()
            
            folders = folders_result.get('files', [])
            
            # Get all video files in current folder
            video_query = f"'{folder_id}' in parents and (mimeType contains 'video/')"
            videos_result = self.service.files().list(
                q=video_query,
                pageSize=100,
                fields="files(id, name, mimeType, videoMediaMetadata)"
            ).execute()
            
            videos = []
            for video in videos_result.get('files', []):
                duration = self.get_video_duration(video['id'])
                if duration > 0:  # Only include videos with valid duration
                    video['duration'] = duration
                    videos.append(video)
            
            # Recursively get videos from subfolders
            for folder in folders:
                subfolder_videos = self.list_folder_contents(folder['id'])
                videos.extend(subfolder_videos)
                
            return videos
            
        except HttpError as e:
            print(f"Warning: Failed to list contents of folder: {str(e)}")
            return []
        
    def find_best_video_combination(self, videos: List[Dict], target_duration: float, min_videos: int = 20, margin: float = 0.1) -> List[Dict]:
        """
        Create a sequence of short segments (0.5-1s) from at least 20 different videos.
        
        Args:
            videos (List[Dict]): List of video metadata including durations
            target_duration (float): Target duration in seconds
            min_videos (int): Minimum number of different videos to use
            margin (float): Acceptable margin of error in seconds
            
        Returns:
            List[Dict]: List of selected video segments with timing info
        """
        if len(videos) < min_videos:
            raise ValueError(f"Not enough videos available. Need at least {min_videos}, but only found {len(videos)}")
        
        # Shuffle all videos for random selection
        all_videos = videos.copy()
        random.shuffle(all_videos)
        
        # Initialize selected videos and segments
        selected_videos = []  # List of videos we're using
        segments = []        # List of all segments we'll create
        current_duration = 0
        last_video = None
        
        # First, ensure we have enough source videos
        selected_videos = all_videos[:min_videos]
        
        # Create segments until we match target duration
        while current_duration < target_duration:
            # Calculate remaining duration
            remaining = target_duration - current_duration
            
            # Pick a random video (not same as last segment)
            while True:
                video = random.choice(selected_videos)
                if video != last_video:
                    break
            
            # Determine segment duration (1.0-1.5s, unless it's the last segment)
            if remaining <= 1.0:
                segment_duration = remaining  # Make last segment fit exactly
            else:
                segment_duration = random.uniform(1.0, min(1.5, remaining))
            
            # Pick a random start point that's at least 2 seconds away from any existing segment
            # from this same video
            max_start = video['duration'] - segment_duration
            existing_segments = [s for s in segments if s['video'] == video]
            
            # Create list of forbidden ranges (+-2 seconds around existing segments)
            forbidden_ranges = []
            for seg in existing_segments:
                start = max(0, seg['start'] - 2)
                end = min(video['duration'], seg['end'] + 2)
                forbidden_ranges.append((start, end))
            
            # Find available ranges
            available_ranges = [(0, max_start)]
            for start, end in sorted(forbidden_ranges):
                if not available_ranges:
                    break
                last_start, last_end = available_ranges[-1]
                if start > last_start:
                    available_ranges[-1] = (last_start, start)
                if end < last_end:
                    available_ranges.append((end, last_end))
            
            # If no available ranges, try another video
            if not available_ranges or not any(end - start >= segment_duration for start, end in available_ranges):
                continue
            
            # Pick a random point from available ranges
            valid_ranges = [(start, end) for start, end in available_ranges if end - start >= segment_duration]
            start_range, end_range = random.choice(valid_ranges)
            start_time = random.uniform(start_range, end_range - segment_duration)
            
            # Create segment
            segment = {
                'video': video,
                'start': start_time,
                'end': start_time + segment_duration,
                'duration': segment_duration,
                'speed_up': random.random() < 0.3  # 30% chance of speed up
            }
            
            segments.append(segment)
            current_duration += segment_duration
            last_video = video
            
            # Break if we've reached or exceeded the target duration
            if current_duration >= target_duration:
                # If we went over, adjust the last segment to fit exactly
                if current_duration > target_duration:
                    overage = current_duration - target_duration
                    segments[-1]['end'] -= overage
                    segments[-1]['duration'] -= overage
                break
        
        # Print segment information
        print(f"\nCreated {len(segments)} segments from {len(set(s['video']['name'] for s in segments))} different videos:")
        for i, segment in enumerate(segments, 1):
            speed_info = " (2x speed)" if segment['speed_up'] else ""
            print(f"{i}. {segment['video']['name']} [{segment['start']:.1f}s-{segment['end']:.1f}s] ({segment['duration']:.2f}s){speed_info}")
        print(f"Total duration: {current_duration:.2f}s (target: {target_duration:.2f}s)")
        
        return segments
        
    def download_videos(self, folder_url: str, target_duration: float, temp_dir: Optional[str] = None) -> List[str]:
        """
        Download videos and create short segments that match target duration exactly.
        
        Args:
            folder_url (str): URL of the Google Drive folder
            target_duration (float): Target duration in seconds
            temp_dir (Optional[str]): Directory to store downloaded files. If None, creates a new temp directory
            
        Returns:
            List[str]: List of paths to processed video segments
        """
        try:
            folder_id = self.get_folder_id_from_url(folder_url)
            
            # Create temporary directory if not provided
            if not temp_dir:
                self.temp_dir = tempfile.mkdtemp()
            else:
                self.temp_dir = temp_dir
                os.makedirs(self.temp_dir, exist_ok=True)
                
            # Get all video files recursively with durations
            all_videos = self.list_folder_contents(folder_id)
            
            if not all_videos:
                raise ValueError(
                    f"No video files found in the folder or its subfolders. Please ensure:\n"
                    "1. The folder URL is correct\n"
                    "2. The folder or its subfolders contain video files\n"
                    "3. The folder is shared with the service account email"
                )
            
            # Find best combination of segments
            segments = self.find_best_video_combination(all_videos, target_duration)
            
            # Download and process videos
            processed_files = []
            downloaded_videos = {}  # Cache for downloaded videos
            
            for i, segment in enumerate(segments, 1):
                try:
                    video = segment['video']
                    
                    # Download video if not already downloaded
                    if video['id'] not in downloaded_videos:
                        temp_path = os.path.join(self.temp_dir, f"temp_{video['name']}")
                        request = self.service.files().get_media(fileId=video['id'])
                        
                        with open(temp_path, 'wb') as f:
                            downloader = MediaIoBaseDownload(f, request)
                            done = False
                            while not done:
                                status, done = downloader.next_chunk()
                        
                        downloaded_videos[video['id']] = temp_path
                    
                    # Create segment
                    output_path = os.path.join(self.temp_dir, f"segment_{i:03d}_{video['name']}")
                    
                    # Build ffmpeg command with accurate seeking
                    cmd = ['ffmpeg']
                    
                    # Add input first
                    cmd.extend(['-i', downloaded_videos[video['id']]])
                    
                    # Add seeking and duration AFTER input for frame-accurate cutting
                    cmd.extend([
                        '-ss', str(segment['start']),
                        '-t', str(segment['duration']),
                        '-avoid_negative_ts', '1'
                    ])
                    
                    # Add speed up if needed
                    if segment['speed_up']:
                        cmd.extend(['-filter:v', 'setpts=0.5*PTS', '-filter:a', 'atempo=2.0'])
                    
                    # Add output options
                    cmd.extend([
                        '-c:v', 'libx264',
                        '-preset', 'slow',
                        '-crf', '18',
                        '-c:a', 'aac',
                        '-b:a', '192k',
                        '-pix_fmt', 'yuv420p',
                        '-y',
                        output_path
                    ])
                    
                    # Run ffmpeg with logging
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    
                    # Log any FFmpeg warnings or errors
                    if result.stderr:
                        print(f"\nFFmpeg log for segment {i}:")
                        print(result.stderr)
                    
                    processed_files.append(output_path)
                    print(f"Created segment {i}/{len(segments)}: {os.path.basename(output_path)}")
                    
                except (HttpError, subprocess.CalledProcessError) as e:
                    print(f"Warning: Failed to process segment {i}: {str(e)}")
                    continue
            
            # Clean up downloaded videos
            for temp_path in downloaded_videos.values():
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
            if not processed_files:
                raise RuntimeError("Failed to create any video segments")
                
            return processed_files
            
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