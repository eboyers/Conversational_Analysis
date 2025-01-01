import subprocess
import requests

def run_medlm(query, model_type):
    """
    Defines the usage of MedLM (medium or large)
    """
    access_token = subprocess.check_output(["gcloud", "auth", "print-access-token"]).strip().decode('UTF-8')
    url = f'https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/google/models/medlm-{model_type}:predict'
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json; charset=utf-8"}

    request_json = {
        "instances": [
            {
                "content": query
            },
        ],
        "parameters": { # fine-tune here
            "temperature": 0,
            "maxOutputTokens": 1024,
            "topK": 40,
            "topP": 0.8,
        }
    }

    try:
        response = requests.post(url=url, headers=headers, json=request_json)
        output = response.json()['predictions'][0]['content'].strip()
        
    except requests.RequestException:
        print("REQUESTS ERROR")
    
    return output
