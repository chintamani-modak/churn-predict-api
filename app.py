from fastapi import FastAPI, Request
from pydantic import BaseModel
import pickle
import uvicorn
import os

# Load model from local file
with open("rf_churn_model.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI()

# ✅ Health check endpoint for Render
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Define input schema
class ChurnInput(BaseModel):
    recency_days: int
    frequency: int
    tenure_days: int
    avg_order_value: float
    total_spent: float

@app.post("/predict")
async def predict_churn(data: ChurnInput):
    features = [[
        data.recency_days,
        data.frequency,
        data.tenure_days,
        data.avg_order_value,
        data.total_spent
    ]]

    churn_prob = model.predict_proba(features)[0][1]
    churn_label = "High" if churn_prob > 0.7 else "Medium" if churn_prob > 0.4 else "Safe"

    return {
        "churn_score": round(float(churn_prob), 2),
        "churn_label": churn_label
    }

# Optional for local testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render injects PORT env var
    uvicorn.run(app, host="0.0.0.0", port=port)
