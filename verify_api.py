import httpx
import json

url = "http://127.0.0.1:8000/app"
try:
    with httpx.Client() as client:
        response = client.get(url, timeout=10.0)
        print(f"GET /app: {response.status_code}")
except Exception as e:
    print(f"GET /app Error: {e}")

url_eval = "http://127.0.0.1:8000/evaluate/custom"
payload = {
    "persona_description": "A tech-savvy teenager who loves anime.",
    "content": "Check out this new cyberpunk-themed energy drink with RGB lighting on the can!"
}

try:
    with httpx.Client() as client:
        response = client.post(url_eval, json=payload, timeout=30.0)
        print(f"POST /evaluate/custom: {response.status_code}")
        if response.status_code != 200:
            print(response.text)
        else:
            print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"POST /evaluate/custom Error: {e}")
