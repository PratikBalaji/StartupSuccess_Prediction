from flask import Flask, render_template, request, jsonify
import joblib
import os
import numpy as np

app = Flask(__name__)

MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

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
        
        # Numerical features (8)
        numerical_features = np.array([[
            funding_rounds, funding_amount, valuation, revenue,
            employees, market_share, profitable, year_founded
        ]])
        
        # Scale numerical features
        numerical_features_scaled = scaler.transform(numerical_features)
        
        # Encoded categorical features (2)
        categorical_features = np.array([[industry_encoded, region_encoded]])
        
        # Combine features (8 + 2 = 10)
        final_features = np.hstack((numerical_features_scaled, categorical_features))
        
        prediction = model.predict(final_features)
        prediction_label = label_encoder_y.inverse_transform(prediction)[0]
        
        probabilities = model.predict_proba(final_features)[0]
        prob_dict = {
            label_encoder_y.classes_[i]: round(prob * 100, 2)
            for i, prob in enumerate(probabilities)
        }
        
        
        # Benchmarks (using scaler means for numerical stats)
        # Note: scaler.mean_ corresponds to the 8 numerical columns in order
        numerical_features_list = [
            'Funding Rounds', 'Funding Amount (M USD)', 'Valuation (M USD)', 
            'Revenue (M USD)', 'Employees', 'Market Share (%)', 
            'Profitable', 'Year Founded'
        ]
        
        benchmarks = {
            feat: round(val, 2) 
            for feat, val in zip(numerical_features_list, scaler.mean_)
        }
        
        # Feature Importance
        # Feature names corresponding to the 10 features passed to model
        all_features = numerical_features_list + ['Industry', 'Region']
        
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            # Normalize to percentage
            total_importance = np.sum(importances)
            feature_importance = {
                feat: round((imp / total_importance) * 100, 2)
                for feat, imp in zip(all_features, importances)
            }
        
        return jsonify({
            'prediction': prediction_label,
            'probabilities': prob_dict,
            'feature_importance': feature_importance,
            'benchmarks': benchmarks,
            'user_input': {
                'Funding Rounds': funding_rounds,
                'Funding Amount (M USD)': funding_amount,
                'Valuation (M USD)': valuation,
                'Revenue (M USD)': revenue,
                'Employees': employees,
                'Market Share (%)': market_share,
                'Profitable': profitable,
                'Year Founded': year_founded
            }
        })
    
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
