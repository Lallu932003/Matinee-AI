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
# 1. DEFINE THE STRUCTURED OUTPUT SCHEMAS
# ---------------------------------------------------------
class EvaluationResult(BaseModel):
    generated_name: str = Field(description="The persona's name.")
    estimated_age: int = Field(description="The age of this persona.")
    inferred_gender: str = Field(description="The gender of this persona.")
    overall_rating: int = Field(description="Score from 1 to 10.")
    attention_hook: int = Field(description="Score from 1 to 10.")
    emotional_resonance: int = Field(description="Score from 1 to 10.")
    binge_ability: int = Field(description="Score from 1 to 10.")
    controversy_risk: str = Field(description="Any alienation risk.")
    relatability_score: int = Field(description="Score from 1 to 10.")
    would_share: bool = Field(description="True if they would share.")
    feedback: str = Field(description="One or two sentences of feedback in normal English.")

class PersonaRecommendation(BaseModel):
    name: str
    age: int
    gender: str
    job: str
    location: str = "Kerala, India"
    description: str = Field(description="A brief description of their typical viewing habits and personality.")

class PersonaGroupResponse(BaseModel):
    personas: list[PersonaRecommendation]

class GroupEvaluationResult(BaseModel):
    results: list[EvaluationResult]

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

class PersonaGenerationInput(BaseModel):
    group_name: str
    age_range: str
    gender: str = "Any"
    additional_details: str = ""
    count: int = 10

class GroupEvaluationInput(BaseModel):
    personas: list[PersonaRecommendation]
    content: str

# ---------------------------------------------------------
# 3. ENDPOINTS
# ---------------------------------------------------------

@app.post("/personas/generate")
def generate_personas(data: PersonaGenerationInput):
    prompt = f"""
    Generate {data.count} unique synthetic audience members for a persona group named '{data.group_name}'.
    Target Age Range: {data.age_range}
    Gender: {data.gender}
    Location: All must be based in Kerala, India.
    Additional Context: {data.additional_details}

    Each persona should have a unique professional background, interest, and personality that fits within the group description but feels like a real individual from Kerala.
    """
    
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[{"role": "user", "content": prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "PersonaGroupResponse",
                "strict": True,
                "schema": PersonaGroupResponse.model_json_schema()
            }
        },
        max_tokens=2048
    )
    return json.loads(response.choices[0].message.content)

@app.post("/evaluate/custom")
def evaluate_custom(data: CustomPersonaInput):
    custom_prompt = f"""
    You are a synthetic audience member with the following persona:
    {data.persona_description}

    Adopt this persona. Evaluate the content strictly from your perspective.
    
    IMPORTANT:
    Feedback MUST be in normal English and ONLY one or two sentences.
    Scores MUST be on a scale of 1 to 10.
    """
    
    full_prompt = f"{custom_prompt}\n\nContent to evaluate:\n{data.content}"
    print(f"DEBUG: full_prompt:\n{full_prompt}")

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[{"role": "user", "content": full_prompt}],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "EvaluationResult",
                "strict": True,
                "schema": EvaluationResult.model_json_schema()
            }
        },
        temperature=0.2,
        max_tokens=1024
    )
    print (response)
    # Return parsed JSON
    return json.loads(response.choices[0].message.content)

@app.post("/evaluate/group")
def evaluate_group(data: GroupEvaluationInput):
    from concurrent.futures import ThreadPoolExecutor

    def evaluate_single_persona(persona):
        custom_prompt = f"""
        You are a synthetic audience member with the following persona:
        Name: {persona.name}
        Age: {persona.age}
        Gender: {persona.gender}
        Job: {persona.job}
        Location: {persona.location}
        Description: {persona.description}

        Adopt this persona. Evaluate the content strictly from your perspective.
        
        IMPORTANT:
        Feedback MUST be in normal English and ONLY one or two sentences.
        Scores MUST be on a scale of 1 to 10.
        """
        
        full_prompt = f"{custom_prompt}\n\nContent to evaluate:\n{data.content}"
        
        try:
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=[{"role": "user", "content": full_prompt}],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "EvaluationResult",
                        "strict": True,
                        "schema": EvaluationResult.model_json_schema()
                    }
                },
                temperature=0.2,
                max_tokens=1024
            )
            eval_data = json.loads(response.choices[0].message.content)
            
            # Print evaluation output to terminal after each call as requested by user
            print(f"\n--- Evaluated for {persona.name} ---")
            print(f"Overall Rating: {eval_data['overall_rating']}/10")
            print(f"Feedback: {eval_data['feedback']}")
            
            return {
                "persona_name": persona.name,
                "evaluation": eval_data
            }
        except Exception as e:
            print(f"Error evaluating {persona.name}: {e}")
            return None

    formatted_results = []
    print(f"\nStarting individual API evaluations for {len(data.personas)} personas...")
    
    # Run API calls concurrently for faster processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(evaluate_single_persona, data.personas))
        
    for res in results:
        if res:
            formatted_results.append(res)
            
    return formatted_results