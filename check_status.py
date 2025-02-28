import requests
import sys
import time

def check_task_status(api_key, video_id, task_id):
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            f"https://api.zapcap.ai/videos/{video_id}/task/{task_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    API_KEY = "bcf60d4d261e7f506087134461011e3180c10f305f8637d2a56494f1968c850b"
    VIDEO_ID = "6934905b-1c62-4a81-9031-d4685acc0d9a"  # Your video ID
    TASK_ID = "6dbdf3a4-c375-4ee7-944c-dc92b1ea6347"   # Your task ID
    
    result = check_task_status(API_KEY, VIDEO_ID, TASK_ID)
    if result:
        status = result.get("status")
        print(f"Status: {status}")
        if status == "completed":
            print(f"Download URL: {result.get('downloadUrl')}")
        elif status == "failed":
            print(f"Error: {result.get('error')}") 