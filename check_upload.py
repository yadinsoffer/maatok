import os
import json
import requests
from dotenv import load_dotenv

def check_upload_status(publish_id, access_token):
    """Check status of an upload using its publish ID"""
    url = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8"
    }
    
    data = {
        "publish_id": publish_id,
        "fields": ["status", "uploaded_bytes", "error_code", "error_message"]
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
            
            # Check for specific error conditions
            if result.get('error', {}).get('code') != 'ok':
                print("\nError from TikTok API:")
                print(f"Code: {result.get('error', {}).get('code')}")
                print(f"Message: {result.get('error', {}).get('message')}")
                
            # Print detailed status information
            if 'data' in result:
                status = result['data'].get('status', 'UNKNOWN')
                print(f"\nUpload Status: {status}")
                if status == 'FAILED':
                    print("Upload has failed - you can try uploading again")
                elif status == 'PROCESSING_UPLOAD':
                    print(f"Upload is still processing - {result['data'].get('uploaded_bytes', 0)} bytes uploaded")
                elif status == 'SUCCESS':
                    print("Upload completed successfully!")
                
            return result
        except json.JSONDecodeError:
            print("\nRaw Response Text:")
            print(response.text)
            raise
            
    except Exception as e:
        print(f"\nError checking status: {str(e)}")
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
    
    # Try to get publish_id from file first
    publish_id = None
    if os.path.exists('last_upload_id.txt'):
        with open('last_upload_id.txt', 'r') as f:
            publish_id = f.read().strip()
            print(f"\nFound saved publish_id: {publish_id}")
    
    # If no saved publish_id, ask for input
    if not publish_id:
        publish_id = input("Enter the publish_id from your last upload attempt: ")
    
    print(f"\nChecking status for publish ID: {publish_id}")
    print(f"Using access token: {access_token}")
    
    result = check_upload_status(publish_id, access_token)

if __name__ == "__main__":
    main() 
