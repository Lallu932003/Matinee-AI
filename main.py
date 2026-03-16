import os
import json
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from pydantic import BaseModel, Field

import openai

load_dotenv()

# Initialize the OpenAI Client configured for OpenRouter
client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

from fastapi.middleware.cors import CORSMiddleware

# ... (keep other imports and your Pydantic models the same) ...

app = FastAPI(title="Persona Evaluation API")

from fastapi.staticfiles import StaticFiles

# Add this CORS block:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the current directory as static files explicitly to serve index.html
app.mount("/app", StaticFiles(directory=".", html=True), name="static")

# ... (keep the rest of your endpoints exactly the same) ...

# ---------------------------------------------------------
# 1. DEFINE THE STRUCTURED OUTPUT SCHEMA FOR GEMINI
# ---------------------------------------------------------
class EvaluationResult(BaseModel):
    overall_rating: int = Field(description="Score from 1 to 10 on how much the persona likes the content overall.")
    attention_hook: int = Field(description="Score from 1 to 10 on how quickly the opening grabs their attention.")
    emotional_resonance: int = Field(description="Score from 1 to 10 on how deeply this moves them emotionally.")
    binge_ability: int = Field(description="Score from 1 to 10 on how likely they are to watch the next episode immediately.")
    controversy_risk: str = Field(description="Explain if anything in this content could offend or alienate this specific persona.")
    relatability_score: int = Field(description="Score from 1 to 10 on how relatable the content is to the persona.")
    would_share: bool = Field(description="True if the persona would share this with friends or their network.")
    feedback: str = Field(description="Detailed feedback written in the voice/slang of the persona.")

# ---------------------------------------------------------
# 2. DEFINE THE INPUT SCHEMAS FOR FASTAPI
# ---------------------------------------------------------
class ContentInput(BaseModel):
    content: str = Field(..., example="Yo, check out this new energy drink, it has 500mg of caffeine!")

class CustomPersonaInput(BaseModel):
    persona_description: str = Field(
        ..., 
        example="A 65-year-old retired librarian from London who loves classical music."
    )
    content: str = Field(..., example="Get 50% off our new wireless waterproof rave speakers!")

# ---------------------------------------------------------
# 3. ENDPOINTS
# ---------------------------------------------------------



@app.post("/evaluate/custom")
def evaluate_custom(data: CustomPersonaInput):
    # Dynamically inject the requested persona into the prompt
    custom_prompt = f"""
    You are a synthetic audience member with the following persona:
    {data.persona_description}

    Adopt this persona completely. Evaluate the following scripted content, film idea, or video completely strictly from your unique perspective.
    
    IMPORTANT INSTRUCTION:
    Do NOT default to a 1 to 5 scale. Use the full range from 1 to 10 to provide nuanced feedback.
    """
    
    full_prompt = f"{custom_prompt}\n\nContent to evaluate:\n{data.content}"
    print(f"DEBUG: full_prompt:\n{full_prompt}")

    response = client.chat.completions.create(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        messages=[
            {"role": "user", "content": full_prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "EvaluationResult",
                "strict": True,
                "schema": EvaluationResult.model_json_schema()
            }
        },
        temperature=0.4,
        max_tokens=2000
    )
    print (response)
    # Return parsed JSON
    return json.loads(response.choices[0].message.content)