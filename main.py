import os
import json
import requests
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

class PredictionPayload(BaseModel):
    customer_id: str
    risk_score: float
    risk_level: str
    gpt_insight: str = None

@app.post("/update-churn")
async def update_churn(payload: PredictionPayload):
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

        # ✅ PATCH to the new table
        supabase_url = f"{SUPABASE_URL}/rest/v1/customers_new_table?customer_id=eq.{payload.customer_id}"

        r = requests.patch(
            supabase_url,
            headers=headers,
            data=json.dumps(data),
            timeout=5
        )

        response_payload["supabase_status"] = r.status_code
        response_payload["supabase_response"] = r.text

    except Exception as e:
        response_payload["warning"] = f"Supabase update failed: {str(e)}"

    return response_payload


