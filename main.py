
import os
import json
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

class PredictionPayload(BaseModel):
    customer_id: int
    risk_score: float
    risk_level: str
    gpt_insight: str = None

@app.post("/update-churn")
async def update_churn(payload: PredictionPayload):
    headers = {
        "apikey": SUPABASE_API_KEY,
        "Authorization": f"Bearer {SUPABASE_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "risk_score": payload.risk_score,
        "risk_level": payload.risk_level
    }

    if payload.gpt_insight:
        data["gpt_insight"] = payload.gpt_insight

    response = requests.patch(
        f"{SUPABASE_URL}/rest/v1/customers?id=eq.{payload.customer_id}",
        headers=headers,
        data=json.dumps(data)
    )

    return {
        "status": "success" if response.status_code == 204 else "failed",
        "supabase_status": response.status_code,
        "supabase_response": response.text
    }

@app.get("/health")
def health():
