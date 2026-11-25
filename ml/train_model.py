import os
import sys
import argparse
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Ensure root directory is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from ml.preprocess import clean_and_prepare_df, build_preprocessor, FEATURE_CONFIGS

MODEL_FILENAME_MAP = {
    'cars': 'car_model.pkl',
    'bikes': 'bike_model.pkl',
    'lorries': 'lorry_model.pkl',
    'autos': 'auto_model.pkl'
}

def train_category_model(category):
    print(f"\n=======================================================")
    print(f" TRAINING RANDOM FOREST MODEL FOR CATEGORY: {category.upper()}")
    print(f"=======================================================")
    
    csv_path = Config.DATASETS.get(category)
    if not csv_path or not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset for {category} not found at {csv_path}. Run generate_datasets.py first.")
        
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} samples from {csv_path}")
    
    # Preprocess & extract features and target
    X, y = clean_and_prepare_df(df, category)
    print(f"Clean feature matrix shape: {X.shape}, Target samples: {len(y)}")
    
    # Train / Test split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Train split: {len(X_train)} samples | Test split: {len(X_test)} samples")
    
    # Build preprocessing + RandomForestRegressor pipeline
    preprocessor = build_preprocessor(category)
    rf_regressor = RandomForestRegressor(
        n_estimators=120,
        max_depth=16,
        min_samples_split=4,
        min_samples_leaf=2,
        max_features='sqrt',
        random_state=42,
        n_jobs=-1
    )
    
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', rf_regressor)
    ])
    
    print("Training Random Forest Regressor...")
    model_pipeline.fit(X_train, y_train)
    
    # Predictions and Evaluation
    y_pred_train = model_pipeline.predict(X_train)
    y_pred_test = model_pipeline.predict(X_test)
    
    mae_test = mean_absolute_error(y_test, y_pred_test)
    rmse_test = float(np.sqrt(mean_squared_error(y_test, y_pred_test)))
    r2_test = r2_score(y_test, y_pred_test)
    r2_train = r2_score(y_train, y_pred_train)
    
    print("\n---------------- MODEL EVALUATION ----------------")
    print(f" Mean Absolute Error (MAE):     Rs. {mae_test:,.2f}")
    print(f" Root Mean Squared Error (RMSE): Rs. {rmse_test:,.2f}")
    print(f" Testing R-squared (R2) Score:  {r2_test:.4f} ({r2_test*100:.2f}%)")
    print(f" Training R-squared (R2) Score: {r2_train:.4f} ({r2_train*100:.2f}%)")
    print("--------------------------------------------------")
    
    # Save model bundle
    os.makedirs(Config.MODELS_DIR, exist_ok=True)
    model_filename = MODEL_FILENAME_MAP.get(category, f"{category}_model.pkl")
    save_path = os.path.join(Config.MODELS_DIR, model_filename)
    
    bundle = {
        'pipeline': model_pipeline,
        'category': category,
        'metrics': {
            'mae': float(mae_test),
            'rmse': float(rmse_test),
            'r2': float(r2_test),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        },
        'feature_config': FEATURE_CONFIGS[category],
        'trained_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    joblib.dump(bundle, save_path)
    print(f"Successfully saved trained model bundle to: {save_path}")
    return bundle

def train_all():
    results = {}
    for cat in ['cars', 'bikes', 'lorries', 'autos']:
        bundle = train_category_model(cat)
        results[cat] = bundle['metrics']
        
    print("\n=======================================================")
    print(" ALL 4 MODELS TRAINED AND SAVED SUCCESSFULLY!")
    print("=======================================================")
    for cat, m in results.items():
        print(f" - {cat.capitalize():<8}: R2 = {m['r2']:.4f} | MAE = Rs. {m['mae']:>10,.2f} | RMSE = Rs. {m['rmse']:>10,.2f}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train Vehicle Price Prediction Models")
    parser.add_argument('--category', type=str, default='all', choices=['all', 'cars', 'bikes', 'lorries', 'autos'],
                        help="Specify vehicle category to train or 'all'")
    args = parser.parse_args()
    
    if args.category == 'all':
        train_all()
    else:
        train_category_model(args.category)
