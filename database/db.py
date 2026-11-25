import sqlite3
import os
import json
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_depreciation_history(purchase_price, purchase_year, current_valuation, current_year=None):
    """
    Generates a realistic month-by-month historical depreciation timeline
    from purchase up to present, plus a 6-month forward forecast.
    """
    if not current_year:
        current_year = Config.CURRENT_YEAR
        
    purchase_price = float(purchase_price) if purchase_price else float(current_valuation) * 1.35
    current_valuation = float(current_valuation)
    
    # Calculate total months from purchase year (assume mid-year purchase if only year given)
    months_elapsed = max(6, (current_year - int(purchase_year)) * 12)
    history_points = []
    
    # Generate past 12-18 months of historical milestones
    num_past_steps = min(12, months_elapsed)
    now = datetime.now()
    
    for i in range(num_past_steps, 0, -1):
        month_date = now - timedelta(days=i * 30.5)
        month_label = month_date.strftime("%b %Y")
        
        # Exponential decay interpolation between purchase_price and current_valuation
        progress = (months_elapsed - i) / max(1, months_elapsed)
        val = purchase_price - (purchase_price - current_valuation) * (progress ** 0.85)
        retained = round((val / purchase_price) * 100, 1)
        history_points.append({
            'label': month_label,
            'valuation': int(round(val, -2)),
            'retained_pct': retained,
            'type': 'historical'
        })
        
    # Current month point
    history_points.append({
        'label': now.strftime("%b %Y (Now)"),
        'valuation': int(round(current_valuation, -2)),
        'retained_pct': round((current_valuation / purchase_price) * 100, 1),
        'type': 'current'
    })
    
    # Future 6 months forecast (standard ~0.9% - 1.2% monthly automotive depreciation)
    monthly_dep_rate = 0.0105
    future_val = current_valuation
    for f in range(1, 7):
        future_date = now + timedelta(days=f * 30.5)
        future_val = future_val * (1.0 - monthly_dep_rate)
        future_retained = round((future_val / purchase_price) * 100, 1)
        history_points.append({
            'label': future_date.strftime("%b %Y (Est.)"),
            'valuation': int(round(future_val, -2)),
            'retained_pct': future_retained,
            'type': 'forecast'
        })
        
    return history_points


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone TEXT,
            avatar_color TEXT DEFAULT '#00f2fe',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Garage Vehicles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS garage_vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            nickname TEXT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            km_driven INTEGER NOT NULL,
            fuel_type TEXT NOT NULL,
            transmission TEXT,
            engine_cc INTEGER,
            load_capacity REAL,
            passenger_capacity TEXT,
            vehicle_type TEXT,
            owners TEXT NOT NULL,
            condition TEXT NOT NULL,
            location TEXT NOT NULL,
            purchase_price REAL,
            purchase_year INTEGER,
            current_valuation REAL NOT NULL,
            price_min REAL NOT NULL,
            price_max REAL NOT NULL,
            valuation_history TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # 3. Predictions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            km_driven INTEGER NOT NULL,
            fuel_type TEXT NOT NULL,
            transmission TEXT,
            engine_cc INTEGER,
            load_capacity REAL,
            passenger_capacity TEXT,
            vehicle_type TEXT,
            owners TEXT NOT NULL,
            condition TEXT NOT NULL,
            location TEXT NOT NULL,
            predicted_price REAL NOT NULL,
            price_min REAL NOT NULL,
            price_max REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')
    
    # Migration: add user_id column to predictions if it doesn't exist
    cursor.execute("PRAGMA table_info(predictions)")
    columns = [row['name'] for row in cursor.fetchall()]
    if 'user_id' not in columns:
        try:
            cursor.execute('ALTER TABLE predictions ADD COLUMN user_id INTEGER')
        except Exception:
            pass
            
    # 4. Contact Messages Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Indexes for fast searches and filtering
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_cat ON predictions(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_brand ON predictions(brand)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_garage_user ON garage_vehicles(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    
    # Seed default Demo User if not exists
    cursor.execute('SELECT id FROM users WHERE email = ?', ('demo@revahan.in',))
    demo_user = cursor.fetchone()
    if not demo_user:
        hashed = generate_password_hash('Demo@123')
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, phone, avatar_color)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Mohammad Ashiq', 'demo@revahan.in', hashed, '+91 98765 43210', '#00f2fe'))
        demo_user_id = cursor.lastrowid
        
        # Seed 2 realistic vehicles into Demo User's Virtual Garage
        # Vehicle 1: 2022 Hyundai Creta
        creta_hist = generate_depreciation_history(1550000, 2022, 1180000)
        cursor.execute('''
            INSERT INTO garage_vehicles (
                user_id, category, nickname, brand, model, year, km_driven,
                fuel_type, transmission, engine_cc, owners, condition, location,
                purchase_price, purchase_year, current_valuation, price_min, price_max,
                valuation_history, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            demo_user_id, 'cars', 'Family Cruiser', 'Hyundai', 'Creta', 2022, 28000,
            'Petrol', 'Manual', 1497, '1st Owner', 'Good', 'Delhi',
            1550000, 2022, 1180000, 1120000, 1240000,
            json.dumps(creta_hist), 'Serviced regularly at authorized Hyundai workshop. Zero accident history.'
        ))
        
        # Vehicle 2: 2023 Royal Enfield Classic 350
        re_hist = generate_depreciation_history(225000, 2023, 185000)
        cursor.execute('''
            INSERT INTO garage_vehicles (
                user_id, category, nickname, brand, model, year, km_driven,
                fuel_type, transmission, engine_cc, owners, condition, location,
                purchase_price, purchase_year, current_valuation, price_min, price_max,
                valuation_history, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            demo_user_id, 'bikes', 'Weekend Rider', 'Royal Enfield', 'Classic 350', 2023, 12500,
            'Petrol', 'Manual', 349, '1st Owner', 'Excellent', 'Kerala',
            225000, 2023, 185000, 175000, 195000,
            json.dumps(re_hist), 'Equipped with touring seat and engine crash guard. Clean condition.'
        ))
    
    conn.commit()
    conn.close()

# ----------------- USER AUTHENTICATION QUERIES ----------------- #

def create_user(name, email, password, phone=None):
    """Registers a new user with hashed password."""
    email = email.lower().strip()
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return None, "An account with this email address already exists."
        
    colors = ['#00f2fe', '#4facfe', '#38ef7d', '#ff0844', '#f6d365', '#f093fb']
    import random
    avatar_color = random.choice(colors)
    password_hash = generate_password_hash(password)
    
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, phone, avatar_color)
        VALUES (?, ?, ?, ?, ?)
    ''', (name.strip(), email, password_hash, phone.strip() if phone else None, avatar_color))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id, None

def get_user_by_id(user_id):
    """Fetch user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_email(email):
    """Fetch user by email."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email.lower().strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_phone(phone):
    """Fetch user by phone."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE phone = ?', (phone.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def authenticate_user(identifier, password):
    """Authenticates by email or phone with password."""
    identifier = identifier.strip()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Try email first, then phone
    cursor.execute('SELECT * FROM users WHERE email = ? OR phone = ?', (identifier.lower(), identifier))
    row = cursor.fetchone()
    conn.close()
    
    if row and check_password_hash(row['password_hash'], password):
        return dict(row)
    return None

def create_or_get_otp_user(phone, name=None):
    """Instant login / auto-register for mobile OTP workflow."""
    phone = phone.strip()
    user = get_user_by_phone(phone)
    if user:
        return user
        
    # Auto-create user for verified mobile
    display_name = name or f"User {phone[-4:]}"
    email = f"user_{phone[-6:]}@revahan.in"
    password = generate_password_hash("MobileVerified123!")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, phone, avatar_color)
        VALUES (?, ?, ?, ?, ?)
    ''', (display_name, email, password, phone, '#00f2fe'))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_user_by_id(user_id)


# ----------------- MY VIRTUAL GARAGE QUERIES ----------------- #

def add_to_garage(user_id, data):
    """Adds a vehicle to user's garage and builds its initial depreciation curve."""
    conn = get_connection()
    cursor = conn.cursor()
    
    purchase_price = float(data.get('purchase_price') or data.get('predicted_price', 0) * 1.35)
    purchase_year = int(data.get('purchase_year') or data.get('year', Config.CURRENT_YEAR))
    current_val = float(data.get('predicted_price') or data.get('current_valuation', 0))
    min_val = float(data.get('price_min') or current_val * 0.94)
    max_val = float(data.get('price_max') or current_val * 1.06)
    
    # Generate depreciation timeline
    hist = generate_depreciation_history(purchase_price, purchase_year, current_val)
    
    cursor.execute('''
        INSERT INTO garage_vehicles (
            user_id, category, nickname, brand, model, year, km_driven,
            fuel_type, transmission, engine_cc, load_capacity, passenger_capacity,
            vehicle_type, owners, condition, location, purchase_price, purchase_year,
            current_valuation, price_min, price_max, valuation_history, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('category', 'cars'),
        data.get('nickname') or f"{data.get('brand')} {data.get('model')}",
        data.get('brand'),
        data.get('model'),
        int(data.get('year', Config.CURRENT_YEAR)),
        int(data.get('km_driven', 0)),
        data.get('fuel_type', 'Petrol'),
        data.get('transmission'),
        int(data.get('engine_cc')) if data.get('engine_cc') else None,
        float(data.get('load_capacity')) if data.get('load_capacity') else None,
        data.get('passenger_capacity'),
        data.get('vehicle_type'),
        data.get('owners', '1st Owner'),
        data.get('condition', 'Good'),
        data.get('location', 'All India'),
        purchase_price,
        purchase_year,
        current_val,
        min_val,
        max_val,
        json.dumps(hist),
        data.get('notes', '')
    ))
    
    vehicle_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return vehicle_id

def get_user_garage(user_id):
    """Fetches all vehicles in user's garage, parsed with JSON history."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM garage_vehicles 
        WHERE user_id = ? 
        ORDER BY id DESC
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    vehicles = []
    for r in rows:
        v = dict(r)
        try:
            v['valuation_history'] = json.loads(v['valuation_history']) if v.get('valuation_history') else []
        except Exception:
            v['valuation_history'] = []
            
        # Compute equity retention percentage
        p_price = v.get('purchase_price') or v.get('current_valuation')
        if p_price and p_price > 0:
            v['retained_pct'] = round((v['current_valuation'] / p_price) * 100, 1)
            v['total_depreciation'] = round(p_price - v['current_valuation'], 2)
        else:
            v['retained_pct'] = 100.0
            v['total_depreciation'] = 0.0
            
        vehicles.append(v)
    return vehicles

def get_garage_vehicle(vehicle_id, user_id=None):
    """Fetches single garage vehicle, ensuring authorization if user_id supplied."""
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute('SELECT * FROM garage_vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id))
    else:
        cursor.execute('SELECT * FROM garage_vehicles WHERE id = ?', (vehicle_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    v = dict(row)
    try:
        v['valuation_history'] = json.loads(v['valuation_history']) if v.get('valuation_history') else []
    except Exception:
        v['valuation_history'] = []
        
    p_price = v.get('purchase_price') or v.get('current_valuation')
    if p_price and p_price > 0:
        v['retained_pct'] = round((v['current_valuation'] / p_price) * 100, 1)
        v['total_depreciation'] = round(p_price - v['current_valuation'], 2)
    else:
        v['retained_pct'] = 100.0
        v['total_depreciation'] = 0.0
    return v

def update_garage_vehicle_mileage(vehicle_id, user_id, new_km, new_valuation, new_min, new_max):
    """Updates vehicle odometer and recalibrates valuation and historical points."""
    vehicle = get_garage_vehicle(vehicle_id, user_id)
    if not vehicle:
        return False
        
    # Rebuild history with updated valuation
    purchase_price = vehicle.get('purchase_price') or new_valuation * 1.35
    purchase_year = vehicle.get('purchase_year') or vehicle.get('year')
    hist = generate_depreciation_history(purchase_price, purchase_year, new_valuation)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE garage_vehicles
        SET km_driven = ?,
            current_valuation = ?,
            price_min = ?,
            price_max = ?,
            valuation_history = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND user_id = ?
    ''', (new_km, new_valuation, new_min, new_max, json.dumps(hist), vehicle_id, user_id))
    
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def delete_garage_vehicle(vehicle_id, user_id):
    """Removes a vehicle from user's garage."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM garage_vehicles WHERE id = ? AND user_id = ?', (vehicle_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_garage_portfolio_stats(user_id):
    """Calculates overall garage fleet equity, total valuation, and depreciation."""
    vehicles = get_user_garage(user_id)
    if not vehicles:
        return {
            'total_vehicles': 0,
            'total_valuation': 0.0,
            'total_purchase': 0.0,
            'net_depreciation': 0.0,
            'average_retention': 0.0,
            'categories_breakdown': {},
            'vehicles': []
        }
        
    total_val = sum(v['current_valuation'] for v in vehicles)
    total_purchase = sum(v.get('purchase_price') or v['current_valuation'] for v in vehicles)
    net_dep = max(0.0, total_purchase - total_val)
    avg_ret = round((total_val / total_purchase) * 100, 1) if total_purchase > 0 else 100.0
    
    breakdown = {}
    for v in vehicles:
        cat = v['category']
        breakdown[cat] = breakdown.get(cat, 0) + 1
        
    return {
        'total_vehicles': len(vehicles),
        'total_valuation': round(total_val, 2),
        'total_purchase': round(total_purchase, 2),
        'net_depreciation': round(net_dep, 2),
        'average_retention': avg_ret,
        'categories_breakdown': breakdown,
        'vehicles': vehicles
    }


# ----------------- PREDICTIONS QUERIES ----------------- #

def save_prediction(data, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions (
            user_id, category, brand, model, year, km_driven, fuel_type,
            transmission, engine_cc, load_capacity, passenger_capacity,
            vehicle_type, owners, condition, location,
            predicted_price, price_min, price_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        data.get('category'),
        data.get('brand'),
        data.get('model'),
        int(data.get('year', Config.CURRENT_YEAR)),
        int(data.get('km_driven', 0)),
        data.get('fuel_type'),
        data.get('transmission'),
        int(data.get('engine_cc')) if data.get('engine_cc') else None,
        float(data.get('load_capacity')) if data.get('load_capacity') else None,
        data.get('passenger_capacity'),
        data.get('vehicle_type'),
        data.get('owners'),
        data.get('condition'),
        data.get('location'),
        float(data.get('predicted_price', 0)),
        float(data.get('price_min', 0)),
        float(data.get('price_max', 0))
    ))
    
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id

def get_prediction(prediction_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_predictions(search=None, category=None, user_id=None, limit=100, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM predictions WHERE 1=1'
    params = []
    
    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)
        
    if category and category.lower() != 'all':
        query += ' AND LOWER(category) = ?'
        params.append(category.lower())
        
    if search:
        query += ' AND (LOWER(brand) LIKE ? OR LOWER(model) LIKE ? OR LOWER(location) LIKE ?)'
        wildcard = f"%{search.lower()}%"
        params.extend([wildcard, wildcard, wildcard])
        
    query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
    params.extend([limit, offset])
    
    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    
    # Get total count matching criteria
    count_query = 'SELECT COUNT(*) as total FROM predictions WHERE 1=1'
    count_params = []
    if user_id:
        count_query += ' AND user_id = ?'
        count_params.append(user_id)
    if category and category.lower() != 'all':
        count_query += ' AND LOWER(category) = ?'
        count_params.append(category.lower())
    if search:
        count_query += ' AND (LOWER(brand) LIKE ? OR LOWER(model) LIKE ? OR LOWER(location) LIKE ?)'
        wildcard = f"%{search.lower()}%"
        count_params.extend([wildcard, wildcard, wildcard])
        
    cursor.execute(count_query, tuple(count_params))
    total = cursor.fetchone()['total']
    
    conn.close()
    return [dict(r) for r in rows], total

def delete_prediction(prediction_id, user_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    if user_id:
        cursor.execute('DELETE FROM predictions WHERE id = ? AND user_id = ?', (prediction_id, user_id))
    else:
        cursor.execute('DELETE FROM predictions WHERE id = ?', (prediction_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Total count
    cursor.execute('SELECT COUNT(*) as total, AVG(predicted_price) as avg_price FROM predictions')
    overall = cursor.fetchone()
    total_predictions = overall['total'] or 0
    avg_price_overall = overall['avg_price'] or 0.0
    
    # Category counts & averages
    categories = ['cars', 'bikes', 'lorries', 'autos']
    cat_counts = {c: 0 for c in categories}
    cat_avg_prices = {c: 0.0 for c in categories}
    
    cursor.execute('''
        SELECT category, COUNT(*) as cnt, AVG(predicted_price) as avg_p 
        FROM predictions 
        GROUP BY category
    ''')
    for row in cursor.fetchall():
        cat = row['category'].lower()
        if cat in cat_counts:
            cat_counts[cat] = row['cnt']
            cat_avg_prices[cat] = round(row['avg_p'] or 0, 2)
            
    # Recent 10 predictions
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT 10')
    recent = [dict(r) for r in cursor.fetchall()]
    
    # Conditions breakdown
    cursor.execute('''
        SELECT condition, COUNT(*) as cnt 
        FROM predictions 
        GROUP BY condition
    ''')
    condition_stats = {r['condition']: r['cnt'] for r in cursor.fetchall()}
    
    # Registered users and garage fleet count
    cursor.execute('SELECT COUNT(*) as cnt FROM users')
    total_users = cursor.fetchone()['cnt']
    
    cursor.execute('SELECT COUNT(*) as cnt, SUM(current_valuation) as val FROM garage_vehicles')
    garage_row = cursor.fetchone()
    total_garage_vehicles = garage_row['cnt'] or 0
    total_garage_valuation = garage_row['val'] or 0.0
    
    conn.close()
    return {
        'total': total_predictions,
        'avg_price': round(avg_price_overall, 2),
        'category_counts': cat_counts,
        'category_averages': cat_avg_prices,
        'recent_predictions': recent,
        'condition_stats': condition_stats,
        'total_users': total_users,
        'total_garage_vehicles': total_garage_vehicles,
        'total_garage_valuation': round(total_garage_valuation, 2)
    }

def save_contact_message(name, email, subject, message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO contact_messages (name, email, subject, message)
        VALUES (?, ?, ?, ?)
    ''', (name, email, subject, message))
    msg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return msg_id
