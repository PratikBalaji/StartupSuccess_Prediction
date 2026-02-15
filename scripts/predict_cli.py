import sys
import json
import joblib
import pandas as pd
import numpy as np
import os

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Load models (Global scope to avoid reloading on every request if we were using a persistent process, 
# but for CLI we load every time. In a production app with high load, we'd use a persistent python shell).
def load_models():
    try:
        model = joblib.load(os.path.join(MODELS_DIR, 'best_model.pkl'))
        label_encoder_y = joblib.load(os.path.join(MODELS_DIR, 'label_encoder_y.pkl'))
        label_encoders = joblib.load(os.path.join(MODELS_DIR, 'label_encoders.pkl'))
        scaler = joblib.load(os.path.join(MODELS_DIR, 'scaler.pkl'))
        return model, label_encoder_y, label_encoders, scaler
    except Exception as e:
        print(json.dumps({'error': f"Failed to load models: {str(e)}"}))
        sys.exit(1)

def predict(data):
    try:
        model, label_encoder_y, label_encoders, scaler = load_models()
        
        # Parse input
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
        
        # Transform categorical features
        industry_encoded = label_encoders['Industry'].transform([industry])[0]
        region_encoded = label_encoders['Region'].transform([region])[0]
        
        # Prepare numerical features
        numerical_features = np.array([[
            funding_rounds, funding_amount, valuation, revenue,
            employees, market_share, profitable, year_founded
        ]])
        
        # Scale numerical features
        numerical_features_scaled = scaler.transform(numerical_features)
        
        # Combine features
        categorical_features = np.array([[industry_encoded, region_encoded]])
        final_features = np.hstack((numerical_features_scaled, categorical_features))
        
        # Predict
        prediction = model.predict(final_features)
        prediction_label = label_encoder_y.inverse_transform(prediction)[0]
        
        # Probabilities
        probabilities = model.predict_proba(final_features)[0]
        prob_dict = {
            cls: round(prob * 100, 2)
            for cls, prob in zip(label_encoder_y.classes_, probabilities)
        }
        
        # Benchmarks
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
        all_features = numerical_features_list + ['Industry', 'Region']
        feature_importance = {}
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            total_importance = np.sum(importances)
            feature_importance = {
                feat: round((imp / total_importance) * 100, 2)
                for feat, imp in zip(all_features, importances)
            }
            
        result = {
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
        }
        
        print(json.dumps(result))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}))
        sys.exit(1)

if __name__ == '__main__':
    # Read input from stdin
    try:
        input_str = sys.stdin.read()
        if not input_str:
            print(json.dumps({'error': 'No input data provided'}))
            sys.exit(1)
            
        data = json.loads(input_str)
        predict(data)
    except Exception as e:
        print(json.dumps({'error': f"Input error: {str(e)}"}))
        sys.exit(1)
