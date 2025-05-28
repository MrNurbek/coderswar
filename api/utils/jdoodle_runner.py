import requests
from django.conf import settings

def run_csharp_jdoodle(code: str, stdin: str):
    payload = {
        "clientId": settings.JD_CLIENT_ID,
        "clientSecret": settings.JD_CLIENT_SECRET,
        "script": code,
        "language": "csharp",
        "versionIndex": "4",  # C# versiyasi
        "stdin": stdin
    }

    try:
        response = requests.post("https://api.jdoodle.com/v1/execute", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"JDoodle status: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}
