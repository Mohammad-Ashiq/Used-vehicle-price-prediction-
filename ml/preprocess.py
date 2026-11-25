import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

CURRENT_YEAR = 2026

# Feature schema definitions for each vehicle category
FEATURE_CONFIGS = {
    'cars': {
        'numeric': ['age', 'km_driven', 'engine_cc'],
        'categorical': ['brand', 'model', 'fuel_type', 'transmission', 'owners', 'condition', 'location'],
        'defaults': {
            'engine_cc': 1197,
            'transmission': 'Manual',
            'fuel_type': 'Petrol',
            'owners': '1st Owner',
            'condition': 'Good'
        }
    },
    'bikes': {
        'numeric': ['age', 'km_driven', 'engine_cc'],
        'categorical': ['brand', 'model', 'fuel_type', 'owners', 'condition', 'location'],
        'defaults': {
            'engine_cc': 125,
            'fuel_type': 'Petrol',
            'owners': '1st Owner',
            'condition': 'Good'
        }
    },
    'lorries': {
        'numeric': ['age', 'km_driven', 'load_capacity'],
        'categorical': ['brand', 'model', 'fuel_type', 'vehicle_type', 'owners', 'condition', 'location'],
        'defaults': {
            'load_capacity': 5.0,
            'vehicle_type': 'Light Commercial Vehicle (LCV)',
            'fuel_type': 'Diesel',
            'owners': '1st Owner',
            'condition': 'Good'
        }
    },
    'autos': {
        'numeric': ['age', 'km_driven'],
        'categorical': ['brand', 'model', 'fuel_type', 'passenger_capacity', 'owners', 'condition', 'location'],
        'defaults': {
            'passenger_capacity': '3 Seater',
            'fuel_type': 'CNG',
            'owners': '1st Owner',
            'condition': 'Good'
        }
    }
}

def clean_and_prepare_df(df, category):
    """
    Cleans raw DataFrame, handles missing values, extracts age,
    and returns feature matrix X and target vector y (if present).
    """
    df = df.copy()
    config = FEATURE_CONFIGS.get(category)
    if not config:
        raise ValueError(f"Unsupported vehicle category: {category}")
        
    # Standardize column names
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Feature Engineering: Age from Manufacturing Year
    if 'year' in df.columns:
        df['age'] = CURRENT_YEAR - pd.to_numeric(df['year'], errors='coerce').fillna(CURRENT_YEAR - 5)
        # Cap age at reasonable range
        df['age'] = df['age'].clip(lower=0, upper=30)
    elif 'age' not in df.columns:
        df['age'] = 5
        
    # Ensure numeric columns are strictly numeric and fill missing with median or defaults
    for num_col in config['numeric']:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors='coerce')
            median_val = df[num_col].median()
            default_val = config['defaults'].get(num_col, median_val if pd.notna(median_val) else 0)
            df[num_col] = df[num_col].fillna(default_val)
        else:
            df[num_col] = config['defaults'].get(num_col, 0)
            
    # Ensure categorical columns are strings and fill missing
    for cat_col in config['categorical']:
        if cat_col in df.columns:
            df[cat_col] = df[cat_col].astype(str).str.strip()
            mode_series = df[cat_col].mode()
            mode_val = mode_series.iloc[0] if not mode_series.empty else 'Unknown'
            default_val = config['defaults'].get(cat_col, mode_val)
            df[cat_col] = df[cat_col].replace({'nan': default_val, 'None': default_val, '': default_val})
        else:
            df[cat_col] = config['defaults'].get(cat_col, 'Unknown')
            
    feature_cols = config['numeric'] + config['categorical']
    X = df[feature_cols]
    
    y = None
    if 'price' in df.columns:
        y = pd.to_numeric(df['price'], errors='coerce')
        # Remove any rows with missing or zero/negative prices
        valid_idx = y.notna() & (y > 0)
        X = X.loc[valid_idx]
        y = y.loc[valid_idx]
        
    return X, y

def build_preprocessor(category):
    """
    Builds a Scikit-Learn ColumnTransformer for numeric scaling
    and categorical one-hot encoding.
    """
    config = FEATURE_CONFIGS.get(category)
    if not config:
        raise ValueError(f"Unknown category {category}")
        
    numeric_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown='ignore', sparse_output=False)
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, config['numeric']),
            ('cat', categorical_transformer, config['categorical'])
        ]
    )
    return preprocessor

def validate_and_format_input(category, form_data):
    """
    Validates form data submitted by user, converts types,
    and returns (clean_dict, error_message).
    """
    config = FEATURE_CONFIGS.get(category)
    if not config:
        return None, f"Invalid vehicle category: {category}"
        
    errors = []
    clean_data = {}
    
    # 1. Year validation
    try:
        year = int(form_data.get('year', 0))
        if year < 1995 or year > CURRENT_YEAR:
            errors.append(f"Manufacturing year must be between 1995 and {CURRENT_YEAR}.")
        clean_data['year'] = year
        clean_data['age'] = max(0, CURRENT_YEAR - year)
    except (ValueError, TypeError):
        errors.append("Invalid manufacturing year.")
        
    # 2. Kilometers Driven validation
    try:
        km = int(form_data.get('km_driven', -1))
        if km < 0 or km > 1500000:
            errors.append("Kilometers driven must be between 0 and 15,00,000 km.")
        clean_data['km_driven'] = km
    except (ValueError, TypeError):
        errors.append("Invalid kilometers driven value.")
        
    # 3. Category specific numeric fields
    if category in ['cars', 'bikes']:
        try:
            cc = int(form_data.get('engine_cc', 0))
            min_cc = 50 if category == 'bikes' else 600
            max_cc = 2500 if category == 'bikes' else 6000
            if cc < min_cc or cc > max_cc:
                errors.append(f"Engine capacity must be between {min_cc}cc and {max_cc}cc.")
            clean_data['engine_cc'] = cc
        except (ValueError, TypeError):
            errors.append("Invalid engine capacity.")
            
    if category == 'lorries':
        try:
            load = float(form_data.get('load_capacity', 0))
            if load <= 0 or load > 60:
                errors.append("Load capacity must be between 0.5 and 60 tons.")
            clean_data['load_capacity'] = load
        except (ValueError, TypeError):
            errors.append("Invalid load capacity.")
            
    # 4. Mandatory categorical fields
    for field in ['brand', 'model', 'fuel_type', 'owners', 'condition', 'location']:
        val = form_data.get(field, '').strip()
        if not val:
            errors.append(f"Please select/enter {field.replace('_', ' ').capitalize()}.")
        clean_data[field] = val
        
    if category == 'cars':
        trans = form_data.get('transmission', '').strip()
        if not trans:
            errors.append("Please select transmission type.")
        clean_data['transmission'] = trans
        
    if category == 'lorries':
        v_type = form_data.get('vehicle_type', '').strip()
        if not v_type:
            errors.append("Please select commercial vehicle type.")
        clean_data['vehicle_type'] = v_type
        
    if category == 'autos':
        pass_cap = form_data.get('passenger_capacity', '').strip()
        if not pass_cap:
            errors.append("Please select passenger capacity.")
        clean_data['passenger_capacity'] = pass_cap
        
    if errors:
        return None, " | ".join(errors)
        
    return clean_data, None
