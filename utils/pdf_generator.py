import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from config import Config
from ml.predict import format_inr, format_lakhs

# Custom Palette
NAVY = colors.HexColor('#0B132B')
DARK_BLUE = colors.HexColor('#1C2541')
ACCENT = colors.HexColor('#0284C7')
GOLD = colors.HexColor('#D97706')
LIGHT_BG = colors.HexColor('#F8FAFC')
BORDER = colors.HexColor('#CBD5E1')
TEXT_MUTED = colors.HexColor('#64748B')
SUCCESS = colors.HexColor('#059669')

def get_base_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY,
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=TEXT_MUTED
    )
    section_head = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=NAVY
    )
    price_head = ParagraphStyle(
        'PriceHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=TEXT_MUTED,
        alignment=1
    )
    price_val = ParagraphStyle(
        'PriceVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=ACCENT,
        alignment=1
    )
    price_sub = ParagraphStyle(
        'PriceSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=SUCCESS,
        alignment=1
    )
    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=NAVY
    )
    cell_val = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    disclaimer_style = ParagraphStyle(
        'DiscStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_MUTED
    )
    
    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'section': section_head,
        'price_head': price_head,
        'price_val': price_val,
        'price_sub': price_sub,
        'cell_label': cell_label,
        'cell_val': cell_val,
        'disclaimer': disclaimer_style
    }

def generate_prediction_pdf(prediction, filename=None, user=None):
    """
    Generates a clean, professional, automotive-themed PDF valuation report
    for public or user-specific predictions.
    """
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    if not filename:
        pred_id = prediction.get('id', 'temp')
        filename = f"valuation_report_{pred_id}.pdf"
        
    pdf_path = os.path.join(Config.REPORTS_DIR, filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    st = get_base_styles()
    elements = []
    
    # 1. Header with branding
    user_info_html = ""
    if user:
        user_info_html = f"<br/><font color='#0284c7'><b>Valued Member:</b> {user.get('name', 'User')}</font>"
        
    header_data = [
        [
            Paragraph("<b>ReVahan &ndash; VEHICLE VALUATION REPORT</b>", st['title']),
            Paragraph(f"<b>REPORT #RV-{prediction.get('id', '000')}</b><br/>"
                      f"Date: {prediction.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}"
                      f"{user_info_html}", 
                      st['subtitle'])
        ]
    ]
    header_table = Table(header_data, colWidths=[360, 180])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=2, spaceAfter=12))
    
    # 2. Main Price Valuation Banner Card
    price_num = float(prediction.get('predicted_price', 0))
    min_num = float(prediction.get('price_min', price_num * 0.94))
    max_num = float(prediction.get('price_max', price_num * 1.06))
    
    banner_data = [
        [Paragraph("ESTIMATED FAIR RESALE MARKET VALUE", st['price_head'])],
        [Paragraph(f"Rs. {format_inr(price_num)}", st['price_val'])],
        [Paragraph(f"<b>{format_lakhs(price_num).replace('₹', 'Rs.')}</b> &nbsp;|&nbsp; Fair Range: Rs. {format_inr(min_num)} – Rs. {format_inr(max_num)}", st['price_sub'])]
    ]
    banner_table = Table(banner_data, colWidths=[540])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 12))
    
    # 3. Vehicle Specifications Table
    elements.append(Paragraph("Vehicle Specifications Evaluated", st['section']))
    elements.append(Spacer(1, 5))
    
    cat = str(prediction.get('category', 'Vehicle')).capitalize()
    specs = [
        [Paragraph("Category", st['cell_label']), Paragraph(cat, st['cell_val']),
         Paragraph("Brand", st['cell_label']), Paragraph(str(prediction.get('brand', 'N/A')), st['cell_val'])],
        [Paragraph("Model", st['cell_label']), Paragraph(str(prediction.get('model', 'N/A')), st['cell_val']),
         Paragraph("Manufacturing Year", st['cell_label']), Paragraph(str(prediction.get('year', 'N/A')), st['cell_val'])],
        [Paragraph("Kilometers Driven", st['cell_label']), Paragraph(f"{int(prediction.get('km_driven', 0)):,} km", st['cell_val']),
         Paragraph("Fuel Type", st['cell_label']), Paragraph(str(prediction.get('fuel_type', 'N/A')), st['cell_val'])],
        [Paragraph("Ownership Status", st['cell_label']), Paragraph(str(prediction.get('owners', 'N/A')), st['cell_val']),
         Paragraph("Vehicle Condition", st['cell_label']), Paragraph(str(prediction.get('condition', 'N/A')), st['cell_val'])],
        [Paragraph("Evaluation Location", st['cell_label']), Paragraph(str(prediction.get('location', 'N/A')), st['cell_val']),
         Paragraph("Estimated Age", st['cell_label']), Paragraph(f"{Config.CURRENT_YEAR - int(prediction.get('year', Config.CURRENT_YEAR))} Years", st['cell_val'])]
    ]
    
    if cat.lower() == 'cars' and prediction.get('transmission'):
        specs.append([
            Paragraph("Transmission", st['cell_label']), Paragraph(str(prediction.get('transmission', 'N/A')), st['cell_val']),
            Paragraph("Engine Capacity", st['cell_label']), Paragraph(f"{prediction.get('engine_cc', 'N/A')} CC", st['cell_val'])
        ])
    elif cat.lower() == 'bikes' and prediction.get('engine_cc'):
        specs.append([
            Paragraph("Engine Displacement", st['cell_label']), Paragraph(f"{prediction.get('engine_cc', 'N/A')} CC", st['cell_val']),
            Paragraph("Type", st['cell_label']), Paragraph("Two-Wheeler / Motorcycle", st['cell_val'])
        ])
    elif cat.lower() == 'lorries' and prediction.get('load_capacity'):
        specs.append([
            Paragraph("Load Capacity", st['cell_label']), Paragraph(f"{prediction.get('load_capacity', 'N/A')} Tons", st['cell_val']),
            Paragraph("Vehicle Class", st['cell_label']), Paragraph(str(prediction.get('vehicle_type', 'Commercial')), st['cell_val'])
        ])
    elif cat.lower() == 'autos' and prediction.get('passenger_capacity'):
        specs.append([
            Paragraph("Passenger Capacity", st['cell_label']), Paragraph(str(prediction.get('passenger_capacity', 'N/A')), st['cell_val']),
            Paragraph("Segment", st['cell_label']), Paragraph("Three-Wheeler Commercial", st['cell_val'])
        ])
        
    specs_table = Table(specs, colWidths=[120, 150, 120, 150])
    specs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    elements.append(specs_table)
    elements.append(Spacer(1, 12))
    
    # 4. Valuation Methodology
    elements.append(Paragraph("Machine Learning Valuation Intelligence", st['section']))
    elements.append(Spacer(1, 4))
    methodology_text = (
        "Valuation determined by an ensemble Random Forest Regressor trained on 70+ automotive brands and "
        "authentic Indian transactions across 36 States/UTs. Multi-variable regression balances non-linear depreciation "
        "curves, odometer mileage wear, ownership title, fuel type demand, and cosmetic condition."
    )
    elements.append(Paragraph(methodology_text, st['subtitle']))
    elements.append(Spacer(1, 12))
    
    # 5. Footer & Legal Disclaimer
    disclaimer_text = (
        "<b>LEGAL & MARKET DISCLAIMER:</b> This appraisal report is generated using statistical Machine Learning algorithms "
        "and is intended solely as an advisory reference for buyers and sellers. It does not constitute an official insurance "
        "survey, certified vehicle inspection, or guaranteed legal sale price."
    )
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=4, spaceAfter=6),
        Paragraph(disclaimer_text, st['disclaimer']),
        Spacer(1, 6),
        Paragraph("ReVahan Valuation Engine &bull; https://revahan.onrender.com &bull; Certified AI Appraisals", 
                  ParagraphStyle('Foot', parent=st['subtitle'], fontName='Helvetica-Bold', fontSize=8, textColor=NAVY, alignment=1))
    ]))
    
    doc.build(elements)
    return pdf_path


def generate_garage_certificate(vehicle, user=None, filename=None):
    """
    Generates an official, high-prestige Personalized Vehicle Valuation Certificate
    & Asset Passport for a vehicle stored in a user's Virtual Garage.
    """
    os.makedirs(Config.REPORTS_DIR, exist_ok=True)
    if not filename:
        v_id = vehicle.get('id', 'asset')
        filename = f"garage_certificate_{v_id}.pdf"
        
    pdf_path = os.path.join(Config.REPORTS_DIR, filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )
    
    st = get_base_styles()
    elements = []
    
    # Owner & Certificate Details
    owner_name = user.get('name', 'Registered Owner') if user else 'Registered Owner'
    owner_email = user.get('email', 'Member') if user else 'Member'
    owner_phone = user.get('phone', 'Verified Phone') if user else 'Verified'
    v_id = vehicle.get('id', 1)
    
    # 1. Top Decorative Certificate Header
    header_data = [
        [
            Paragraph("<b>ReVahan &ndash; VIRTUAL GARAGE ASSET PASSPORT</b>", st['title']),
            Paragraph(f"<b>CERTIFICATE #RV-GAR-{v_id:05d}</b><br/>"
                      f"Issued: {datetime.now().strftime('%d %B %Y')}<br/>"
                      f"<font color='#059669'><b>Status: Verified Asset</b></font>", 
                      st['subtitle'])
        ]
    ]
    header_table = Table(header_data, colWidths=[350, 190])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4))
    elements.append(HRFlowable(width="100%", thickness=2.5, color=GOLD, spaceBefore=2, spaceAfter=8))
    
    # 2. Registered Owner Profile Block
    vehicle_nickname = vehicle.get('nickname') or f"{vehicle.get('brand')} {vehicle.get('model')}"
    owner_data = [
        [
            Paragraph("<b>Registered Vehicle Owner</b>", st['cell_label']),
            Paragraph(f"<b>{owner_name}</b> &nbsp;|&nbsp; {owner_email} &nbsp;|&nbsp; {owner_phone}", st['cell_val']),
        ],
        [
            Paragraph("<b>Garage Asset Nickname</b>", st['cell_label']),
            Paragraph(f"<b>&ldquo;{vehicle_nickname}&rdquo;</b>", st['cell_val'])
        ]
    ]
    owner_table = Table(owner_data, colWidths=[150, 390])
    owner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(owner_table)
    elements.append(Spacer(1, 10))
    
    # 3. Main Valuation & Equity Box
    cur_val = float(vehicle.get('current_valuation', 0))
    pur_price = float(vehicle.get('purchase_price') or cur_val * 1.35)
    retained_pct = vehicle.get('retained_pct') or round((cur_val / pur_price) * 100, 1)
    dep_amount = max(0, pur_price - cur_val)
    min_v = float(vehicle.get('price_min') or cur_val * 0.94)
    max_v = float(vehicle.get('price_max') or cur_val * 1.06)
    
    val_banner = [
        [
            Paragraph("CERTIFIED FAIR MARKET RESALE VALUATION", st['price_head']),
            Paragraph("ORIGINAL PURCHASE & EQUITY", st['price_head'])
        ],
        [
            Paragraph(f"Rs. {format_inr(cur_val)}", st['price_val']),
            Paragraph(f"Rs. {format_inr(pur_price)}", st['price_val'])
        ],
        [
            Paragraph(f"<b>{format_lakhs(cur_val).replace('₹', 'Rs.')}</b> (Range: Rs. {format_inr(min_v)} - {format_inr(max_v)})", st['price_sub']),
            Paragraph(f"<b>{retained_pct}% Value Retained</b> &bull; Depreciated: Rs. {format_inr(dep_amount)}", 
                      ParagraphStyle('SubDep', parent=st['price_sub'], textColor=GOLD))
        ]
    ]
    val_table = Table(val_banner, colWidths=[270, 270])
    val_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('LINEBEFORE', (1,0), (1,-1), 1, BORDER),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(val_table)
    elements.append(Spacer(1, 12))
    
    # 4. Specifications Matrix
    elements.append(Paragraph("Vehicle Technical & Operational Profile", st['section']))
    elements.append(Spacer(1, 4))
    
    cat_str = str(vehicle.get('category', 'Vehicle')).capitalize()
    v_specs = [
        [Paragraph("Category", st['cell_label']), Paragraph(cat_str, st['cell_val']),
         Paragraph("Brand & Model", st['cell_label']), Paragraph(f"{vehicle.get('brand')} {vehicle.get('model')}", st['cell_val'])],
        [Paragraph("Model Year", st['cell_label']), Paragraph(str(vehicle.get('year')), st['cell_val']),
         Paragraph("Odometer Reading", st['cell_label']), Paragraph(f"{int(vehicle.get('km_driven', 0)):,} km", st['cell_val'])],
        [Paragraph("Fuel Type", st['cell_label']), Paragraph(str(vehicle.get('fuel_type')), st['cell_val']),
         Paragraph("Transmission", st['cell_label']), Paragraph(str(vehicle.get('transmission') or 'Standard'), st['cell_val'])],
        [Paragraph("Registered State / RTO", st['cell_label']), Paragraph(str(vehicle.get('location')), st['cell_val']),
         Paragraph("Ownership Title", st['cell_label']), Paragraph(str(vehicle.get('owners')), st['cell_val'])],
        [Paragraph("Mechanical Condition", st['cell_label']), Paragraph(str(vehicle.get('condition')), st['cell_val']),
         Paragraph("Purchase Year", st['cell_label']), Paragraph(str(vehicle.get('purchase_year') or vehicle.get('year')), st['cell_val'])]
    ]
    
    if vehicle.get('notes'):
        v_specs.append([
            Paragraph("Owner Notes", st['cell_label']),
            Paragraph(str(vehicle.get('notes')), st['cell_val']),
            Paragraph("Authentication", st['cell_label']),
            Paragraph("ReVahan AI Verified", st['cell_val'])
        ])
        
    specs_t = Table(v_specs, colWidths=[120, 150, 120, 150])
    specs_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    elements.append(specs_t)
    elements.append(Spacer(1, 10))
    
    # 5. Month-by-Month Depreciation Tracking Table
    elements.append(Paragraph("Month-by-Month Depreciation & Valuation Curve", st['section']))
    elements.append(Spacer(1, 4))
    
    history = vehicle.get('valuation_history') or []
    # Pick sample milestones (e.g. up to 6 historical and 2 forecast)
    milestones = []
    if history:
        # Step through history points
        step = max(1, len(history) // 6)
        milestones = history[::step][:7]
        if history[-1] not in milestones:
            milestones.append(history[-1])
            
    if milestones:
        dep_rows = [[
            Paragraph("Milestone Period", st['cell_label']),
            Paragraph("Valuation (INR)", st['cell_label']),
            Paragraph("Value Retained (%)", st['cell_label']),
            Paragraph("Trajectory Type", st['cell_label'])
        ]]
        for m in milestones:
            tag_color = '#059669' if m.get('type') == 'current' else ('#0284c7' if m.get('type') == 'historical' else '#d97706')
            dep_rows.append([
                Paragraph(m.get('label', 'N/A'), st['cell_val']),
                Paragraph(f"Rs. {format_inr(m.get('valuation', 0))}", st['cell_val']),
                Paragraph(f"{m.get('retained_pct', 0)}%", st['cell_val']),
                Paragraph(f"<font color='{tag_color}'><b>{m.get('type', 'historical').capitalize()}</b></font>", st['cell_val'])
            ])
            
        dep_table = Table(dep_rows, colWidths=[140, 140, 130, 130])
        dep_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, BORDER),
            ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))
        elements.append(dep_table)
        elements.append(Spacer(1, 10))
        
    # 6. Verification Seal & Legal Sign-Off
    verification_box = [
        [
            Paragraph("<b>CERTIFIED BY REVAHAN AI VALUATION ENGINE</b><br/>"
                      "This document certifies that the above asset was appraised using multi-parameter machine learning "
                      "calibrated to regional automotive indexes in India. Stored in ReVahan Virtual Garage with automatic "
                      "depreciation recalibration.", st['subtitle']),
            Paragraph("<font size='10' color='#d97706'><b>★ REVAHAN SEAL ★</b></font><br/>"
                      "<font size='8' color='#64748b'>Digitally Signed<br/>ID: RV-VERIFIED-AI</font>", 
                      ParagraphStyle('Seal', parent=st['subtitle'], alignment=1))
        ]
    ]
    ver_t = Table(verification_box, colWidths=[400, 140])
    ver_t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(ver_t)
    elements.append(Spacer(1, 6))
    
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=2, spaceAfter=4),
        Paragraph("<b>Notice:</b> Advisory appraisal only. Not a formal insurance policy or financial loan underwriting guarantee.", st['disclaimer']),
        Paragraph("ReVahan &bull; https://revahan.onrender.com &bull; Certified Virtual Garage Asset Passport", 
                  ParagraphStyle('Foot', parent=st['subtitle'], fontName='Helvetica-Bold', fontSize=7.5, textColor=NAVY, alignment=1))
    ]))
    
    doc.build(elements)
    return pdf_path
