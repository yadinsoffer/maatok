import os
import json
import requests
from dotenv import load_dotenv

def check_pending_uploads(access_token):
    """Check all pending uploads for the account"""
    url = "https://open.tiktokapis.com/v2/post/publish/list/query/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    # Query for all relevant statuses
    data = {
        "publish_status_list": [
            "PROCESSING_UPLOAD",
            "PROCESSING",
            "PENDING",
            "REVIEW",
            "FAILED",
            "SUCCESS"
        ],
        "cursor": 0,
        "count": 20  # Max number of items to return
    }
    
    try:
        print("\nSending request to:", url)
        print("Headers:", json.dumps(headers, indent=2))
        print("Data:", json.dumps(data, indent=2))
        
        response = requests.post(url, headers=headers, json=data)
        
        print("\nResponse Headers:")
        print(json.dumps(dict(response.headers), indent=2))
        
        print("\nResponse Status Code:", response.status_code)
        
        try:
            result = response.json()
            print("\nResponse Body:")
            print(json.dumps(result, indent=2))
            return result
        except json.JSONDecodeError:
            print("\nRaw Response Text:")
            print(response.text)
            raise
            
    except Exception as e:
        print(f"\nError checking pending uploads: {str(e)}")
        if hasattr(e, 'response'):
            print("\nResponse Status Code:", e.response.status_code)
            print("\nResponse Headers:")
            print(json.dumps(dict(e.response.headers), indent=2))
            print("\nResponse Text:", e.response.text)
        raise

def main():
    # Load environment variables
    load_dotenv()
    
    # Get access token
    access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
    if not access_token:
        raise ValueError("Missing TIKTOK_ACCESS_TOKEN in .env file")
    
    print(f"\nChecking pending uploads for token: {access_token}")
    result = check_pending_uploads(access_token)
    
    if result and 'data' in result:
        uploads = result['data'].get('publish_status_list', [])
        if uploads:
            print("\nFound uploads:")
            for upload in uploads:
                print(f"\nPublish ID: {upload.get('publish_id')}")
                print(f"Status: {upload.get('status')}")
                print(f"Create Time: {upload.get('create_time')}")
                print("-" * 50)
        else:
            print("\nNo pending uploads found.")

if __name__ == "__main__":
    main() 