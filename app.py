import os
import sys
from functools import wraps
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_file, send_from_directory, abort, session
)

from config import Config
from database.db import (
    init_db, save_prediction, get_prediction, get_all_predictions,
    delete_prediction, get_dashboard_stats, save_contact_message,
    create_user, get_user_by_id, get_user_by_email, get_user_by_phone,
    authenticate_user, create_or_get_otp_user,
    add_to_garage, get_user_garage, get_garage_vehicle,
    update_garage_vehicle_mileage, delete_garage_vehicle, get_garage_portfolio_stats
)
from ml.preprocess import validate_and_format_input, CURRENT_YEAR
from ml.predict import predict_price, get_model_info, format_inr, format_lakhs
from ml.voice_assistant import process_voice_query
from utils.pdf_generator import generate_prediction_pdf, generate_garage_certificate

app = Flask(__name__)
app.config.from_object(Config)

# Ensure required directories exist
for path in [Config.DATASET_DIR, Config.MODELS_DIR, Config.REPORTS_DIR, os.path.dirname(Config.DATABASE_PATH)]:
    os.makedirs(path, exist_ok=True)

# Initialize database tables on application start
with app.app_context():
    init_db()

# ----------------- AUTHENTICATION HELPERS ----------------- #

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access your Virtual Garage.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Context processor to make common data available across all templates
@app.context_processor
def inject_global_data():
    current_user = None
    garage_count = 0
    if 'user_id' in session:
        current_user = get_user_by_id(session['user_id'])
        if current_user:
            user_garage = get_user_garage(current_user['id'])
            garage_count = len(user_garage)
        else:
            session.pop('user_id', None)
            
    return {
        'current_year': CURRENT_YEAR,
        'categories_info': Config.CATEGORIES_INFO,
        'supported_locations': Config.LOCATIONS,
        'format_inr': format_inr,
        'format_lakhs': format_lakhs,
        'current_user': current_user,
        'garage_count': garage_count
    }

# ----------------- CORE NAVIGATION & LANDING ----------------- #

@app.route('/')
def index():
    """Home Landing Page"""
    stats = get_dashboard_stats()
    return render_template('index.html', stats=stats)

@app.route('/dashboard')
def dashboard():
    """User Analytics Dashboard"""
    stats = get_dashboard_stats()
    model_status = {cat: get_model_info(cat) for cat in Config.CATEGORIES_INFO}
    return render_template('dashboard.html', stats=stats, model_status=model_status)

@app.route('/categories')
def categories():
    """Vehicle Category Hub"""
    return render_template('categories.html')

# ----------------- USER AUTHENTICATION ROUTES ----------------- #

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User Sign In with Email/Password or Demo Fast-Track"""
    if 'user_id' in session:
        return redirect(url_for('garage'))
        
    next_url = request.args.get('next') or request.form.get('next') or url_for('garage')
    
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password = request.form.get('password', '').strip()
        
        if not identifier or not password:
            flash("Please enter both your email/phone and password.", "danger")
            return render_template('login.html', next=next_url)
            
        user = authenticate_user(identifier, password)
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash(f"Welcome back, {user['name']}! Your garage is ready.", "success")
            
            # Handle pending prediction save to garage if any
            pending_pred = session.pop('pending_garage_prediction_id', None)
            if pending_pred:
                pred_rec = get_prediction(pending_pred)
                if pred_rec:
                    add_to_garage(user['id'], pred_rec)
                    flash("Saved your recent valuation directly to your Virtual Garage!", "info")
                    
            return redirect(next_url)
        else:
            flash("Invalid email/phone or password. Please try again or use Demo Login.", "danger")
            
    return render_template('login.html', next=next_url)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User Registration"""
    if 'user_id' in session:
        return redirect(url_for('garage'))
        
    next_url = request.args.get('next') or request.form.get('next') or url_for('garage')
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not name or not email or not password:
            flash("Name, email, and password are required.", "danger")
            return render_template('signup.html', next=next_url)
            
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('signup.html', next=next_url)
            
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template('signup.html', next=next_url)
            
        user_id, error = create_user(name, email, password, phone)
        if error:
            flash(error, "danger")
            return render_template('signup.html', next=next_url)
            
        # Log user in immediately
        session['user_id'] = user_id
        session['user_name'] = name
        session['user_email'] = email
        flash(f"Account created successfully! Welcome to ReVahan, {name}.", "success")
        
        # Handle pending prediction save
        pending_pred = session.pop('pending_garage_prediction_id', None)
        if pending_pred:
            pred_rec = get_prediction(pending_pred)
            if pred_rec:
                add_to_garage(user_id, pred_rec)
                flash("Saved your recent valuation to your Virtual Garage!", "info")
                
        return redirect(next_url)
        
    return render_template('signup.html', next=next_url)

@app.route('/demo-login')
def demo_login():
    """One-Click Instant Demo Login for Portfolios & Evaluation"""
    demo_user = authenticate_user('demo@revahan.in', 'Demo@123')
    if not demo_user:
        init_db()
        demo_user = authenticate_user('demo@revahan.in', 'Demo@123')
        
    if demo_user:
        session['user_id'] = demo_user['id']
        session['user_name'] = demo_user['name']
        session['user_email'] = demo_user['email']
        flash(f"Logged in as Demo User: {demo_user['name']}! Feel free to explore your Virtual Garage.", "success")
    return redirect(url_for('garage'))

@app.route('/api/otp-login', methods=['POST'])
def api_otp_login():
    """Quick Mobile OTP / Phone Instant Verification"""
    data = request.get_json(silent=True) or request.form
    phone = data.get('phone', '').strip()
    otp = data.get('otp', '').strip()
    
    if not phone or len(phone.replace(' ', '').replace('+91', '')) < 10:
        return jsonify({'success': False, 'message': 'Please enter a valid 10-digit mobile number.'}), 400
        
    # Standard simulated OTP verification (accepts demo OTP '123456' or any 6-digit entered during preview)
    if otp and len(otp) == 6:
        user = create_or_get_otp_user(phone)
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        return jsonify({'success': True, 'redirect': url_for('garage')})
    else:
        # Step 1: Send OTP simulation
        return jsonify({
            'success': True,
            'step': 'otp_sent',
            'message': f"OTP sent to {phone}. Use demo code 123456 to verify instantly."
        })

@app.route('/logout')
def logout():
    """Log out current user and terminate session"""
    session.clear()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for('index'))

# ----------------- MY VIRTUAL GARAGE ROUTES ----------------- #

@app.route('/garage')
@login_required
def garage():
    """My Virtual Garage Portfolio: Fleet Value, Depreciation Tracker, and Asset Certificates"""
    user_id = session['user_id']
    portfolio = get_garage_portfolio_stats(user_id)
    return render_template('garage.html', portfolio=portfolio)

@app.route('/garage/add', methods=['POST'])
@login_required
def garage_add_vehicle():
    """Add a new vehicle to the user's garage and calculate its initial depreciation curve"""
    user_id = session['user_id']
    category = request.form.get('category', 'cars').lower().strip()
    
    form_data = dict(request.form)
    # Supply category defaults if missing in quick garage add
    if category == 'cars' and not form_data.get('engine_cc'):
        form_data['engine_cc'] = 1197
    elif category == 'bikes' and not form_data.get('engine_cc'):
        form_data['engine_cc'] = 150
    elif category == 'lorries':
        if not form_data.get('load_capacity'):
            form_data['load_capacity'] = 5.0
        if not form_data.get('vehicle_type'):
            form_data['vehicle_type'] = 'Light Commercial Vehicle (LCV)'
    elif category == 'autos' and not form_data.get('passenger_capacity'):
        form_data['passenger_capacity'] = '3 Seater'

    clean_data, error_msg = validate_and_format_input(category, form_data)
    if error_msg:
        flash(f"Validation error: {error_msg}", "danger")
        return redirect(url_for('garage'))
        
    try:
        # Run ML prediction to determine current market valuation
        result = predict_price(category, clean_data)
        
        # Merge input data with prediction output & garage extras
        record_data = {
            **clean_data,
            **result,
            'category': category,
            'nickname': request.form.get('nickname', '').strip(),
            'purchase_price': float(request.form.get('purchase_price') or result['predicted_price'] * 1.35),
            'purchase_year': int(request.form.get('purchase_year') or clean_data.get('year', CURRENT_YEAR)),
            'notes': request.form.get('notes', '').strip()
        }
        
        v_id = add_to_garage(user_id, record_data)
        flash(f"Vehicle '{record_data['nickname'] or record_data['brand']}' added to your Virtual Garage!", "success")
        return redirect(url_for('garage'))
        
    except Exception as e:
        app.logger.error(f"Error adding vehicle to garage: {str(e)}")
        flash(f"Could not add vehicle to garage: {str(e)}", "danger")
        return redirect(url_for('garage'))

@app.route('/garage/save-prediction/<int:prediction_id>', methods=['POST'])
def garage_save_prediction(prediction_id):
    """Quick-save an existing prediction result into the user's Virtual Garage"""
    rec = get_prediction(prediction_id)
    if not rec:
        flash("Prediction record not found.", "danger")
        return redirect(url_for('history'))
        
    if 'user_id' not in session:
        # Store pending prediction to auto-save after login
        session['pending_garage_prediction_id'] = prediction_id
        flash("Please log in or sign up to add this vehicle to your Virtual Garage.", "info")
        return redirect(url_for('login', next=url_for('prediction_result', prediction_id=prediction_id)))
        
    user_id = session['user_id']
    # Check if already added
    user_garage = get_user_garage(user_id)
    for v in user_garage:
        if v['brand'] == rec['brand'] and v['model'] == rec['model'] and v['year'] == rec['year'] and v['km_driven'] == rec['km_driven']:
            flash(f"{rec['brand']} {rec['model']} is already in your Virtual Garage!", "warning")
            return redirect(url_for('garage'))
            
    # Add to garage
    add_to_garage(user_id, rec)
    flash(f"Successfully saved {rec['year']} {rec['brand']} {rec['model']} to your Virtual Garage!", "success")
    return redirect(url_for('garage'))

@app.route('/garage/update-mileage/<int:vehicle_id>', methods=['POST'])
@login_required
def garage_update_mileage(vehicle_id):
    """Update odometer reading and re-evaluate current valuation via ML"""
    user_id = session['user_id']
    vehicle = get_garage_vehicle(vehicle_id, user_id)
    if not vehicle:
        flash("Vehicle not found in your garage.", "danger")
        return redirect(url_for('garage'))
        
    try:
        new_km = int(request.form.get('km_driven', vehicle['km_driven']))
        if new_km < 0:
            flash("Odometer reading cannot be negative.", "danger")
            return redirect(url_for('garage'))
            
        # Re-run ML model with updated mileage
        eval_data = dict(vehicle)
        eval_data['km_driven'] = new_km
        pred = predict_price(vehicle['category'], eval_data)
        
        update_garage_vehicle_mileage(
            vehicle_id, user_id, new_km,
            pred['predicted_price'], pred['price_min'], pred['price_max']
        )
        flash(f"Odometer updated to {new_km:,} km! New market valuation: ₹ {format_inr(pred['predicted_price'])}.", "success")
    except Exception as e:
        flash(f"Failed to update odometer: {str(e)}", "danger")
        
    return redirect(url_for('garage'))

@app.route('/garage/delete/<int:vehicle_id>', methods=['POST'])
@login_required
def garage_delete_vehicle(vehicle_id):
    """Remove vehicle from Virtual Garage"""
    user_id = session['user_id']
    success = delete_garage_vehicle(vehicle_id, user_id)
    if success:
        flash("Vehicle removed from your Virtual Garage.", "info")
    else:
        flash("Vehicle could not be removed.", "danger")
    return redirect(url_for('garage'))

@app.route('/garage/certificate/<int:vehicle_id>')
@login_required
def download_garage_certificate(vehicle_id):
    """Download Branded Personalized PDF Valuation Certificate & Asset Passport"""
    user_id = session['user_id']
    vehicle = get_garage_vehicle(vehicle_id, user_id)
    user = get_user_by_id(user_id)
    
    if not vehicle:
        flash("Vehicle not found in your garage.", "warning")
        return redirect(url_for('garage'))
        
    try:
        pdf_path = generate_garage_certificate(vehicle, user=user)
        filename = f"ReVahan_Certificate_{vehicle['brand']}_{vehicle['model']}_{vehicle['id']}.pdf"
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"Garage Certificate Error: {str(e)}")
        flash(f"Failed to generate certificate: {str(e)}", "danger")
        return redirect(url_for('garage'))

@app.route('/api/garage/depreciation/<int:vehicle_id>')
@login_required
def api_garage_depreciation(vehicle_id):
    """Returns JSON depreciation history timeline for Chart.js rendering"""
    user_id = session['user_id']
    vehicle = get_garage_vehicle(vehicle_id, user_id)
    if not vehicle:
        return jsonify({'error': 'Vehicle not found'}), 404
        
    return jsonify({
        'nickname': vehicle.get('nickname') or f"{vehicle['brand']} {vehicle['model']}",
        'brand': vehicle['brand'],
        'model': vehicle['model'],
        'purchase_price': vehicle.get('purchase_price'),
        'current_valuation': vehicle['current_valuation'],
        'history': vehicle.get('valuation_history', [])
    })

# ----------------- PREDICTION & REPORT ROUTES ----------------- #

@app.route('/predict/<category>', methods=['GET'])
def prediction_form(category):
    """Dynamic Prediction Form for Specific Category"""
    cat = category.lower()
    if cat not in Config.CATEGORIES_INFO:
        flash(f"Vehicle category '{category}' is not supported.", 'danger')
        return redirect(url_for('categories'))
        
    cat_info = Config.CATEGORIES_INFO[cat]
    model_info = get_model_info(cat)
    return render_template('prediction.html', category=cat, info=cat_info, model_info=model_info)

@app.route('/predict', methods=['POST'])
def process_prediction():
    """Handle Form Submission & Machine Learning Estimation"""
    category = request.form.get('category', '').lower().strip()
    if category not in Config.CATEGORIES_INFO:
        flash("Invalid vehicle category selected.", 'danger')
        return redirect(url_for('categories'))
        
    # Validate and clean input
    clean_data, error_msg = validate_and_format_input(category, request.form)
    if error_msg:
        flash(f"Validation Error: {error_msg}", 'danger')
        return redirect(url_for('prediction_form', category=category))
        
    try:
        # Run Machine Learning prediction
        result = predict_price(category, clean_data)
        
        # Merge input data with prediction output
        record_data = {**clean_data, **result, 'category': category}
        
        # Save record in SQLite with optional user attribution
        user_id = session.get('user_id')
        pred_id = save_prediction(record_data, user_id=user_id)
        
        flash("Vehicle market valuation calculated successfully!", "success")
        return redirect(url_for('prediction_result', prediction_id=pred_id))
        
    except FileNotFoundError as fnf_error:
        flash(f"Model File Missing: {str(fnf_error)} Please train models using train_model.py.", 'warning')
        return redirect(url_for('prediction_form', category=category))
    except Exception as e:
        app.logger.error(f"Prediction Error: {str(e)}")
        flash(f"An unexpected error occurred during prediction: {str(e)}", 'danger')
        return redirect(url_for('prediction_form', category=category))

@app.route('/result/<int:prediction_id>')
def prediction_result(prediction_id):
    """Display Vehicle Valuation Results & Explanatory Factors"""
    record = get_prediction(prediction_id)
    if not record:
        flash("Valuation record not found.", "warning")
        return redirect(url_for('history'))
        
    # Re-evaluate factors for rich display
    category = record.get('category', 'cars')
    prediction_details = predict_price(category, record)
    
    return render_template(
        'result.html',
        record=record,
        details=prediction_details,
        category_info=Config.CATEGORIES_INFO.get(category, {})
    )

@app.route('/history')
def history():
    """Valuation History with Search and Filtering"""
    search = request.args.get('search', '').strip()
    category = request.args.get('category', 'all').strip()
    page = int(request.args.get('page', 1))
    limit = 15
    offset = (page - 1) * limit
    
    records, total_count = get_all_predictions(search=search, category=category, limit=limit, offset=offset)
    total_pages = max(1, (total_count + limit - 1) // limit)
    
    return render_template(
        'history.html',
        records=records,
        search=search,
        selected_category=category,
        page=page,
        total_pages=total_pages,
        total_count=total_count
    )

@app.route('/history/delete/<int:prediction_id>', methods=['POST'])
def delete_history_record(prediction_id):
    """Delete Individual Record from History"""
    success = delete_prediction(prediction_id)
    if success:
        flash(f"Prediction record #{prediction_id} deleted successfully.", "success")
    else:
        flash(f"Failed to delete record #{prediction_id}.", "danger")
    return redirect(request.referrer or url_for('history'))

@app.route('/report/<int:prediction_id>')
def download_report(prediction_id):
    """Download Valuation PDF Report with optional user branding"""
    record = get_prediction(prediction_id)
    if not record:
        flash("Record not found for report generation.", "warning")
        return redirect(url_for('history'))
        
    try:
        user = get_user_by_id(session['user_id']) if 'user_id' in session else None
        pdf_path = generate_prediction_pdf(record, user=user)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Vehicle_Valuation_Report_{prediction_id}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        app.logger.error(f"PDF Generation Error: {str(e)}")
        flash(f"Failed to generate PDF report: {str(e)}", "danger")
        return redirect(url_for('prediction_result', prediction_id=prediction_id))

@app.route('/about')
def about():
    """About the System, Machine Learning Architecture, and Team"""
    model_metrics = {cat: get_model_info(cat) for cat in Config.CATEGORIES_INFO}
    return render_template('about.html', model_metrics=model_metrics)

@app.route('/how-it-works')
def how_it_works():
    """Detailed Explanation of ML Workflow and Feature Processing"""
    return render_template('how_it_works.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact & Feedback Page with SQLite Ingestion"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()
        
        if not (name and email and subject and message):
            flash("All fields in the contact form are required.", "danger")
        else:
            save_contact_message(name, email, subject, message)
            flash("Thank you for your message! Our team will get back to you shortly.", "success")
            return redirect(url_for('contact'))
            
    return render_template('contact.html')

@app.route('/privacy-policy')
def privacy_policy():
    """Official Privacy Policy for Google Play Store compliance"""
    return render_template('privacy_policy.html')

# ----------------- REST API ENDPOINTS ----------------- #

@app.route('/api/models/<category>')
def get_brand_models(category):
    """Returns available vehicle models for a selected brand (for dynamic dropdowns)"""
    cat = category.lower()
    brand = request.args.get('brand', '').strip()
    
    if cat not in Config.CATEGORIES_INFO:
        return jsonify({'error': 'Invalid category'}), 400
        
    brands_catalog = Config.CATEGORIES_INFO[cat]['brands']
    models = brands_catalog.get(brand, [])
    return jsonify({'brand': brand, 'models': models})

@app.route('/api/stats')
def api_stats():
    """Returns aggregated stats for Chart.js rendering"""
    stats = get_dashboard_stats()
    return jsonify(stats)

@app.route('/api/voice-assistant', methods=['POST'])
def api_voice_assistant():
    """AI Voice Assistant Endpoint: Natural Language Understanding + Voice Prediction"""
    data = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    result = process_voice_query(query)
    return jsonify(result)

# ----------------- ERROR HANDLERS ----------------- #

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ----------------- PWA & SEARCH ENGINE ROUTES ----------------- #

@app.route('/sw.js')
def service_worker():
    response = send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/manifest.json')
def pwa_manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/manifest+json')

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt', mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(app.static_folder, 'sitemap.xml', mimetype='application/xml')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=====================================================================")
    print(f"  USED VEHICLE PRICE PREDICTION SYSTEM - FLASK SERVER RUNNING ON {port}")
    print(f"  Access web portal at: http://127.0.0.1:{port}")
    print("=====================================================================")
    app.run(host='0.0.0.0', port=port, debug=False)
