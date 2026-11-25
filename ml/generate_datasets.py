import os
import sys
import random
import numpy as np
import pandas as pd
from datetime import datetime

# Ensure root directory is on sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config

# Set seed for reproducible realistic datasets
np.random.seed(42)
random.seed(42)

CURRENT_YEAR = 2026

# Brand Price & Spec Estimation Helpers
CAR_BRAND_BASE_TIERS = {
    'Maruti Suzuki': (650000, 1197),
    'Hyundai': (1100000, 1396),
    'Tata Motors': (1150000, 1299),
    'Mahindra': (1550000, 2179),
    'Toyota': (2200000, 2197),
    'Kia': (1350000, 1497),
    'Honda': (1250000, 1498),
    'Volkswagen': (1400000, 1498),
    'Skoda': (1500000, 1498),
    'MG (Morris Garages)': (1600000, 1490),
    'Renault': (750000, 999),
    'Nissan': (850000, 999),
    'Ford': (1100000, 1498),
    'Jeep': (2400000, 1956),
    'BMW': (5500000, 1998),
    'Mercedes-Benz': (6000000, 1993),
    'Audi': (5200000, 1984),
    'Volvo': (5800000, 1969),
    'Land Rover': (8500000, 2996),
    'Jaguar': (7200000, 1997),
    'Porsche': (11500000, 2981),
    'BYD': (3200000, 1498),
    'Citroen': (950000, 1199),
    'Force Motors': (1650000, 2596),
    'Lexus': (7500000, 2487),
    'Mini': (4400000, 1998),
    'Isuzu': (2300000, 1898)
}

BIKE_BRAND_BASE_TIERS = {
    'Hero MotoCorp': (85000, 110),
    'Honda': (95000, 125),
    'Bajaj': (140000, 160),
    'TVS': (110000, 125),
    'Royal Enfield': (220000, 349),
    'Yamaha': (155000, 155),
    'Suzuki': (115000, 125),
    'KTM': (240000, 250),
    'Kawasaki': (480000, 400),
    'Harley-Davidson': (420000, 440),
    'Triumph': (310000, 400),
    'Jawa': (215000, 334),
    'Yezdi': (225000, 334),
    'Ducati': (1250000, 803),
    'BMW Motorrad': (390000, 313),
    'Benelli': (350000, 374),
    'Aprilia': (240000, 160),
    'Vespa': (145000, 125),
    'Ather Energy': (140000, 110),
    'Ola Electric': (115000, 110),
    'Revolt Motors': (130000, 110),
    'Ultraviolette': (380000, 250),
    'Husqvarna': (260000, 250),
    'Simple Energy': (150000, 110),
    'Tork Motors': (165000, 125)
}

LORRY_BRAND_BASE_TIERS = {
    'Tata Motors': (1800000, 7.5, 'Medium Commercial Vehicle (MCV)'),
    'Ashok Leyland': (1950000, 9.0, 'Medium Commercial Vehicle (MCV)'),
    'Eicher': (1750000, 6.5, 'Medium Commercial Vehicle (MCV)'),
    'BharatBenz': (2600000, 14.0, 'Heavy Commercial Vehicle (HCV)'),
    'Mahindra Commercial': (1100000, 3.5, 'Light Commercial Vehicle (LCV)'),
    'Force Motors': (1350000, 4.0, 'Light Commercial Vehicle (LCV)'),
    'SML Isuzu': (1650000, 6.0, 'Medium Commercial Vehicle (MCV)'),
    'Volvo Trucks': (8500000, 32.0, 'Heavy Commercial Vehicle (HCV)'),
    'Scania': (9000000, 35.0, 'Heavy Commercial Vehicle (HCV)'),
    'Piaggio Commercial': (550000, 1.2, 'Light Commercial Vehicle (LCV)'),
    'Maruti Suzuki Commercial': (580000, 1.2, 'Light Commercial Vehicle (LCV)'),
    'KAMAZ': (5500000, 25.0, 'Tipper')
}

AUTO_BRAND_BASE_TIERS = {
    'Bajaj Auto': (285000, '3 Seater', 'CNG'),
    'Piaggio': (275000, '3 Seater', 'Diesel'),
    'Mahindra 3-Wheeler': (310000, '4 Seater', 'Electric'),
    'TVS': (265000, '3 Seater', 'Petrol'),
    'Atul Auto': (250000, '3 Seater', 'CNG'),
    'Saarthi': (175000, '4 Seater', 'Electric'),
    'Kinetic Green': (195000, '4 Seater', 'Electric'),
    'Euler Motors': (395000, '3 Seater', 'Electric'),
    'Montra Electric': (320000, '4 Seater', 'Electric'),
    'Terra Motors': (180000, '4 Seater', 'Electric'),
    'Lohia Auto': (185000, '4 Seater', 'Electric'),
    'Baxy Mobility': (260000, '3 Seater', 'CNG')
}

LOCATIONS = Config.LOCATIONS
OWNERS_LIST = ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner & Above']
OWNER_WEIGHTS = [0.58, 0.28, 0.11, 0.03]
OWNER_MULTIPLIERS = {'1st Owner': 1.0, '2nd Owner': 0.88, '3rd Owner': 0.77, '4th Owner & Above': 0.65}

CONDITIONS = ['Excellent', 'Good', 'Fair', 'Poor']
CONDITION_WEIGHTS = [0.35, 0.45, 0.15, 0.05]
CONDITION_MULTIPLIERS = {'Excellent': 1.12, 'Good': 1.0, 'Fair': 0.86, 'Poor': 0.70}

def generate_car_data(n_samples=2500):
    brands_info = Config.CATEGORIES_INFO['cars']['brands']
    brands = list(brands_info.keys())
    transmissions = ['Manual', 'Automatic']
    fuel_options = ['Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid']
    
    rows = []
    for _ in range(n_samples):
        brand = random.choice(brands)
        model_name = random.choice(brands_info[brand])
        base_price_avg, default_cc = CAR_BRAND_BASE_TIERS.get(brand, (1200000, 1498))
        
        # Specific model tiering
        if any(w in model_name for w in ['Fortuner', 'Defender', 'Q7', 'GLS', 'X7', 'Cayenne', 'Vellfire']):
            base_price = base_price_avg * random.uniform(1.4, 2.0)
            engine_cc = default_cc + 1000
        elif any(w in model_name for w in ['Alto', 'Kwid', 'Eeco', 'Celerio', 'Santro']):
            base_price = base_price_avg * random.uniform(0.55, 0.75)
            engine_cc = max(796, default_cc - 400)
        else:
            base_price = base_price_avg * random.uniform(0.85, 1.25)
            engine_cc = default_cc + random.choice([-100, 0, 100])

        year = random.randint(2011, 2024)
        age = CURRENT_YEAR - year
        
        km_driven = int(age * random.uniform(7000, 15000) + random.uniform(2000, 8000))
        km_driven = max(4000, min(km_driven, 195000))
        
        if 'EV' in model_name or 'Electric' in model_name or brand == 'BYD':
            fuel_type = 'Electric'
        elif any(w in model_name for w in ['CNG', 'Wagon R']):
            fuel_type = random.choice(['CNG', 'Petrol'])
        else:
            fuel_type = random.choice(['Petrol', 'Diesel', 'Petrol'])
            
        transmission = random.choice(transmissions)
        owners = random.choices(OWNERS_LIST, weights=OWNER_WEIGHTS)[0]
        condition = random.choices(CONDITIONS, weights=CONDITION_WEIGHTS)[0]
        location = random.choice(LOCATIONS)
        
        depreciated = base_price * ((1 - 0.082) ** age)
        km_factor = max(0.65, 1.0 - (km_driven / 300000.0) * 0.25)
        trans_factor = 1.08 if transmission == 'Automatic' else 1.0
        own_factor = OWNER_MULTIPLIERS[owners]
        cond_factor = CONDITION_MULTIPLIERS[condition]
        fuel_factor = 1.05 if fuel_type in ['Electric', 'Hybrid'] else (1.02 if fuel_type == 'Diesel' else 1.0)
        noise = random.uniform(0.97, 1.03)
        
        final_price = depreciated * km_factor * trans_factor * own_factor * cond_factor * fuel_factor * noise
        final_price = round(max(95000, final_price), -3)
        
        rows.append({
            'brand': brand,
            'model': model_name,
            'year': year,
            'km_driven': km_driven,
            'fuel_type': fuel_type,
            'transmission': transmission,
            'owners': owners,
            'condition': condition,
            'engine_cc': int(engine_cc),
            'location': location,
            'price': int(final_price)
        })
        
    return pd.DataFrame(rows)

def generate_bike_data(n_samples=2500):
    brands_info = Config.CATEGORIES_INFO['bikes']['brands']
    brands = list(brands_info.keys())
    
    rows = []
    for _ in range(n_samples):
        brand = random.choice(brands)
        model_name = random.choice(brands_info[brand])
        base_price_avg, default_cc = BIKE_BRAND_BASE_TIERS.get(brand, (140000, 160))
        
        # Specific model tiering
        if any(w in model_name for w in ['Hayabusa', 'Panigale', 'S 1000', 'Gold Wing', 'Fat Boy']):
            base_price = base_price_avg * random.uniform(2.5, 4.0)
            engine_cc = default_cc + 500
        elif any(w in model_name for w in ['Splendor', 'Platina', 'HF Deluxe', 'XL100', 'Shine 100']):
            base_price = base_price_avg * random.uniform(0.65, 0.85)
            engine_cc = 100
        elif any(w in model_name for w in ['Classic 350', 'Bullet 350', 'Meteor', 'Himalayan']):
            base_price = 230000 * random.uniform(0.90, 1.20)
            engine_cc = 349
        else:
            base_price = base_price_avg * random.uniform(0.85, 1.20)
            engine_cc = default_cc
            
        year = random.randint(2011, 2024)
        age = CURRENT_YEAR - year
        
        km_driven = int(age * random.uniform(4000, 10000) + random.uniform(1000, 5000))
        km_driven = max(2000, min(km_driven, 120000))
        
        if 'EV' in model_name or brand in ['Ather Energy', 'Ola Electric', 'Revolt Motors', 'Ultraviolette', 'Simple Energy', 'Tork Motors']:
            fuel_type = 'Electric'
        else:
            fuel_type = 'Petrol'
            
        owners = random.choices(OWNERS_LIST, weights=[0.65, 0.25, 0.08, 0.02])[0]
        condition = random.choices(CONDITIONS, weights=CONDITION_WEIGHTS)[0]
        location = random.choice(LOCATIONS)
        
        # Bike depreciation ~7.8% (cult bikes like Royal Enfield retain more)
        depr_rate = 0.065 if 'Royal Enfield' in brand else 0.080
        depreciated = base_price * ((1 - depr_rate) ** age)
        km_factor = max(0.60, 1.0 - (km_driven / 150000.0) * 0.30)
        own_factor = OWNER_MULTIPLIERS[owners]
        cond_factor = CONDITION_MULTIPLIERS[condition]
        noise = random.uniform(0.97, 1.03)
        
        final_price = depreciated * km_factor * own_factor * cond_factor * noise
        final_price = round(max(18000, final_price), -2)
        
        rows.append({
            'brand': brand,
            'model': model_name,
            'year': year,
            'km_driven': km_driven,
            'fuel_type': fuel_type,
            'owners': owners,
            'condition': condition,
            'engine_cc': int(engine_cc),
            'location': location,
            'price': int(final_price)
        })
        
    return pd.DataFrame(rows)

def generate_lorry_data(n_samples=1600):
    brands_info = Config.CATEGORIES_INFO['lorries']['brands']
    brands = list(brands_info.keys())
    vehicle_types = Config.CATEGORIES_INFO['lorries']['vehicle_types']
    
    rows = []
    for _ in range(n_samples):
        brand = random.choice(brands)
        model_name = random.choice(brands_info[brand])
        base_price_avg, default_load, default_type = LORRY_BRAND_BASE_TIERS.get(
            brand, (1800000, 7.5, 'Medium Commercial Vehicle (MCV)')
        )
        
        if 'Ace' in model_name or 'Dost' in model_name or 'Super Carry' in model_name or 'Porter' in model_name:
            base_price = 650000 * random.uniform(0.85, 1.15)
            load_capacity = 1.25
            vehicle_type = 'Light Commercial Vehicle (LCV)'
        elif 'Tipper' in model_name or 'Kamaz' in brand:
            base_price = 3800000 * random.uniform(0.90, 1.30)
            load_capacity = 18.0
            vehicle_type = 'Tipper'
        elif 'Volvo' in brand or 'Scania' in brand or 'Prima' in model_name or 'Signa' in model_name:
            base_price = base_price_avg * random.uniform(0.90, 1.25)
            load_capacity = default_load
            vehicle_type = 'Heavy Commercial Vehicle (HCV)'
        else:
            base_price = base_price_avg * random.uniform(0.85, 1.20)
            load_capacity = default_load
            vehicle_type = default_type
            
        year = random.randint(2011, 2024)
        age = CURRENT_YEAR - year
        
        km_driven = int(age * random.uniform(20000, 45000) + random.uniform(5000, 20000))
        km_driven = max(10000, min(km_driven, 450000))
        
        fuel_type = 'CNG' if 'CNG' in model_name else ('Electric' if 'EV' in model_name else 'Diesel')
        owners = random.choices(OWNERS_LIST, weights=[0.52, 0.32, 0.12, 0.04])[0]
        condition = random.choices(CONDITIONS, weights=CONDITION_WEIGHTS)[0]
        location = random.choice(LOCATIONS)
        
        depreciated = base_price * ((1 - 0.088) ** age)
        km_factor = max(0.58, 1.0 - (km_driven / 600000.0) * 0.30)
        own_factor = OWNER_MULTIPLIERS[owners]
        cond_factor = CONDITION_MULTIPLIERS[condition]
        noise = random.uniform(0.97, 1.03)
        
        final_price = depreciated * km_factor * own_factor * cond_factor * noise
        final_price = round(max(150000, final_price), -3)
        
        rows.append({
            'brand': brand,
            'model': model_name,
            'year': year,
            'km_driven': km_driven,
            'fuel_type': fuel_type,
            'vehicle_type': vehicle_type,
            'load_capacity': round(float(load_capacity), 1),
            'owners': owners,
            'condition': condition,
            'location': location,
            'price': int(final_price)
        })
        
    return pd.DataFrame(rows)

def generate_auto_data(n_samples=1600):
    brands_info = Config.CATEGORIES_INFO['autos']['brands']
    brands = list(brands_info.keys())
    
    rows = []
    for _ in range(n_samples):
        brand = random.choice(brands)
        model_name = random.choice(brands_info[brand])
        base_price_avg, default_pass, default_fuel = AUTO_BRAND_BASE_TIERS.get(
            brand, (280000, '3 Seater', 'CNG')
        )
        
        base_price = base_price_avg * random.uniform(0.88, 1.15)
        passenger_capacity = '6 Seater' if 'Wide' in model_name or 'Plus' in model_name else default_pass
        
        year = random.randint(2011, 2024)
        age = CURRENT_YEAR - year
        
        km_driven = int(age * random.uniform(12000, 25000) + random.uniform(3000, 10000))
        km_driven = max(5000, min(km_driven, 250000))
        
        if 'Electric' in model_name or 'EV' in model_name or default_fuel == 'Electric':
            fuel_type = 'Electric'
        elif 'Diesel' in model_name:
            fuel_type = 'Diesel'
        elif 'Petrol' in model_name:
            fuel_type = 'Petrol'
        else:
            fuel_type = 'CNG'
            
        owners = random.choices(OWNERS_LIST, weights=[0.55, 0.30, 0.11, 0.04])[0]
        condition = random.choices(CONDITIONS, weights=CONDITION_WEIGHTS)[0]
        location = random.choice(LOCATIONS)
        
        depreciated = base_price * ((1 - 0.090) ** age)
        km_factor = max(0.55, 1.0 - (km_driven / 300000.0) * 0.28)
        pass_factor = 1.08 if passenger_capacity == '6 Seater' else (1.04 if passenger_capacity == '4 Seater' else 1.0)
        own_factor = OWNER_MULTIPLIERS[owners]
        cond_factor = CONDITION_MULTIPLIERS[condition]
        fuel_factor = 1.06 if fuel_type in ['Electric', 'CNG'] else 1.0
        noise = random.uniform(0.97, 1.03)
        
        final_price = depreciated * km_factor * pass_factor * own_factor * cond_factor * fuel_factor * noise
        final_price = round(max(38000, final_price), -2)
        
        rows.append({
            'brand': brand,
            'model': model_name,
            'year': year,
            'km_driven': km_driven,
            'fuel_type': fuel_type,
            'passenger_capacity': passenger_capacity,
            'owners': owners,
            'condition': condition,
            'location': location,
            'price': int(final_price)
        })
        
    return pd.DataFrame(rows)

def main():
    target_dir = os.path.join(os.path.dirname(__file__), '..', 'dataset')
    os.makedirs(target_dir, exist_ok=True)
    
    print("Generating comprehensive realistic datasets for all 70+ brands & 36 States/UTs...")
    
    cars_df = generate_car_data(2500)
    cars_path = os.path.join(target_dir, 'cars.csv')
    cars_df.to_csv(cars_path, index=False)
    print(f"Generated {len(cars_df)} records for Cars -> {cars_path}")
    
    bikes_df = generate_bike_data(2500)
    bikes_path = os.path.join(target_dir, 'bikes.csv')
    bikes_df.to_csv(bikes_path, index=False)
    print(f"Generated {len(bikes_df)} records for Bikes -> {bikes_path}")
    
    lorries_df = generate_lorry_data(1600)
    lorries_path = os.path.join(target_dir, 'lorries.csv')
    lorries_df.to_csv(lorries_path, index=False)
    print(f"Generated {len(lorries_df)} records for Lorries -> {lorries_path}")
    
    autos_df = generate_auto_data(1600)
    autos_path = os.path.join(target_dir, 'autos.csv')
    autos_df.to_csv(autos_path, index=False)
    print(f"Generated {len(autos_df)} records for Auto-rickshaws -> {autos_path}")
    
    print("Dataset generation complete!")

if __name__ == '__main__':
    main()
