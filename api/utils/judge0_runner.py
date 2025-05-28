import requests
from django.conf import settings

def run_code_judge0(code: str, stdin: str, expected_output: str):
    url = "https://judge0-ce.p.rapidapi.com/submissions"
    querystring = {"base64_encoded": "false", "wait": "true"}

    payload = {
        "language_id": 51,  # 51 — C# .NET Core
        "source_code": code,
        "stdin": stdin,
        "expected_output": expected_output
    }

    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": settings.JUDGE0_API_KEY,
        "X-RapidAPI-Host": settings.JUDGE0_API_HOST
    }

    try:
        response = requests.post(url, json=payload, headers=headers, params=querystring)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

