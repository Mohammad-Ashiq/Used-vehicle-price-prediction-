"""
test_predictions.py
Quick smoke test for model inference across all 4 vehicle categories.
"""
import joblib
import pandas as pd

def test_inference():
    categories = {
        "car": {
            "file": "models/car_model.joblib",
            "sample": {
                "brand": "Maruti Suzuki",
                "model": "Swift",
                "manufacturing_year": 2019,
                "kilometers_driven": 45000,
                "fuel_type": "Petrol",
                "transmission_type": "Manual",
                "number_of_owners": 1,
                "vehicle_condition": "Good",
                "engine_capacity": 1200
            }
        },
        "lorry": {
            "file": "models/lorry_model.joblib",
            "sample": {
                "brand": "Tata Motors",
                "manufacturing_year": 2018,
                "kilometers_driven": 180000,
                "fuel_type": "Diesel",
                "vehicle_type": "Tipper",
                "load_capacity_tonnes": 16.0,
                "number_of_owners": 1,
                "vehicle_condition": "Good"
            }
        },
        "bike": {
            "file": "models/bike_model.joblib",
            "sample": {
                "brand": "Hero",
                "model": "Splendor Plus",
                "manufacturing_year": 2020,
                "kilometers_driven": 25000,
                "engine_capacity": 97,
                "fuel_type": "Petrol",
                "number_of_owners": 1,
                "vehicle_condition": "Good"
            }
        },
        "auto": {
            "file": "models/auto_model.joblib",
            "sample": {
                "brand": "Bajaj Auto",
                "manufacturing_year": 2019,
                "kilometers_driven": 65000,
                "fuel_type": "CNG",
                "passenger_or_cargo": "Passenger",
                "number_of_owners": 1,
                "vehicle_condition": "Good"
            }
        }
    }

    for cat, info in categories.items():
        bundle = joblib.load(info["file"])
        pipe = bundle["pipeline"]
        df = pd.DataFrame([info["sample"]])
        pred = pipe.predict(df)[0]
        print(f"[{cat.upper()}] Predicted: INR {pred:,.2f} | R2: {bundle['metrics']['r2']:.3f} | MAE: INR {bundle['metrics']['mae']:,.2f}")

if __name__ == "__main__":
    test_inference()
