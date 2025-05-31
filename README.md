# Churn Predict API

This is a lightweight Flask-based API for predicting customer churn, designed for B2C SMBs in the Intimate Wellness and Pharma sectors. The model uses behavioral data (Recency, Frequency, Tenure, Avg Order Value) to score churn risk.

## 🔍 Features

- Input: Recency, Frequency, Tenure, Avg Order Value
- Output: Churn Score (0 to 1) and Churn Label ("High Risk" or "Safe")
- Trained using XGBoost on synthetic industry-aligned data
- RESTful POST endpoint `/predict`
- Ready for deployment on Render.com or Railway

## 📦 API Usage

### Endpoint

```
POST /predict
```

### Input JSON

```json
{
  "recency": 30,
  "frequency": 5,
  "tenure": 12,
  "avg_order_value": 85.0
}
```

### Response JSON

```json
{
  "churn_score": 0.72,
  "churn_label": "High Risk"
}
```

## 🚀 Deployment (on Render.com)

1. Push code to GitHub
2. Go to https://render.com and click "New Web Service"
3. Use the following settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python app.py`

## 🧠 Model Training

The model is trained on synthetic enriched churn data using XGBoost.
To retrain or adjust, edit `app.py` to accept different features or retrain using `churn_model_enriched.pkl`.

## 📜 License

MIT License. For demo and learning use.
