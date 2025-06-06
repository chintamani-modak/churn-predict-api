import os
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

class PredictionPayload(BaseModel):
    customer_id: str  # changed from int to str
    risk_score: float
    risk_level: str
    gpt_insight: str = None

@app.post("/update-churn")
async def update_churn(payload: PredictionPayload):
    # Early response for API speed
    response_payload = {
        "status": "queued",
        "customer_id": payload.customer_id,
        "risk_score": payload.risk_score,
        "risk_level": payload.risk_level
    }

    try:
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

        # Update using the actual customer_id column (which is a string)
        requests.patch(
            f"{SUPABASE_URL}/rest/v1/customers_new_table?customer_id=eq.{payload.customer_id}",
            headers=headers,
            data=json.dumps(data),
            timeout=5
        )
    except Exception as e:
        response_payload["warning"] = f"Supabase update failed: {str(e)}"

    return response_payload

