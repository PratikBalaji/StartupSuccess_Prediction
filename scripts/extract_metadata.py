import joblib
import json
import os
import sys

# Add parent directory to path to import from src if needed, 
# though we just need the pickle files here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

def extract_metadata():
    try:
        print(f"Loading models from {MODELS_DIR}...")
        label_encoders = joblib.load(os.path.join(MODELS_DIR, 'label_encoders.pkl'))
        
        industries = list(label_encoders['Industry'].classes_)
        regions = list(label_encoders['Region'].classes_)
        
        metadata = {
            'industries': industries,
            'regions': regions
        }
        
        output_path = os.path.join(DATA_DIR, 'metadata.json')
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Metadata successfully extracted to {output_path}")
        
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        sys.exit(1)

if __name__ == '__main__':
    extract_metadata()
