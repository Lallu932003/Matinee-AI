import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()

YOUTH_PERSONA_PROMPT = """
You are a synthetic youth audience member (age 18–25).
Respond ONLY in valid JSON.
Think like a modern, urban youth.
"""

class ContentInput(BaseModel):
    content: str

@app.post("/evaluate/youth")
def evaluate_youth(data: ContentInput):

    full_prompt = YOUTH_PERSONA_PROMPT + "\n\n" + data.content

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_prompt,
    )

    return {"Output": response.text}
