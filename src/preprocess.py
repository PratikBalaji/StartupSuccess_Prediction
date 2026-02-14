import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib
import os

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'startup_data.csv')

def load_data():
    df = pd.read_csv(DATA_PATH)
    return df

def create_success_labels(df):
    label_map = {
        'IPO': 'High Success',
        'Acquired': 'Medium Success',
        'Private': 'Low Success'
    }
    df['Success'] = df['Exit Status'].map(label_map)
    return df

def preprocess_data(df, label_encoders=None, scaler=None, fit=True):
    df = df.copy()
    
    df = create_success_labels(df)
    
    feature_cols = [
        'Industry', 'Funding Rounds', 'Funding Amount (M USD)',
        'Valuation (M USD)', 'Revenue (M USD)', 'Employees',
        'Market Share (%)', 'Profitable', 'Year Founded', 'Region'
    ]
    
    categorical_cols = ['Industry', 'Region']
    numerical_cols = [
        'Funding Rounds', 'Funding Amount (M USD)', 'Valuation (M USD)',
        'Revenue (M USD)', 'Employees', 'Market Share (%)', 'Profitable', 'Year Founded'
    ]
    
    if fit:
        label_encoders = {}
        for col in categorical_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col])
            label_encoders[col] = le
        
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
    else:
        for col in categorical_cols:
            df[col + '_encoded'] = label_encoders[col].transform(df[col])
        df[numerical_cols] = scaler.transform(df[numerical_cols])
    
    encoded_cols = [col + '_encoded' for col in categorical_cols]
    feature_columns = numerical_cols + encoded_cols
    
    X = df[feature_columns]
    y = df['Success']
    
    return X, y, label_encoders, scaler, feature_columns

def get_feature_columns():
    return [
        'Funding Rounds', 'Funding Amount (M USD)', 'Valuation (M USD)',
        'Revenue (M USD)', 'Employees', 'Market Share (%)', 'Profitable',
        'Year Founded', 'Industry_encoded', 'Region_encoded'
    ]

if __name__ == '__main__':
    df = load_data()
    print('Data loaded:', df.shape)
    print('\nPreprocessing...')
    X, y, le, scaler, cols = preprocess_data(df)
    print('X shape:', X.shape)
    print('y distribution:')
    print(y.value_counts())
