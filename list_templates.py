import requests

def list_templates(api_key):
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.zapcap.ai/templates",
            headers=headers
        )
        response.raise_for_status()
        templates = response.json()
        
        print("\nAvailable Templates:")
        print("===================")
        for template in templates:
            template_id = template.get('id')
            categories = template.get('categories', [])
            preview_url = template.get('previewUrl')
            print(f"\nTemplate ID: {template_id}")
            print(f"Categories: {', '.join(categories)}")
            print(f"Preview URL: {preview_url}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    API_KEY = "bcf60d4d261e7f506087134461011e3180c10f305f8637d2a56494f1968c850b"
    list_templates(API_KEY) 