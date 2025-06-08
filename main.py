import os
import json
import joblib
import requests
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from xgboost import XGBClassifier, Booster, DMatrix

app = FastAPI()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_API_KEY = os.getenv("SUPABASE_API_KEY")

# Load model and artifacts
model = None
scaler = None

try:
    booster = Booster()
    booster.load_model("xgb_model.json")  # load XGBoost booster directly

    model = XGBClassifier()
    model._Booster = booster
    model.n_classes_ = 2  # required for predict_proba
    model._le = None  # workaround for label encoder bug in newer XGBoost

    scaler = joblib.load("scaler.pkl")
    print("✅ Model and scaler loaded successfully.")
except Exception as e:
    print("❌ Error loading model:", str(e))

# ====== Endpoint 1: Predict churn risk ======
class PredictPayload(BaseModel):
    recency: float
    frequency: float
    tenure: float
    aov: float
    total_spent: float

@app.post("/predict")
async def predict(payload: PredictPayload):
    if model is None or scaler is None:
        return {"error": "Model or scaler not loaded on server."}

    try:
        raw = np.array([[payload.recency, payload.frequency, payload.tenure, payload.aov, payload.total_spent]])
        print("🚀 INPUT FEATURES:", raw)

        features_scaled = scaler.transform(raw)
        probability = model.predict_proba(features_scaled)[0][1]

        risk_score = round(float(probability), 2)
        if risk_score > 0.7:
            risk_level = "High"
        elif risk_score > 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "risk_score": risk_score,
            "risk_level": risk_level
        }

    except Exception as e:
        return {"error": f"Prediction error: {str(e)}"}

# ====== Endpoint 2: Update Supabase with churn results ======
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



 



