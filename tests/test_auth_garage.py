import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
import json

client = app.test_client()

# 1. Test Home
res = client.get('/')
assert res.status_code == 200, f'Home failed: {res.status_code}'
print('1. Home Page: 200 OK')

# 2. Test Login & Signup pages
res = client.get('/login')
assert res.status_code == 200, f'Login page failed: {res.status_code}'
res = client.get('/signup')
assert res.status_code == 200, f'Signup page failed: {res.status_code}'
print('2. Login & Signup pages: 200 OK')

# 3. Test Demo Login
res = client.get('/demo-login', follow_redirects=True)
assert res.status_code == 200, f'Demo login failed: {res.status_code}'
assert b'Mohammad Ashiq' in res.data, 'User name not found in garage page'
assert b'Family Cruiser' in res.data or b'Weekend Rider' in res.data, 'Garage vehicles not rendered'
print('3. Demo Login & Virtual Garage: 200 OK (Mohammad Ashiq logged in)')

# 4. Test Depreciation API
res = client.get('/api/garage/depreciation/1')
assert res.status_code == 200, f'Depreciation API failed: {res.status_code}'
dep_data = json.loads(res.data)
assert 'history' in dep_data and len(dep_data['history']) > 0, 'No depreciation history'
print(f"4. Depreciation API: 200 OK ({len(dep_data['history'])} milestones generated)")

# 5. Test Branded PDF Certificate Download
res = client.get('/garage/certificate/1')
assert res.status_code == 200, f'Certificate download failed: {res.status_code}'
assert res.mimetype == 'application/pdf', f'Wrong mimetype: {res.mimetype}'
assert len(res.data) > 1000, 'PDF data too small'
print(f'5. Branded PDF Certificate Download: 200 OK ({len(res.data)} bytes)')

# 6. Test Odometer Update
res = client.post('/garage/update-mileage/1', data={'km_driven': 35000}, follow_redirects=True)
assert res.status_code == 200, f'Update mileage failed: {res.status_code}'
assert b'35,000' in res.data or b'35000' in res.data, 'Updated km not reflected'
print('6. Recalculate Valuation with Odometer Update: 200 OK')

# 7. Test Prediction and Save to Garage
pred_data = {
    'category': 'cars',
    'brand': 'Tata Motors',
    'model': 'Nexon',
    'year': 2022,
    'km_driven': 25000,
    'engine_cc': 1199,
    'fuel_type': 'Petrol',
    'transmission': 'Manual',
    'owners': '1st Owner',
    'condition': 'Good',
    'location': 'Delhi'
}
res = client.post('/predict', data=pred_data, follow_redirects=True)
assert res.status_code == 200, f'Prediction failed: {res.status_code}'
assert b'Estimated Fair Market Resale Price' in res.data
print('7. ML Prediction: 200 OK')

# 8. Test Add Vehicle to Garage directly via Modal Form
res = client.get('/demo-login', follow_redirects=True)
add_v_data = {
    'category': 'cars',
    'brand': 'Mahindra',
    'model': 'Thar',
    'year': 2023,
    'km_driven': 18000,
    'fuel_type': 'Diesel',
    'transmission': 'Manual',
    'condition': 'Excellent',
    'owners': '1st Owner',
    'location': 'Delhi',
    'nickname': 'Offroad Beast',
    'purchase_price': 1600000,
    'purchase_year': 2023
}
res = client.post('/garage/add', data=add_v_data, follow_redirects=True)
assert res.status_code == 200, f'Add vehicle to garage failed: {res.status_code}'
assert b'Offroad Beast' in res.data, 'New vehicle not found in garage page'
print('8. Add Vehicle via Garage Modal: 200 OK')

# 9. Test Logout
res = client.get('/logout', follow_redirects=True)
assert res.status_code == 200
print('9. Logout: 200 OK')
print('=== ALL 9 INTEGRATION TESTS PASSED PERFECTLY ===')
