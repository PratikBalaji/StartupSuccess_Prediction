import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocess import load_data, preprocess_data

MODELS_PATH = os.path.join(os.path.dirname(__file__), '..', 'models')

def train_models():
    print('Loading data...')
    df = load_data()
    
    print('Preprocessing data...')
    X, y, label_encoders, scaler, feature_columns = preprocess_data(df)
    
    label_encoder_y = LabelEncoder()
    y_encoded = label_encoder_y.fit_transform(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    print(f'Training set: {X_train.shape[0]} samples')
    print(f'Test set: {X_test.shape[0]} samples')
    print(f'Classes: {label_encoder_y.classes_}')
    
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
        'XGBoost': xgb.XGBClassifier(n_estimators=100, random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
    }
    
    results = {}
    best_model = None
    best_score = 0
    
    print('\n' + '='*50)
    print('Training and evaluating models...')
    print('='*50)
    
    for name, model in models.items():
        print(f'\n{name}:')
        
        model.fit(X_train, y_train)
        
        train_score = model.score(X_train, y_train)
        test_score = model.score(X_test, y_test)
        
        cv_scores = cross_val_score(model, X, y_encoded, cv=5)
        
        print(f'  Train Accuracy: {train_score:.4f}')
        print(f'  Test Accuracy: {test_score:.4f}')
        print(f'  CV Score: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})')
        
        results[name] = {
            'train_score': train_score,
            'test_score': test_score,
            'cv_score': cv_scores.mean()
        }
        
        if test_score > best_score:
            best_score = test_score
            best_model = model
            best_model_name = name
    
    print('\n' + '='*50)
    print(f'Best Model: {best_model_name} (Test Accuracy: {best_score:.4f})')
    print('='*50)
    
    print(f'\nClassification Report for {best_model_name}:')
    y_pred = best_model.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=label_encoder_y.classes_))
    
    print('\nConfusion Matrix:')
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    print('\nSaving models and preprocessors...')
    os.makedirs(MODELS_PATH, exist_ok=True)
    
    joblib.dump(best_model, os.path.join(MODELS_PATH, 'best_model.pkl'))
    joblib.dump(label_encoder_y, os.path.join(MODELS_PATH, 'label_encoder_y.pkl'))
    joblib.dump(label_encoders, os.path.join(MODELS_PATH, 'label_encoders.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_PATH, 'scaler.pkl'))
    
    print('\nModels saved successfully!')
    
    return best_model, label_encoder_y, label_encoders, scaler, feature_columns

if __name__ == '__main__':
    train_models()
