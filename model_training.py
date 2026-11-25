"""
model_training.py
=================
Machine Learning Training Pipeline for Used Vehicle Price Prediction System.
Trains dedicated Random Forest Regression models for four vehicle categories:
1. Car
2. Lorry
3. Bike
4. Auto-rickshaw

Key ML Best Practices:
- Strict featurization ordering (Train/Test split BEFORE pipeline fitting)
- Sklearn Pipeline with ColumnTransformer for clean numerical scaling and one-hot encoding
- Evaluation using MAE, RMSE, and R-squared on unseen test sets
- Capture of feature bounds to enable out-of-range input detection during user inference
- Model serialization via Joblib
- Re-trainable with custom/real-world CSV datasets
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# Paths configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Category configurations
CATEGORY_CONFIGS = {
    "car": {
        "title": "Car",
        "csv_file": os.path.join(DATA_DIR, "car_data.csv"),
        "model_file": os.path.join(MODELS_DIR, "car_model.joblib"),
        "numerical_features": ["manufacturing_year", "kilometers_driven", "engine_capacity", "number_of_owners"],
        "categorical_features": ["brand", "model", "fuel_type", "transmission_type", "vehicle_condition"],
        "target": "resale_price"
    },
    "lorry": {
        "title": "Lorry",
        "csv_file": os.path.join(DATA_DIR, "lorry_data.csv"),
        "model_file": os.path.join(MODELS_DIR, "lorry_model.joblib"),
        "numerical_features": ["manufacturing_year", "kilometers_driven", "load_capacity_tonnes", "number_of_owners"],
        "categorical_features": ["brand", "fuel_type", "vehicle_type", "vehicle_condition"],
        "target": "resale_price"
    },
    "bike": {
        "title": "Bike",
        "csv_file": os.path.join(DATA_DIR, "bike_data.csv"),
        "model_file": os.path.join(MODELS_DIR, "bike_model.joblib"),
        "numerical_features": ["manufacturing_year", "kilometers_driven", "engine_capacity", "number_of_owners"],
        "categorical_features": ["brand", "model", "fuel_type", "vehicle_condition"],
        "target": "resale_price"
    },
    "auto": {
        "title": "Auto-rickshaw",
        "csv_file": os.path.join(DATA_DIR, "auto_data.csv"),
        "model_file": os.path.join(MODELS_DIR, "auto_model.joblib"),
        "numerical_features": ["manufacturing_year", "kilometers_driven", "number_of_owners"],
        "categorical_features": ["brand", "fuel_type", "passenger_or_cargo", "vehicle_condition"],
        "target": "resale_price"
    }
}


def ensure_datasets_exist():
    """Checks if dataset CSVs exist; generates them if missing."""
    missing = False
    for cat, cfg in CATEGORY_CONFIGS.items():
        if not os.path.exists(cfg["csv_file"]):
            missing = True
            break
    if missing:
        print("[INFO] One or more datasets not found. Generating sample demonstration datasets...")
        import generate_datasets
        generate_datasets.generate_car_data()
        generate_datasets.generate_lorry_data()
        generate_datasets.generate_bike_data()
        generate_datasets.generate_auto_data()
        print("[SUCCESS] Demonstration datasets generated successfully.")


def create_preprocessor(numerical_features, categorical_features):
    """
    Builds a scikit-learn ColumnTransformer for preprocessing.
    Uses median imputation + StandardScaler for numerical columns.
    Uses most_frequent imputation + OneHotEncoder for categorical columns.
    """
    num_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    # Compatibility check for sparse_output across sklearn versions
    try:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        ohe = OneHotEncoder(handle_unknown="ignore", sparse=False)

    cat_pipeline = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", ohe)
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numerical_features),
            ("cat", cat_pipeline, categorical_features)
        ],
        remainder="drop"
    )
    return preprocessor


def train_category_model(category_key):
    """
    Trains, evaluates, and saves a Random Forest model for a specific vehicle category.
    Returns metrics dict and saved bundle path.
    """
    cfg = CATEGORY_CONFIGS[category_key]
    csv_file = cfg["csv_file"]
    print(f"\n=======================================================")
    print(f"Training Model for: {cfg['title'].upper()} ({csv_file})")
    print(f"=======================================================")

    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"Dataset file not found: {csv_file}")

    df = pd.read_csv(csv_file)
    num_cols = cfg["numerical_features"]
    cat_cols = cfg["categorical_features"]
    target_col = cfg["target"]

    # Verify column presence
    expected_cols = num_cols + cat_cols + [target_col]
    missing_cols = [c for c in expected_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in {csv_file}: {missing_cols}")

    # Drop rows missing the target variable
    df = df.dropna(subset=[target_col])
    X = df[num_cols + cat_cols]
    y = df[target_col]

    # Calculate training feature bounds for out-of-bounds warning during inference
    bounds = {}
    for col in num_cols:
        bounds[col] = {
            "min": float(X[col].min()),
            "max": float(X[col].max()),
            "median": float(X[col].median()),
            "q25": float(X[col].quantile(0.25)),
            "q75": float(X[col].quantile(0.75))
        }
    for col in cat_cols:
        bounds[col] = {
            "unique": list(X[col].dropna().unique())
        }

    # Strict featurization: train/test split BEFORE fitting preprocessor
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )

    preprocessor = create_preprocessor(num_cols, cat_cols)

    # Random Forest Regressor with balanced parameters
    model = RandomForestRegressor(
        n_estimators=120,
        max_depth=16,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    full_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", model)
    ])

    # Fit pipeline strictly on training data
    full_pipeline.fit(X_train, y_train)

    # Evaluation on unseen test split
    y_pred = full_pipeline.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)

    # Mean absolute percentage error
    mape = np.mean(np.abs((y_test - y_pred) / np.maximum(y_test, 1))) * 100

    print(f"Evaluation Metrics on Test Set (N={len(X_test)}):")
    print(f"  - Mean Absolute Error (MAE):     INR {mae:,.2f}")
    print(f"  - Root Mean Squared Error (RMSE): INR {rmse:,.2f}")
    print(f"  - R² Score:                      {r2:.4f} ({r2*100:.1f}%)")
    print(f"  - Mean Abs Percentage Err (MAPE): {mape:.2f}%")

    # Package model metadata and validation artifacts
    bundle = {
        "pipeline": full_pipeline,
        "category": category_key,
        "category_title": cfg["title"],
        "feature_columns": num_cols + cat_cols,
        "numerical_features": num_cols,
        "categorical_features": cat_cols,
        "target": target_col,
        "training_bounds": bounds,
        "metrics": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "mape": float(mape),
            "total_samples": int(len(df)),
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test))
        },
        "is_synthetic_demonstration": True,
        "algorithm": "Random Forest Regressor (n_estimators=120, max_depth=16)"
    }

    joblib.dump(bundle, cfg["model_file"])
    print(f"Saved model bundle to: {cfg['model_file']}")
    return bundle


def train_all_models():
    """Trains all four vehicle category models."""
    ensure_datasets_exist()
    results = {}
    for cat in CATEGORY_CONFIGS.keys():
        results[cat] = train_category_model(cat)
    print("\n=======================================================")
    print("ALL VEHICLE MODELS SUCCESSFULLY TRAINED AND SAVED!")
    print("=======================================================\n")
    return results


if __name__ == "__main__":
    train_all_models()
