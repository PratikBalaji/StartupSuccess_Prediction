from flask import Flask, render_template, request, jsonify
import joblib
import os
import numpy as np

app = Flask(__name__)

MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models')

model = joblib.load(os.path.join(MODELS_PATH, 'best_model.pkl'))
label_encoder_y = joblib.load(os.path.join(MODELS_PATH, 'label_encoder_y.pkl'))
label_encoders = joblib.load(os.path.join(MODELS_PATH, 'label_encoders.pkl'))
scaler = joblib.load(os.path.join(MODELS_PATH, 'scaler.pkl'))

INDUSTRIES = list(label_encoders['Industry'].classes_)
REGIONS = list(label_encoders['Region'].classes_)

@app.route('/')
def home():
    return render_template('index.html', industries=INDUSTRIES, regions=REGIONS)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        funding_rounds = float(data['funding_rounds'])
        funding_amount = float(data['funding_amount'])
        valuation = float(data['valuation'])
        revenue = float(data['revenue'])
        employees = int(data['employees'])
        market_share = float(data['market_share'])
        profitable = int(data['profitable'])
        year_founded = int(data['year_founded'])
        industry = data['industry']
        region = data['region']
        
        industry_encoded = label_encoders['Industry'].transform([industry])[0]
        region_encoded = label_encoders['Region'].transform([region])[0]
        
        features = np.array([[
            funding_rounds, funding_amount, valuation, revenue,
            employees, market_share, profitable, year_founded,
            industry_encoded, region_encoded
        ]])
        
        features_scaled = scaler.transform(features)
        
        prediction = model.predict(features_scaled)
        prediction_label = label_encoder_y.inverse_transform(prediction)[0]
        
        probabilities = model.predict_proba(features_scaled)[0]
        prob_dict = {
            label_encoder_y.classes_[i]: round(prob * 100, 2)
            for i, prob in enumerate(probabilities)
        }
        
        return jsonify({
            'prediction': prediction_label,
            'probabilities': prob_dict
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
