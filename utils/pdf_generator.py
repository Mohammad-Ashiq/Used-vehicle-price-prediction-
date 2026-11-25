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

def generate_prediction_pdf(prediction, filename=None):
    """
    Generates a clean, professional, automotive-themed PDF valuation report
    using ReportLab and returns the absolute file path.
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
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    NAVY = colors.HexColor('#0B132B')
    BLUE = colors.HexColor('#1C2541')
    ACCENT = colors.HexColor('#3A86FF')
    LIGHT_BG = colors.HexColor('#F8FAFC')
    BORDER = colors.HexColor('#CBD5E1')
    TEXT_MUTED = colors.HexColor('#64748B')
    SUCCESS = colors.HexColor('#059669')
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=NAVY,
        alignment=0
    )
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=TEXT_MUTED
    )
    section_head = ParagraphStyle(
        'SecHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=NAVY
    )
    price_head = ParagraphStyle(
        'PriceHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=TEXT_MUTED,
        alignment=1
    )
    price_val = ParagraphStyle(
        'PriceVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=ACCENT,
        alignment=1
    )
    price_sub = ParagraphStyle(
        'PriceSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=SUCCESS,
        alignment=1
    )
    cell_label = ParagraphStyle(
        'CellLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=NAVY
    )
    cell_val = ParagraphStyle(
        'CellVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )
    disclaimer_style = ParagraphStyle(
        'DiscStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=TEXT_MUTED
    )
    
    elements = []
    
    # 1. Header with branding
    header_data = [
        [
            Paragraph("<b>ReVahan &ndash; VEHICLE VALUATION REPORT</b>", title_style),
            Paragraph(f"<b>REPORT #RV-{prediction.get('id', '000')}</b><br/>"
                      f"Date: {prediction.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}", 
                      subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[380, 160])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceBefore=4, spaceAfter=14))
    
    # 2. Main Price Valuation Banner Card
    price_num = float(prediction.get('predicted_price', 0))
    min_num = float(prediction.get('price_min', price_num * 0.94))
    max_num = float(prediction.get('price_max', price_num * 1.06))
    
    banner_data = [
        [
            Paragraph("ESTIMATED FAIR RESALE MARKET VALUE", price_head),
        ],
        [
            Paragraph(f"Rs. {format_inr(price_num)}", price_val),
        ],
        [
            Paragraph(f"<b>{format_lakhs(price_num).replace('₹', 'Rs.')}</b> &nbsp;|&nbsp; Estimated Fair Range: Rs. {format_inr(min_num)} – Rs. {format_inr(max_num)}", price_sub)
        ]
    ]
    banner_table = Table(banner_data, colWidths=[540])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1.5, ACCENT),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(banner_table)
    elements.append(Spacer(1, 14))
    
    # 3. Vehicle Specifications Table
    elements.append(Paragraph("Vehicle Specifications Evaluated", section_head))
    elements.append(Spacer(1, 6))
    
    cat = str(prediction.get('category', 'Vehicle')).capitalize()
    
    specs = [
        [Paragraph("Category", cell_label), Paragraph(cat, cell_val),
         Paragraph("Brand", cell_label), Paragraph(str(prediction.get('brand', 'N/A')), cell_val)],
        [Paragraph("Model", cell_label), Paragraph(str(prediction.get('model', 'N/A')), cell_val),
         Paragraph("Manufacturing Year", cell_label), Paragraph(str(prediction.get('year', 'N/A')), cell_val)],
        [Paragraph("Kilometers Driven", cell_label), Paragraph(f"{int(prediction.get('km_driven', 0)):,} km", cell_val),
         Paragraph("Fuel Type", cell_label), Paragraph(str(prediction.get('fuel_type', 'N/A')), cell_val)],
        [Paragraph("Ownership Status", cell_label), Paragraph(str(prediction.get('owners', 'N/A')), cell_val),
         Paragraph("Vehicle Condition", cell_label), Paragraph(str(prediction.get('condition', 'N/A')), cell_val)],
        [Paragraph("Evaluation Location", cell_label), Paragraph(str(prediction.get('location', 'N/A')), cell_val),
         Paragraph("Estimated Age", cell_label), Paragraph(f"{Config.CURRENT_YEAR - int(prediction.get('year', Config.CURRENT_YEAR))} Years", cell_val)]
    ]
    
    # Category extra specs
    if cat.lower() == 'cars' and prediction.get('transmission'):
        specs.append([
            Paragraph("Transmission", cell_label), Paragraph(str(prediction.get('transmission', 'N/A')), cell_val),
            Paragraph("Engine Capacity", cell_label), Paragraph(f"{prediction.get('engine_cc', 'N/A')} CC", cell_val)
        ])
    elif cat.lower() == 'bikes' and prediction.get('engine_cc'):
        specs.append([
            Paragraph("Engine Displacement", cell_label), Paragraph(f"{prediction.get('engine_cc', 'N/A')} CC", cell_val),
            Paragraph("Type", cell_label), Paragraph("Two-Wheeler / Motorcycle", cell_val)
        ])
    elif cat.lower() == 'lorries' and prediction.get('load_capacity'):
        specs.append([
            Paragraph("Load Capacity", cell_label), Paragraph(f"{prediction.get('load_capacity', 'N/A')} Tons", cell_val),
            Paragraph("Vehicle Class", cell_label), Paragraph(str(prediction.get('vehicle_type', 'Commercial')), cell_val)
        ])
    elif cat.lower() == 'autos' and prediction.get('passenger_capacity'):
        specs.append([
            Paragraph("Passenger Capacity", cell_label), Paragraph(str(prediction.get('passenger_capacity', 'N/A')), cell_val),
            Paragraph("Segment", cell_label), Paragraph("Three-Wheeler Commercial", cell_val)
        ])
        
    specs_table = Table(specs, colWidths=[120, 150, 120, 150])
    specs_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    elements.append(specs_table)
    elements.append(Spacer(1, 14))
    
    # 4. Valuation Methodology & Model Parameters
    elements.append(Paragraph("Machine Learning Valuation Intelligence", section_head))
    elements.append(Spacer(1, 6))
    
    methodology_text = (
        "This estimation was determined by an ensemble Random Forest Regressor trained on thousands of authentic "
        "Indian automotive transactions. The model performs multi-variable regression balancing non-linear depreciation "
        "curves, odometer mileage wear, ownership transfer degradation, fuel type demand, and condition grading."
    )
    elements.append(Paragraph(methodology_text, subtitle_style))
    elements.append(Spacer(1, 8))
    
    # Factors Table
    factors_data = [
        [Paragraph("Key Value Driver", cell_label), Paragraph("Market Assessment & Impact", cell_label)],
        [Paragraph("Age & Depreciation", cell_val), Paragraph("Depreciated based on standard automotive lifecycle retention curves.", cell_val)],
        [Paragraph("Odometer Running", cell_val), Paragraph(f"{int(prediction.get('km_driven', 0)):,} km evaluated against standard vehicle usage benchmarks.", cell_val)],
        [Paragraph("Physical Condition", cell_val), Paragraph(f"Graded as '{prediction.get('condition', 'Good')}', setting cosmetic and mechanical baseline.", cell_val)],
        [Paragraph("Ownership Multiplier", cell_val), Paragraph(f"Registered under '{prediction.get('owners', '1st Owner')}' title.", cell_val)]
    ]
    factors_table = Table(factors_data, colWidths=[160, 380])
    factors_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, BORDER),
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(factors_table)
    elements.append(Spacer(1, 14))
    
    # 5. Disclaimer & Verification Footer
    disclaimer_text = (
        "<b>LEGAL & MARKET DISCLAIMER:</b> This appraisal report is generated using statistical Machine Learning algorithms "
        "and is intended solely as an advisory reference for buyers and sellers. It does not constitute an official insurance "
        "survey, certified vehicle inspection, or guaranteed legal sale price. Actual transaction prices may vary depending "
        "on local market demand, tyre condition, accident history, RTO tax dues, and service records."
    )
    elements.append(KeepTogether([
        HRFlowable(width="100%", thickness=0.5, color=BORDER, spaceBefore=4, spaceAfter=8),
        Paragraph(disclaimer_text, disclaimer_style),
        Spacer(1, 8),
        Paragraph("ReVahan Valuation Engine &bull; Powered by Scikit-Learn Random Forest Regressor & Flask", 
                  ParagraphStyle('Foot', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, textColor=NAVY, alignment=1))
    ]))
    
    doc.build(elements)
    return pdf_path
