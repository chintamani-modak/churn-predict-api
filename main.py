import os
import json
import requests
from fastapi import FastAPI
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
    """
    Updates churn prediction info for a customer in Supabase.
    Responds immediately to avoid Pipedream timeouts.
    """
    # Immediate response to prevent timeout
    response_payload = {
        "status": "queued",
        "customer_id": payload.customer_id,
        "risk_score": payload.risk_score,
        "risk_level": payload.risk_level
    }

    # Supabase update (fire-and-forget style)
    try:
        headers = {
            "apikey": SUPABASE_API_KEY,
            "Authorization": f"Bearer {SUPABASE_API_KEY}",
            "Content-Type": "application/json"
        }

        update_data = {
            "risk_score": payload.risk_score,
            "risk_level": payload.risk_level
        }

        if payload.gpt_insight:
            update_data["gpt_insight"] = payload.gpt_insight

        supabase_url = f"{SUPABASE_URL}/rest/v1/customers?id=eq.{payload.customer_id}"

        # Debug print (you can remove later)
        print(f"[DEBUG] PATCH to {supabase_url} with data: {update_data}")

        response = requests.patch(
            supabase_url,
            headers=headers,
            data=json.dumps(update_data),
            timeout=5
        )

        response_payload["supabase_status"] = response.status_code
        response_payload["supabase_response"] = response.text

        if response.status_code != 204:
            response_payload["warning"] = "Supabase update may have failed. Check permissions and ID."

    except Exception as e:
        response_payload["error"] = f"Supabase PATCH failed: {str(e)}"

    return response_payload
