import httpx
import json

def test_persona_consistency():
    url = "http://127.0.0.1:8000/evaluate/group"
    
    # Test personas with very different identities
    personas = [
        {"name": "Appupa", "age": 75, "gender": "Male", "job": "Retired Farmer", "location": "Palakkad", "description": "Highly traditional, values values over trend."},
        {"name": "Z-Gamer", "age": 19, "gender": "Non-binary", "job": "Streamer", "location": "Kochi", "description": "Loves fast edits, memes, and global trends."}
    ]
    
    content = "A slow-paced, 15-minute documentary about the history of traditional Kerala temple architecture with classical music."
    
    payload = {
        "personas": personas,
        "content": content
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=60.0)
            if response.status_code == 200:
                results = response.json()
                print("--- Verification Results ---")
                for res in results:
                    name = res["persona_name"]
                    eval_data = res["evaluation"]
                    print(f"Persona: {name}")
                    print(f"Rating: {eval_data['overall_rating']}/10")
                    print(f"Feedback: {eval_data['feedback']}")
                    print("-" * 20)
                
                # Basic check: Appupa should probably rate higher or at least different from Z-Gamer
                # and the feedback should reflect their identity.
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_persona_consistency()
