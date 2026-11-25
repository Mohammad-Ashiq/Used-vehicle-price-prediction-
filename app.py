import os
import sys
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, send_file, send_from_directory, abort
)
from datetime import datetime

from config import Config
from database.db import (
    init_db, save_prediction, get_prediction, get_all_predictions,
    delete_prediction, get_dashboard_stats, save_contact_message
)
from ml.preprocess import validate_and_format_input, CURRENT_YEAR
from ml.predict import predict_price, get_model_info, format_inr, format_lakhs
from ml.voice_assistant import process_voice_query
from utils.pdf_generator import generate_prediction_pdf

app = Flask(__name__)
app.config.from_object(Config)

# Ensure required directories exist
for path in [Config.DATASET_DIR, Config.MODELS_DIR, Config.REPORTS_DIR, os.path.dirname(Config.DATABASE_PATH)]:
    os.makedirs(path, exist_ok=True)

# Initialize database tables on application start
with app.app_context():
    init_db()

# Context processor to make common data available across all templates
@app.context_processor
def inject_global_data():
    return {
        'current_year': CURRENT_YEAR,
        'categories_info': Config.CATEGORIES_INFO,
        'supported_locations': Config.LOCATIONS,
        'format_inr': format_inr,
        'format_lakhs': format_lakhs
    }

# ----------------- ROUTES ----------------- #

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
        
        # Save record in SQLite
        pred_id = save_prediction(record_data)
        
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
    """Download Valuation PDF Report"""
    record = get_prediction(prediction_id)
    if not record:
        flash("Record not found for report generation.", "warning")
        return redirect(url_for('history'))
        
    try:
        pdf_path = generate_prediction_pdf(record)
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

# ----------------- PWA ROUTES ----------------- #

@app.route('/sw.js')
def service_worker():
    response = send_from_directory(app.static_folder, 'sw.js', mimetype='application/javascript')
    response.headers['Service-Worker-Allowed'] = '/'
    return response

@app.route('/manifest.json')
def pwa_manifest():
    return send_from_directory(app.static_folder, 'manifest.json', mimetype='application/manifest+json')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=====================================================================")
    print(f"  USED VEHICLE PRICE PREDICTION SYSTEM - FLASK SERVER RUNNING ON {port}")
    print(f"  Access web portal at: http://127.0.0.1:{port}")
    print("=====================================================================")
    app.run(host='0.0.0.0', port=port, debug=False)

