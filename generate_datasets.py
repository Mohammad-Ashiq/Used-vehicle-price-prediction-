"""
generate_datasets.py
====================
Dataset Generator for Used Vehicle Price Prediction and Analysis System (India).
Generates realistic demonstration datasets for:
1. Car
2. Lorry (Commercial Truck)
3. Bike (Two-wheeler)
4. Auto-rickshaw (Three-wheeler)

These datasets emulate real Indian automotive market trends, including brand premiums,
mileage depreciation, age decay, fuel pricing dynamics, vehicle condition, and load capacity.
Users can replace these CSVs with real-world scraped or survey data at any time.
"""

import os
import numpy as np
import pandas as pd

# Set fixed seed for reproducibility
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)


# ==============================================================================
# 1. CAR DATASET GENERATOR
# ==============================================================================
def generate_car_data(n_samples=1800):
    brands_models = {
        "Maruti Suzuki": [("Swift", 1200, 650000), ("Baleno", 1200, 720000), ("Dzire", 1200, 700000), ("Brezza", 1500, 950000), ("Alto", 800, 380000), ("WagonR", 1000, 560000)],
        "Hyundai": [("i20", 1200, 780000), ("Creta", 1500, 1250000), ("Verna", 1500, 1180000), ("Grand i10", 1200, 620000), ("Venue", 1200, 880000)],
        "Tata": [("Nexon", 1200, 920000), ("Tiago", 1200, 580000), ("Altroz", 1200, 710000), ("Harrier", 2000, 1750000), ("Safari", 2000, 1950000)],
        "Mahindra": [("Thar", 2000, 1500000), ("Scorpio-N", 2200, 1650000), ("XUV700", 2000, 1850000), ("Bolero", 1500, 890000)],
        "Honda": [("City", 1500, 1250000), ("Amaze", 1200, 750000)],
        "Toyota": [("Innova Crysta", 2400, 2100000), ("Fortuner", 2800, 3600000), ("Glanza", 1200, 730000), ("Urban Cruiser", 1500, 980000)],
        "Kia": [("Seltos", 1500, 1300000), ("Sonet", 1200, 910000), ("Carens", 1500, 1150000)],
        "Ford": [("EcoSport", 1500, 900000), ("Endeavour", 2000, 3100000), ("Figo", 1200, 590000)],
        "Renault": [("Kwid", 1000, 480000), ("Triber", 1000, 680000), ("Kiger", 1000, 750000)],
        "Volkswagen": [("Polo", 1000, 760000), ("Taigun", 1000, 1350000), ("Vento", 1500, 1050000)]
    }

    brand_list = list(brands_models.keys())
    data = []
    current_year = 2026

    for _ in range(n_samples):
        brand = np.random.choice(brand_list, p=[0.22, 0.18, 0.16, 0.12, 0.08, 0.08, 0.07, 0.04, 0.03, 0.02])
        model_info = brands_models[brand][np.random.choice(len(brands_models[brand]))]
        model_name, default_cc, base_original_price = model_info

        # Manufacturing year: 2008 to 2025
        year = int(np.random.choice(range(2008, 2026), p=[
            0.02, 0.02, 0.03, 0.03, 0.04, 0.05, 0.06, 0.07,
            0.08, 0.09, 0.10, 0.11, 0.11, 0.09, 0.06, 0.03, 0.01, 0.00
        ]))
        age = current_year - year

        # Kilometers driven based on age with noise
        avg_km_per_year = np.random.uniform(7000, 16000)
        km_driven = int(max(2000, min(260000, age * avg_km_per_year + np.random.normal(0, 8000))))

        # Fuel type
        if "Electric" in model_name or brand in ["Tata"] and np.random.rand() < 0.08:
            fuel = "Electric"
        else:
            fuel = np.random.choice(["Petrol", "Diesel", "CNG"], p=[0.58, 0.32, 0.10])

        # Transmission type
        transmission = np.random.choice(["Manual", "Automatic"], p=[0.72, 0.28])

        # Previous owners: correlated with age
        if age <= 2:
            owners = np.random.choice([1, 2], p=[0.92, 0.08])
        elif age <= 6:
            owners = np.random.choice([1, 2, 3], p=[0.65, 0.30, 0.05])
        else:
            owners = np.random.choice([1, 2, 3, 4], p=[0.40, 0.38, 0.17, 0.05])

        # Vehicle condition
        condition = np.random.choice(["Excellent", "Good", "Fair", "Poor"], p=[0.25, 0.45, 0.22, 0.08])

        # Engine capacity
        engine_capacity = int(default_cc + np.random.choice([-100, 0, 100]) if default_cc > 1000 else default_cc)

        # Resale price calculation with realistic Indian market depreciation
        # Base annual depreciation (approx 8-11% compounded)
        depreciation_factor = (1 - 0.095) ** age
        # Mileage penalty (approx 1.5% drop per 15,000 km beyond baseline)
        km_factor = max(0.45, 1.0 - (km_driven / 300000.0) * 0.4)
        # Condition multiplier
        cond_map = {"Excellent": 1.10, "Good": 1.00, "Fair": 0.86, "Poor": 0.70}
        # Owner penalty
        owner_factor = {1: 1.0, 2: 0.90, 3: 0.80, 4: 0.70}[owners]
        # Transmission bonus
        trans_factor = 1.06 if transmission == "Automatic" else 1.00
        # Fuel premium
        fuel_factor = 1.04 if fuel == "Diesel" else (1.08 if fuel == "Electric" else 0.98 if fuel == "CNG" else 1.0)
        # Brand retention bonus
        brand_retention = 1.06 if brand in ["Toyota", "Maruti Suzuki"] else (0.95 if brand in ["Ford", "Renault"] else 1.0)

        estimated_price = base_original_price * depreciation_factor * km_factor * cond_map[condition] * owner_factor * trans_factor * fuel_factor * brand_retention
        # Add random noise (+- 5%)
        noise = np.random.normal(1.0, 0.04)
        resale_price = int(max(45000, round(estimated_price * noise, -2)))

        data.append({
            "brand": brand,
            "model": model_name,
            "manufacturing_year": year,
            "kilometers_driven": km_driven,
            "fuel_type": fuel,
            "transmission_type": transmission,
            "number_of_owners": owners,
            "vehicle_condition": condition,
            "engine_capacity": engine_capacity,
            "resale_price": resale_price
        })

    df = pd.DataFrame(data)
    csv_path = os.path.join(DATA_DIR, "car_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated Car dataset with {len(df)} records at: {csv_path}")
    return df


# ==============================================================================
# 2. LORRY (COMMERCIAL TRUCK) DATASET GENERATOR
# ==============================================================================
def generate_lorry_data(n_samples=1500):
    brands = {
        "Tata Motors": 1.04,
        "Ashok Leyland": 1.03,
        "Eicher": 0.99,
        "BharatBenz": 1.07,
        "Mahindra Truck": 0.96,
        "Force Motors": 0.92
    }

    vehicle_types = ["Tipper", "Container", "Open Body", "Tanker", "Flatbed", "Mini Truck"]
    current_year = 2026
    data = []

    for _ in range(n_samples):
        brand = np.random.choice(list(brands.keys()), p=[0.38, 0.30, 0.15, 0.08, 0.06, 0.03])
        brand_mult = brands[brand]

        v_type = np.random.choice(vehicle_types, p=[0.25, 0.22, 0.28, 0.10, 0.08, 0.07])

        # Load capacity in tonnes based on vehicle type
        if v_type == "Mini Truck":
            load_capacity = round(float(np.random.uniform(1.2, 3.5)), 1)
            base_new_cost = 650000 + (load_capacity * 120000)
        elif v_type == "Tipper":
            load_capacity = round(float(np.random.uniform(10.0, 28.0)), 1)
            base_new_cost = 2500000 + (load_capacity * 75000)
        elif v_type == "Container":
            load_capacity = round(float(np.random.uniform(14.0, 35.0)), 1)
            base_new_cost = 2800000 + (load_capacity * 80000)
        elif v_type == "Tanker":
            load_capacity = round(float(np.random.uniform(12.0, 30.0)), 1)
            base_new_cost = 2900000 + (load_capacity * 85000)
        else:
            load_capacity = round(float(np.random.uniform(5.0, 40.0)), 1)
            base_new_cost = 1800000 + (load_capacity * 70000)

        year = int(np.random.choice(range(2008, 2026), p=[
            0.03, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.08,
            0.09, 0.09, 0.10, 0.09, 0.08, 0.05, 0.04, 0.02, 0.00, 0.00
        ]))
        age = current_year - year

        # Commercial lorries cover 25,000 to 70,000 km per year
        avg_km_per_year = np.random.uniform(25000, 65000)
        km_driven = int(max(15000, min(750000, age * avg_km_per_year + np.random.normal(0, 20000))))

        fuel = np.random.choice(["Diesel", "CNG"], p=[0.92, 0.08])

        # Owners
        if age <= 3:
            owners = np.random.choice([1, 2], p=[0.85, 0.15])
        elif age <= 7:
            owners = np.random.choice([1, 2, 3], p=[0.55, 0.35, 0.10])
        else:
            owners = np.random.choice([1, 2, 3, 4], p=[0.30, 0.40, 0.22, 0.08])

        condition = np.random.choice(["Excellent", "Good", "Fair", "Poor"], p=[0.18, 0.46, 0.26, 0.10])

        # Commercial depreciation rate (approx 10.5% per year)
        depreciation_factor = (1 - 0.105) ** age
        km_factor = max(0.38, 1.0 - (km_driven / 800000.0) * 0.48)
        cond_map = {"Excellent": 1.12, "Good": 1.00, "Fair": 0.84, "Poor": 0.65}
        owner_factor = {1: 1.0, 2: 0.88, 3: 0.77, 4: 0.68}[owners]
        fuel_factor = 1.02 if fuel == "Diesel" else 0.96

        est_price = base_new_cost * brand_mult * depreciation_factor * km_factor * cond_map[condition] * owner_factor * fuel_factor
        noise = np.random.normal(1.0, 0.05)
        resale_price = int(max(120000, round(est_price * noise, -3)))

        data.append({
            "brand": brand,
            "manufacturing_year": year,
            "kilometers_driven": km_driven,
            "fuel_type": fuel,
            "vehicle_type": v_type,
            "load_capacity_tonnes": load_capacity,
            "number_of_owners": owners,
            "vehicle_condition": condition,
            "resale_price": resale_price
        })

    df = pd.DataFrame(data)
    csv_path = os.path.join(DATA_DIR, "lorry_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated Lorry dataset with {len(df)} records at: {csv_path}")
    return df


# ==============================================================================
# 3. BIKE (TWO-WHEELER) DATASET GENERATOR
# ==============================================================================
def generate_bike_data(n_samples=1600):
    brands_models = {
        "Hero": [("Splendor Plus", 97, 76000), ("HF Deluxe", 97, 65000), ("Passion Pro", 113, 80000), ("Glamour", 125, 87000), ("Xpulse 200", 200, 145000)],
        "Bajaj": [("Pulsar 150", 150, 112000), ("Pulsar NS200", 200, 150000), ("Platina 100", 102, 68000), ("Avenger 220", 220, 142000), ("Dominar 400", 373, 235000)],
        "TVS": [("Apache RTR 160", 160, 122000), ("Apache RR 310", 312, 275000), ("Jupiter", 110, 78000), ("Raider 125", 125, 96000), ("XL 100", 100, 50000)],
        "Honda": [("Activa 6G", 110, 80000), ("Shine 125", 125, 85000), ("Unicorn", 160, 110000), ("Hornet 2.0", 184, 140000), ("Dio", 110, 75000)],
        "Royal Enfield": [("Classic 350", 349, 215000), ("Bullet 350", 349, 185000), ("Hunter 350", 349, 170000), ("Himalayan 450", 452, 290000), ("Continental GT 650", 648, 345000)],
        "Yamaha": [("FZ-S FI", 149, 124000), ("MT-15", 155, 172000), ("R15 V4", 155, 188000), ("Aerox 155", 155, 150000)],
        "Suzuki": [("Access 125", 124, 84000), ("Gixxer 150", 155, 138000), ("Burgman Street", 125, 98000)],
        "KTM": [("Duke 200", 200, 198000), ("Duke 390", 373, 315000), ("RC 200", 200, 218000)]
    }

    brand_list = list(brands_models.keys())
    current_year = 2026
    data = []

    for _ in range(n_samples):
        brand = np.random.choice(brand_list, p=[0.24, 0.20, 0.16, 0.18, 0.10, 0.05, 0.04, 0.03])
        model_info = brands_models[brand][np.random.choice(len(brands_models[brand]))]
        model_name, cc, base_price = model_info

        year = int(np.random.choice(range(2010, 2026), p=[
            0.02, 0.03, 0.04, 0.04, 0.05, 0.06, 0.07, 0.08,
            0.09, 0.10, 0.11, 0.11, 0.09, 0.06, 0.04, 0.01
        ]))
        age = current_year - year

        avg_km_per_year = np.random.uniform(4000, 11000)
        km_driven = int(max(1000, min(140000, age * avg_km_per_year + np.random.normal(0, 4000))))

        fuel = "Electric" if brand in ["TVS", "Bajaj"] and np.random.rand() < 0.05 else "Petrol"

        if age <= 2:
            owners = np.random.choice([1, 2], p=[0.90, 0.10])
        elif age <= 6:
            owners = np.random.choice([1, 2, 3], p=[0.70, 0.25, 0.05])
        else:
            owners = np.random.choice([1, 2, 3, 4], p=[0.45, 0.35, 0.15, 0.05])

        condition = np.random.choice(["Excellent", "Good", "Fair", "Poor"], p=[0.28, 0.44, 0.20, 0.08])

        depreciation_factor = (1 - 0.09) ** age
        km_factor = max(0.42, 1.0 - (km_driven / 150000.0) * 0.45)
        cond_map = {"Excellent": 1.10, "Good": 1.00, "Fair": 0.85, "Poor": 0.68}
        owner_factor = {1: 1.0, 2: 0.88, 3: 0.76, 4: 0.65}[owners]
        brand_retention = 1.12 if brand == "Royal Enfield" else (1.04 if brand in ["Hero", "Honda"] else 1.00)

        est_price = base_price * brand_retention * depreciation_factor * km_factor * cond_map[condition] * owner_factor
        noise = np.random.normal(1.0, 0.04)
        resale_price = int(max(12000, round(est_price * noise, -2)))

        data.append({
            "brand": brand,
            "model": model_name,
            "manufacturing_year": year,
            "kilometers_driven": km_driven,
            "engine_capacity": cc,
            "fuel_type": fuel,
            "number_of_owners": owners,
            "vehicle_condition": condition,
            "resale_price": resale_price
        })

    df = pd.DataFrame(data)
    csv_path = os.path.join(DATA_DIR, "bike_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated Bike dataset with {len(df)} records at: {csv_path}")
    return df


# ==============================================================================
# 4. AUTO-RICKSHAW DATASET GENERATOR
# ==============================================================================
def generate_auto_data(n_samples=1400):
    brands = {
        "Bajaj Auto": (1.05, 235000),
        "Piaggio": (1.02, 245000),
        "Mahindra": (0.98, 260000),
        "Atul Auto": (0.95, 220000),
        "TVS King": (0.99, 230000)
    }

    current_year = 2026
    data = []

    for _ in range(n_samples):
        brand = np.random.choice(list(brands.keys()), p=[0.48, 0.24, 0.12, 0.09, 0.07])
        brand_multiplier, base_cost = brands[brand]

        cargo_type = np.random.choice(["Passenger", "Cargo"], p=[0.72, 0.28])
        if cargo_type == "Cargo":
            base_cost += 35000

        fuel = np.random.choice(["CNG", "LPG", "Petrol", "Diesel", "Electric"], p=[0.45, 0.18, 0.14, 0.13, 0.10])
        if fuel == "Electric":
            base_cost += 40000

        year = int(np.random.choice(range(2011, 2026), p=[
            0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10,
            0.11, 0.11, 0.09, 0.08, 0.05, 0.03, 0.01
        ]))
        age = current_year - year

        avg_km_per_year = np.random.uniform(12000, 28000)
        km_driven = int(max(4000, min(320000, age * avg_km_per_year + np.random.normal(0, 8000))))

        if age <= 3:
            owners = np.random.choice([1, 2], p=[0.82, 0.18])
        elif age <= 7:
            owners = np.random.choice([1, 2, 3], p=[0.58, 0.32, 0.10])
        else:
            owners = np.random.choice([1, 2, 3, 4], p=[0.35, 0.40, 0.18, 0.07])

        condition = np.random.choice(["Excellent", "Good", "Fair", "Poor"], p=[0.20, 0.48, 0.24, 0.08])

        depreciation_factor = (1 - 0.10) ** age
        km_factor = max(0.40, 1.0 - (km_driven / 350000.0) * 0.45)
        cond_map = {"Excellent": 1.10, "Good": 1.00, "Fair": 0.86, "Poor": 0.70}
        owner_factor = {1: 1.0, 2: 0.88, 3: 0.77, 4: 0.66}[owners]
        fuel_factor = 1.05 if fuel == "CNG" else (1.08 if fuel == "Electric" else 0.96)

        est_price = base_cost * brand_multiplier * depreciation_factor * km_factor * cond_map[condition] * owner_factor * fuel_factor
        noise = np.random.normal(1.0, 0.04)
        resale_price = int(max(25000, round(est_price * noise, -2)))

        data.append({
            "brand": brand,
            "manufacturing_year": year,
            "kilometers_driven": km_driven,
            "fuel_type": fuel,
            "passenger_or_cargo": cargo_type,
            "number_of_owners": owners,
            "vehicle_condition": condition,
            "resale_price": resale_price
        })

    df = pd.DataFrame(data)
    csv_path = os.path.join(DATA_DIR, "auto_data.csv")
    df.to_csv(csv_path, index=False)
    print(f"Generated Auto-rickshaw dataset with {len(df)} records at: {csv_path}")
    return df


if __name__ == "__main__":
    print("Generating authentic sample datasets for 4 vehicle categories...")
    generate_car_data()
    generate_lorry_data()
    generate_bike_data()
    generate_auto_data()
    print("All datasets generated successfully!")
