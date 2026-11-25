import os
import sys

# Ensure root directory on path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from config import Config
from database.db import init_db, save_prediction, get_dashboard_stats
from ml.predict import predict_price, format_inr
from utils.pdf_generator import generate_prediction_pdf

def seed():
    print("Initializing Database...")
    init_db()
    
    samples = [
        {
            'category': 'cars',
            'brand': 'Hyundai',
            'model': 'Creta',
            'year': 2021,
            'km_driven': 38000,
            'fuel_type': 'Diesel',
            'transmission': 'Manual',
            'engine_cc': 1493,
            'owners': '1st Owner',
            'condition': 'Excellent',
            'location': 'Bengaluru'
        },
        {
            'category': 'cars',
            'brand': 'Maruti Suzuki',
            'model': 'Swift',
            'year': 2019,
            'km_driven': 52000,
            'fuel_type': 'Petrol',
            'transmission': 'Manual',
            'engine_cc': 1197,
            'owners': '1st Owner',
            'condition': 'Good',
            'location': 'Delhi NCR'
        },
        {
            'category': 'bikes',
            'brand': 'Royal Enfield',
            'model': 'Classic 350',
            'year': 2022,
            'km_driven': 14000,
            'fuel_type': 'Petrol',
            'engine_cc': 349,
            'owners': '1st Owner',
            'condition': 'Excellent',
            'location': 'Pune'
        },
        {
            'category': 'bikes',
            'brand': 'Honda',
            'model': 'Activa 6G',
            'year': 2021,
            'km_driven': 22000,
            'fuel_type': 'Petrol',
            'engine_cc': 109,
            'owners': '2nd Owner',
            'condition': 'Good',
            'location': 'Mumbai'
        },
        {
            'category': 'lorries',
            'brand': 'Tata Motors',
            'model': 'Tata 407 Gold',
            'year': 2020,
            'km_driven': 95000,
            'fuel_type': 'Diesel',
            'load_capacity': 3.5,
            'vehicle_type': 'Light Commercial Vehicle (LCV)',
            'owners': '1st Owner',
            'condition': 'Good',
            'location': 'Hyderabad'
        },
        {
            'category': 'autos',
            'brand': 'Bajaj Auto',
            'model': 'Compact 4S RE',
            'year': 2021,
            'km_driven': 48000,
            'fuel_type': 'CNG',
            'passenger_capacity': '3 Seater',
            'owners': '1st Owner',
            'condition': 'Good',
            'location': 'Ahmedabad'
        }
    ]
    
    print("Generating predictions and seeding database...")
    for s in samples:
        cat = s['category']
        pred_res = predict_price(cat, s)
        full_data = {**s, **pred_res, 'category': cat}
        pred_id = save_prediction(full_data)
        print(f"  [+] Saved {s['year']} {s['brand']} {s['model']} ({cat}) -> Pred ID #{pred_id} | Price: Rs. {format_inr(pred_res['predicted_price'])}")
        
        # Test PDF generation for first sample
        if pred_id == 1:
            full_data['id'] = pred_id
            pdf_file = generate_prediction_pdf(full_data)
            print(f"  [+] Sample PDF successfully created: {pdf_file}")
            
    stats = get_dashboard_stats()
    print(f"\nSeeding complete! Total predictions in SQLite: {stats['total']}")
    print(f"Category counts: {stats['category_counts']}")

if __name__ == '__main__':
    seed()
