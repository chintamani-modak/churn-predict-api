
from flask import Flask, request, jsonify
import joblib
import numpy as np

# Load the trained model
model = joblib.load("churn_model_enriched.pkl")

# Create the Flask app
app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = ['recency', 'frequency', 'tenure', 'avg_order_value']
        X = np.array([[data[feature] for feature in features]])
        prob = model.predict_proba(X)[0][1]
        label = "High Risk" if prob > 0.6 else "Safe"
        return jsonify({
            "churn_score": round(float(prob), 2),
            "churn_label": label
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
