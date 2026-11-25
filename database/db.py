import sqlite3
import os
from config import Config

def get_connection():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Predictions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Contact Messages Table
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
    
    conn.commit()
    conn.close()

def save_prediction(data):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions (
            category, brand, model, year, km_driven, fuel_type,
            transmission, engine_cc, load_capacity, passenger_capacity,
            vehicle_type, owners, condition, location,
            predicted_price, price_min, price_max
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
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

def get_all_predictions(search=None, category=None, limit=100, offset=0):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT * FROM predictions WHERE 1=1'
    params = []
    
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

def delete_prediction(prediction_id):
    conn = get_connection()
    cursor = conn.cursor()
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
    
    conn.close()
    return {
        'total': total_predictions,
        'avg_price': round(avg_price_overall, 2),
        'category_counts': cat_counts,
        'category_averages': cat_avg_prices,
        'recent_predictions': recent,
        'condition_stats': condition_stats
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
