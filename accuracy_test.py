import httpx
import json
import statistics

def test_evaluation_accuracy():
    url = "http://127.0.0.1:8000/evaluate/group"
    
    # Test personas with very different identities to check variance
    personas = [
        {"name": "Appupa", "age": 75, "gender": "Male", "job": "Retired Farmer", "location": "Palakkad", "description": "Highly traditional, values values over trend."},
        {"name": "Z-Gamer", "age": 19, "gender": "Non-binary", "job": "Streamer", "location": "Kochi", "description": "Loves fast edits, memes, and global trends."},
        {"name": "Priya", "age": 35, "gender": "Female", "job": "Yoga Instructor", "location": "Varkala", "description": "Health-conscious, calm, dislikes loud noises and aggressive marketing."},
        {"name": "Rahul", "age": 28, "gender": "Male", "job": "Tech Bro", "location": "Trivandrum", "description": "Loves gadgets, efficiency, and tech jargon. Always looking for the next big tool."},
        {"name": "Latha", "age": 50, "gender": "Female", "job": "School Principal", "location": "Kottayam", "description": "Strict, values education and discipline, highly critical of slang or casual behavior."}
    ]
    
    # Content designed to be polarizing
    content = "Yo! Check out this new ultra-loud waterproof rave speaker with flashing RGB lights! Perfect for blasting your favorite tracks at full volume and annoying the neighbors. Buy now with crypto!"
    
    payload = {
        "personas": personas,
        "content": content
    }
    
    print("\nStarting Accuracy & Variance Test...")
    print("Evaluating content designed to be polarizing across 5 diverse personas.")
    
    try:
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=120.0)
            if response.status_code == 200:
                results = response.json()
                print("\n--- ✅ Accuracy Test Results ---")
                
                scores = []
                for res in results:
                    name = res["persona_name"]
                    eval_data = res["evaluation"]
                    score = eval_data['overall_rating']
                    scores.append(score)
                    print(f"\nPersona: {name}")
                    print(f"Rating: {score}/10")
                    print(f"Feedback: {eval_data['feedback']}")
                    print("-" * 30)
                
                # Calculate True Accuracy (Variance/Spread)
                if len(scores) > 1:
                    variance = statistics.variance(scores)
                    std_dev = statistics.stdev(scores)
                    print(f"\n📊 Statistical Analysis:")
                    print(f"Average Score: {statistics.mean(scores)}")
                    print(f"Score Variance: {variance:.2f} (Higher means distinct personas)")
                    print(f"Standard Deviation: {std_dev:.2f}")
                    
                    if variance > 3:
                        print("✅ RESULT: EXCELLENT. High variance means individual API calls successfully prevented personality blending. Personas showed strong, distinct opinions!")
                    elif variance > 1:
                        print("⚠️ RESULT: OK. Some variance, but opinions were somewhat similar.")
                    else:
                        print("❌ RESULT: POOR. Low variance. The AI might be blending personas together.")
                
            else:
                print(f"Error: {response.status_code}")
                print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_evaluation_accuracy()
