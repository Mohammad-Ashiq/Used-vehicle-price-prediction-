"""
=============================================================================
ReVahan - AI Voice Assistant Intelligence Engine
Two-Way Conversational NLU • Instant Real-time ML Prediction • Zero Repetitive Intros
=============================================================================
"""

import re
from datetime import datetime
from config import Config
from ml.predict import predict_price, format_inr, format_lakhs
from database.db import save_prediction

CURRENT_YEAR = 2026

# Comprehensive Automotive Domain Knowledge Base (Evaluated first for direct domain answers)
KNOWLEDGE_BASE = [
    # 1. Greetings (Direct, natural, friendly - handles all colloquial variations)
    {
        'patterns': [
            r'\b(h+l+o+|h+e+l+o+|h+a+l+o+|h+e+y+|h+i+|h+a+i+|y+o+|s+u+p+|w+a+s+s?u+p+|w+h?a+t+s?\s*u+p+|g+o+o+d\s*(morning|afternoon|evening|day)|namaste|vanakkam|pranam|hello|hi)\b'
        ],
        'response': "Hello! I am ready to help. Which vehicle would you like to check today? (For example: Classic 350, Swift, Creta, or Tata Truck)."
    },
    # 2. Well-being / Chit-chat
    {
        'patterns': [r'\b(how are you|how r u|how do you do|how.*going|sab badhiya|kya haal)\b'],
        'response': "I am doing great and ready to evaluate vehicles! Which car, bike, truck, or auto would you like to price today?"
    },
    # 3. Explicit Identity
    {
        'patterns': [r'\b(who are you|your name|what is your name|who made you|who created you)\b'],
        'response': "I am the ReVahan AI Voice Assistant, powered by Machine Learning to predict fair resale prices and provide automotive market guidance."
    },
    # 4. Gratitude & Pleasantries
    {
        'patterns': [r'\b(thank you|thanks|thank u|thx|shukriya|dhanyawad)\b'],
        'response': "You're very welcome! Feel free to ask about any other vehicle valuation or market question."
    },
    # 5. Farewell (Strict pattern to NEVER clash with 'Tata' vehicles)
    {
        'patterns': [r'\b(bye\s*bye|goodbye|see\s*you|cya|good\s*night)\b|^(bye|tata\s*bye|tata\s*tata)$'],
        'response': "Goodbye! Have a great day and drive safely!"
    },
    # 6. What can you do / Capabilities
    {
        'patterns': [r'\b(what can you do|help me|how can you help|features|capabilities)\b'],
        'response': "You can ask me to estimate the resale price of any car, bike, commercial truck, or auto-rickshaw, or ask about vehicle depreciation, condition, and market trends."
    },
    # 7. Model FAQ: Classic 350
    {
        'patterns': [r'\b(classic 350.*(mileage|average|resale|review|popular|worth it|good|issues|problem))\b', r'\b(mileage.*classic 350)\b'],
        'response': "The Royal Enfield Classic 350 delivers 32 to 37 kmpl in mixed driving. It is India's highest resale retention motorcycle, holding up to 70% of its purchase price after 3 years thanks to huge enthusiast demand."
    },
    # 8. Model FAQ: Swift
    {
        'patterns': [r'\b(swift.*(mileage|average|resale|review|popular|worth it|good|issues|problem))\b', r'\b(mileage.*swift)\b'],
        'response': "The Maruti Suzuki Swift delivers 22 to 25 kmpl. It is India's fastest-selling resale car due to bulletproof engine reliability, minimal maintenance costs, and widely available spare parts."
    },
    # 9. Model FAQ: Creta
    {
        'patterns': [r'\b(creta.*(mileage|average|resale|review|popular|worth it|good))\b'],
        'response': "The Hyundai Creta retains up to 70% of its initial value after 3 years, leading the compact SUV segment in resale liquidity due to strong brand trust and high pre-owned buyer demand."
    },
    # 10. Model FAQ: Activa
    {
        'patterns': [r'\b(activa.*(mileage|average|resale|review|popular))\b'],
        'response': "The Honda Activa delivers 45 to 50 kmpl. Its metal body and low maintenance make it the most liquid pre-owned two-wheeler in India, often selling within 48 hours of listing."
    },
    # 11. Model FAQ: Splendor
    {
        'patterns': [r'\b(splendor.*(mileage|average|resale|review|popular))\b'],
        'response': "Hero Splendor offers an impressive 65+ kmpl. It has unmatched resale liquidity across both urban and rural India with almost zero depreciation between years 3 and 7."
    },
    # 12. Top Resale Bike Query
    {
        'patterns': [r'\b(best\s*(bike|two\s*wheeler).*(resale|value)|(which|what)\s*bike.*(best|resale)|best\s*resale\s*bike)\b'],
        'response': "The Royal Enfield Classic 350, Honda Activa, and Hero Splendor hold the highest resale value retention among two-wheelers in India, often retaining 65% to 70% of original price after 3 years."
    },
    # 13. Top Resale Car Query
    {
        'patterns': [r'\b(best\s*car.*(resale|value)|(which|what)\s*car.*(best|resale)|best\s*resale\s*car|fastest\s*selling\s*car)\b'],
        'response': "Maruti Suzuki Swift, Baleno, and Hyundai Creta lead used car resale retention in India, retaining over 65% of purchase value after 3 years due to immense liquidity and affordable spare parts."
    },
    # 14. Mileage / Odometer Wear
    {
        'patterns': [r'\b(mileage|odometer|high km|high mileage|distance)\b', r'\bhow.*(km|kilometer).*affect\b'],
        'response': "Every additional 10,000 kilometers typically reduces a vehicle's resale value by 2% to 4%, because higher mileage implies greater wear on the engine, suspension, and brake components."
    },
    # 15. Documentation / RC Transfer / RTO
    {
        'patterns': [r'\b(document|documents|rc|transfer|rto|paper|papers|form 29|form 30)\b'],
        'response': "To sell a used vehicle legally, you need the original Registration Certificate (RC), valid Insurance, Pollution Certificate (PUC), signed Form 29 and Form 30 for RTO transfer, and a bank NOC if a loan was active."
    },
    # 16. Best time to sell a vehicle
    {
        'patterns': [r'\b(when to sell|best time to sell|right time to sell)\b'],
        'response': "The best time to sell is before your vehicle completes 5 years of age or 50,000 kilometers, ideally during festive periods like Diwali or Navratri when pre-owned buyer demand is highest."
    },
    # 17. Fuel Type Comparisons (Petrol, Diesel, CNG, EV)
    {
        'patterns': [r'\b(diesel vs petrol|petrol or diesel|best fuel|cng vs petrol|electric car resale|ev resale|10 year rule)\b'],
        'response': "In India, Petrol and factory-fitted CNG vehicles hold the highest resale demand in cities. In Delhi NCR, diesel cars face a 10-year limit compared to 15 years for petrol, making petrol vehicles hold value better."
    },
    # 18. Physical Condition & Accidents
    {
        'patterns': [r'\b(scratch|dent|paint|accident|accidental|damage)\b', r'\bhow.*condition.*affect\b'],
        'response': "Physical and mechanical condition impacts vehicle price by up to 25%. Original showroom paint, rust-free underbody, and clean accident-free service records earn the highest market valuation."
    },
    # 19. Number of Owners (1st vs 2nd vs 3rd owner)
    {
        'patterns': [r'\b(1st owner|2nd owner|second hand|second owner|multiple owners)\b', r'\bhow.*owner.*affect\b'],
        'response': "A second-owner vehicle generally trades at 10% to 15% lower than a single-owner vehicle of the same model and year, because buyers associate multiple owners with inconsistent maintenance."
    },
    # 20. Insurance Impact
    {
        'patterns': [r'\b(insurance|zero dep|policy|third party|comprehensive)\b'],
        'response': "A valid comprehensive or zero-depreciation insurance policy adds 3% to 5% value to your resale price, whereas an expired policy leads to immediate negotiation discounts from buyers."
    },
    # 21. Tyre & Battery Wear
    {
        'patterns': [r'\b(tyre|tyres|tread|battery|wheel)\b'],
        'response': "Worn tyres with less than 3 millimeters tread depth reduce resale value by 15,000 to 30,000 Rupees, since buyers factor in the immediate cost of a replacement set."
    },
    # 22. Transmission: Automatic vs Manual
    {
        'patterns': [r'\b(automatic vs manual|manual vs automatic|automatic or manual|amt|cvt|torque converter)\b'],
        'response': "Automatic cars in traffic-dense cities like Delhi, Mumbai, and Bangalore now sell for a 5% to 8% premium over manual equivalents due to increasing urban driving convenience."
    },
    # 23. Commercial Lorries & Trucks
    {
        'patterns': [r'\b(how to value.*(truck|lorry)|commercial vehicle valuation|truck permit|fitness certificate)\b'],
        'response': "Commercial truck valuation depends primarily on national or state permit validity, fitness certificate duration, payload tonnage capacity, and engine health rather than strictly odometer kilometers."
    },
    # 24. Auto-rickshaws
    {
        'patterns': [r'\b(how to value.*auto|rickshaw permit|auto-rickshaw valuation)\b'],
        'response': "Auto-rickshaw resale value depends heavily on city permit availability, valid hydro-tested CNG cylinder certificates, and engine compression health."
    },
    # 25. Machine Learning Algorithm & Architecture
    {
        'patterns': [r'\b(algorithm|machine learning|random forest|decision tree|how it calculates|math behind)\b'],
        'response': "ReVahan uses an ensemble of 120 Random Forest decision trees trained on multi-regional market transaction data. It models non-linear vehicle depreciation without arbitrary human bias."
    },
    # 26. Accuracy & Metrics (R², MAE, RMSE)
    {
        'patterns': [r'\b(accuracy|r2|mae|rmse|reliable|how accurate|confidence score)\b'],
        'response': "The model achieves test accuracy of 84.4% for Cars, 88.7% for Bikes, 91.9% for Lorries, and 91.7% for Auto-rickshaws, with negotiation intervals calculated using Root Mean Squared Error."
    },
    # 27. PDF Valuation Certificate
    {
        'patterns': [r'\b(pdf|report|certificate|download certificate|print report)\b'],
        'response': "Every appraisal generates a certified PDF Valuation Report containing full technical specifications, negotiation range, and depreciation factor breakdown that you can print or download immediately."
    },
    # 28. History & SQLite Database
    {
        'patterns': [r'\b(database|history|sqlite|saved records|audit trail)\b'],
        'response': "All user appraisals are stored in an SQLite relational database. You can search, filter by vehicle category, or view past valuations on the History page."
    },
    # 29. How to increase resale value / selling tips
    {
        'patterns': [r'\b(sell tips|increase value|better price|maximize price|higher selling price)\b'],
        'response': "To maximize selling price: get the car professionally detailed, service it with authorized bills, replace worn wiper blades, touch up minor surface scratches, and keep all service invoices ready."
    },
    # 30. Loan / Hypothecation (HP)
    {
        'patterns': [r'\b(loan|hypothecation|noc|bank emi|clearing loan)\b'],
        'response': "If the vehicle is financed, you must obtain a Form 35 and Bank NOC confirming loan clearance before the RTO will approve ownership transfer to a buyer."
    },
    # 31. Inspection before buying
    {
        'patterns': [r'\b(inspection|inspect|buying tips|buy used|check before buying)\b'],
        'response': "Before buying a used vehicle: inspect the engine bay for fluid leaks, verify odometer reading against service bills, check tyre manufacturing date codes, and test drive on both city roads and open highway."
    },
    # 32. Negotiation advice
    {
        'patterns': [r'\b(negotiate|negotiation|bargain|discount|deal advice)\b'],
        'response': "When negotiating, use the vehicle's fair range: buyers should offer near the minimum range if tyres or insurance are expiring soon, while sellers with complete service records should stick close to the fair market average."
    }
]

# Vehicle Keywords for Smart Prediction Trigger
KNOWN_VEHICLE_NAMES = [
    # Cars
    'swift', 'baleno', 'dzire', 'wagon r', 'wagonr', 'brezza', 'ertiga', 'alto', 'alto 800',
    'i20', 'creta', 'verna', 'venue', 'grand i10', 'i10', 'alcazar',
    'nexon', 'punch', 'altroz', 'harrier', 'safari', 'tiago',
    'city', 'amaze', 'elevate', 'wr-v', 'wrv', 'jazz',
    'scorpio', 'scorpio-n', 'thar', 'xuv700', 'xuv300', 'bolero',
    'innova', 'innova crysta', 'fortuner', 'urban cruiser', 'glanza', 'camry',
    'seltos', 'sonet', 'carens', 'carnival',
    'polo', 'virtus', 'taigun', 'vento',
    # Bikes
    'splendor', 'splendor plus', 'hf deluxe', 'glamour', 'xpulse', 'passion pro',
    'activa', 'activa 6g', 'shine', 'shine 125', 'unicorn', 'hornet', 'dio',
    'pulsar', 'pulsar 150', 'pulsar ns200', 'platina', 'dominar', 'avenger',
    'apache', 'apache rtr', 'jupiter', 'raider', 'ntorq',
    'classic 350', 'hunter 350', 'bullet', 'bullet 350', 'meteor 350', 'himalayan',
    'fz', 'fz-s', 'mt-15', 'mt15', 'r15', 'rayzr', 'aerox',
    'duke', 'duke 200', 'duke 390', 'rc 200',
    'access', 'access 125', 'gixxer', 'burgman', 'v-strom',
    # Commercial Lorries
    'tata 407', 'tata truck', 'tata lpt', 'tata prima', 'tata signa', 'tata ace',
    'dost strong', 'dost', 'ecomet', 'captain', 'ashok leyland',
    'eicher', 'pro 2049', 'pro 3019', 'bharatbenz', 'bolero maxi truck',
    # Autos
    'bajaj re', 'compact 4s', 're optima', 'auto rickshaw', 'autorickshaw', 'rickshaw', 'tuk tuk',
    'ape city', 'piaggio ape', 'alfa dx', 'treo', 'king deluxe'
]


def parse_vehicle_voice_command(query):
    """
    Intelligently parses vehicle parameters from voice query:
    e.g. 'classic 350' -> Royal Enfield Classic 350, 2021, 20,000 km
         'swift' -> Maruti Suzuki Swift, 2021, 30,000 km
         'tata truck' -> Tata Motors Tata 407 Gold, 2020, 75,000 km
         'predict car price for 2021 Swift with 30000 km'
         'estimate bike value 2020 Classic 350 15000 km'
    """
    q = query.lower()

    # 1. Detect Category
    category = None
    if any(w in q for w in ['lorry', 'truck', 'container', 'tipper', 'tonnage', 'lcv', 'tata 407', 'eicher', 'ashok leyland', 'bharatbenz']):
        category = 'lorries'
    elif any(w in q for w in ['auto', 'rickshaw', 'tuk tuk', 'three wheeler', '3 wheeler', 'ape', 'bajaj re', 'compact 4s']):
        category = 'autos'
    elif any(w in q for w in ['bike', 'motorcycle', 'scooter', 'bullet', 'pulsar', 'splendor', 'activa', 'duke', 'enfield', 'classic 350', 'hunter', 'jupiter', 'apache', 'r15', 'yamaha', 'hero', 'ktm']):
        category = 'bikes'
    elif any(w in q for w in ['car', 'suv', 'sedan', 'hatchback', 'swift', 'creta', 'verna', 'baleno', 'city', 'nexon', 'innova', 'thar', 'scorpio', 'fortuner', 'seltos']):
        category = 'cars'

    # Fallback category scan across config brands/models
    if not category:
        for cat, info in Config.CATEGORIES_INFO.items():
            for b, models in info['brands'].items():
                if b.lower() in q or any(m.lower() in q for m in models):
                    category = cat
                    break
            if category:
                break

    if not category:
        category = 'cars'

    cat_info = Config.CATEGORIES_INFO[category]

    # Extract all numbers in query
    all_numbers = [int(n) for n in re.findall(r'\b\d+\b', q)]

    # 2. Detect Year (between 2000 and 2026)
    year = None
    for n in all_numbers:
        if 2000 <= n <= 2026:
            year = n
            break
    if not year:
        # Intelligent category-specific default year
        year = 2021 if category in ['cars', 'bikes', 'autos'] else 2020

    # 3. Detect Kilometers
    km = None
    km_match = re.search(r'(\d+)\s*(?:k|thousand|km|kms|kilometer|kilometers)', q)
    if km_match:
        num = int(km_match.group(1))
        km = num * 1000 if num < 500 else num
    else:
        for n in all_numbers:
            if n != year and n != 350 and n >= 500:  # Avoid matching model 350 in Classic 350 as km
                km = n
                break
    if not km:
        # Category-appropriate standard odometer reading
        if category == 'bikes':
            km = 20000
        elif category == 'cars':
            km = 30000
        elif category == 'lorries':
            km = 75000
        else:
            km = 35000

    # 4. Detect Brand and Model
    detected_brand = None
    detected_model = None

    for brand, models in cat_info['brands'].items():
        if brand.lower() in q:
            detected_brand = brand
            for m in models:
                if m.lower() in q:
                    detected_model = m
                    break
            break
        for m in models:
            if m.lower() in q:
                detected_brand = brand
                detected_model = m
                break
        if detected_brand:
            break

    # Colloquial mapping if not detected
    if not detected_brand:
        if 'classic 350' in q or 'classic' in q or 'enfield' in q or 'bullet' in q:
            category = 'bikes'
            detected_brand, detected_model = 'Royal Enfield', 'Classic 350'
        elif 'swift' in q:
            category = 'cars'
            detected_brand, detected_model = 'Maruti Suzuki', 'Swift'
        elif 'creta' in q:
            category = 'cars'
            detected_brand, detected_model = 'Hyundai', 'Creta'
        elif 'truck' in q or 'lorry' in q or 'tata' in q:
            category = 'lorries'
            detected_brand, detected_model = 'Tata Motors', 'Tata 407 Gold'
        elif 'auto' in q or 'rickshaw' in q:
            category = 'autos'
            detected_brand, detected_model = 'Bajaj', 'Compact 4S'
        else:
            if category == 'cars':
                detected_brand, detected_model = 'Maruti Suzuki', 'Swift'
            elif category == 'bikes':
                detected_brand, detected_model = 'Royal Enfield', 'Classic 350'
            elif category == 'lorries':
                detected_brand, detected_model = 'Tata Motors', 'Tata 407 Gold'
            else:
                detected_brand, detected_model = 'Bajaj', 'Compact 4S'
    elif not detected_model:
        detected_model = cat_info['brands'][detected_brand][0]

    # 5. Detect Fuel Type
    fuel_type = None
    for f in cat_info['fuel_types']:
        if f.lower() in q:
            fuel_type = f
            break
    if not fuel_type:
        fuel_type = 'Diesel' if category == 'lorries' else ('CNG' if category == 'autos' else 'Petrol')

    # 6. Detect Condition
    condition = 'Good'
    if any(w in q for w in ['excellent', 'mint', 'showroom', 'perfect', 'superb', 'new']):
        condition = 'Excellent'
    elif any(w in q for w in ['fair', 'average', 'okay', 'moderate']):
        condition = 'Fair'
    elif any(w in q for w in ['poor', 'damaged', 'accidental', 'bad']):
        condition = 'Poor'

    # 7. Detect Location
    location = 'Delhi'
    for loc in ['Delhi', 'Mumbai', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad', 'Jaipur', 'Lucknow']:
        if loc.lower() in q:
            location = loc
            break

    # Build category-specific vehicle payload
    vehicle_data = {
        'brand': detected_brand,
        'model': detected_model,
        'year': year,
        'km_driven': km,
        'fuel_type': fuel_type,
        'owners': '1st Owner',
        'condition': condition,
        'location': location
    }

    if category == 'cars':
        vehicle_data['transmission'] = 'Automatic' if 'automatic' in q else 'Manual'
        vehicle_data['engine_cc'] = 1197
    elif category == 'bikes':
        vehicle_data['engine_cc'] = 349 if 'enfield' in detected_brand.lower() else 150
    elif category == 'lorries':
        vehicle_data['load_capacity'] = 6.5
        vehicle_data['vehicle_type'] = 'Medium Commercial Vehicle (MCV)'
    elif category == 'autos':
        vehicle_data['passenger_capacity'] = '3 Seater'

    return category, vehicle_data


def process_voice_query(query_text):
    """
    Main Assistant Pipeline:
    - Direct knowledge answers with ZERO repetitive introductions
    - Real-time ML Prediction triggered by vehicle names, quick chips, or price questions
    """
    if not query_text or not query_text.strip():
        return {
            'text': "I am listening. Ask any vehicle question or say a model like: 'Classic 350' or '2021 Swift with 30,000 km'.",
            'spoken_text': "I am listening. Which vehicle would you like to check?",
            'action': 'info'
        }

    q = query_text.strip()
    q_lower = q.lower()

    # Priority 1: Match Knowledge Base for Direct Questions
    for item in KNOWLEDGE_BASE:
        for pat in item['patterns']:
            if re.search(pat, q_lower):
                return {
                    'text': item['response'],
                    'spoken_text': item['response'],
                    'action': 'info'
                }

    # Priority 2: Check for Vehicle Prediction Intent
    prediction_verbs = [
        'predict', 'estimate', 'valuation', 'calculate', 'how much',
        'worth', 'appraise', 'sell for', 'price', 'value', 'rate', 'cost'
    ]
    has_pred_verb = any(v in q_lower for v in prediction_verbs)

    # Check if query mentions ANY known vehicle model or brand
    has_vehicle_mention = any(m in q_lower for m in KNOWN_VEHICLE_NAMES)
    if not has_vehicle_mention:
        for cat, info in Config.CATEGORIES_INFO.items():
            for b in info['brands']:
                if b.lower() in q_lower:
                    has_vehicle_mention = True
                    break
            if has_vehicle_mention:
                break

    # Check for category words
    has_category_word = any(w in q_lower for w in ['car', 'bike', 'truck', 'lorry', 'auto', 'vehicle'])

    # PREDICTION TRIGGER:
    # 1. Mention of any specific vehicle model (e.g., 'classic 350', 'swift', 'creta', 'tata truck')
    # 2. Prediction verb + vehicle category (e.g., 'estimate car', 'how much for bike')
    # 3. Explicit 'predict' command
    is_prediction = has_vehicle_mention or (has_pred_verb and has_category_word) or ('predict' in q_lower)

    if is_prediction:
        try:
            category, vehicle_data = parse_vehicle_voice_command(q)
            pred_res = predict_price(category, vehicle_data)
            pred_price = pred_res['predicted_price']
            price_min = pred_res['price_min']
            price_max = pred_res['price_max']

            # Check if user provided explicit year and km in the prompt
            has_explicit_year = bool(re.search(r'\b(200[5-9]|201[0-9]|202[0-6])\b', q_lower))
            has_explicit_km = bool(re.search(r'(\d+)\s*(?:k|thousand|km|kms)', q_lower))

            # Persist to SQLite
            db_record = {
                'category': category,
                'brand': vehicle_data['brand'],
                'model': vehicle_data['model'],
                'year': vehicle_data['year'],
                'km_driven': vehicle_data['km_driven'],
                'fuel_type': vehicle_data['fuel_type'],
                'transmission': vehicle_data.get('transmission'),
                'engine_cc': vehicle_data.get('engine_cc'),
                'load_capacity': vehicle_data.get('load_capacity'),
                'vehicle_type': vehicle_data.get('vehicle_type'),
                'passenger_capacity': vehicle_data.get('passenger_capacity'),
                'owners': vehicle_data['owners'],
                'condition': vehicle_data['condition'],
                'location': vehicle_data['location'],
                'predicted_price': pred_price,
                'price_min': price_min,
                'price_max': price_max
            }
            pred_id = save_prediction(db_record)

            inr_str = format_inr(pred_price)
            lakh_str = format_lakhs(pred_price)
            min_lakh = format_lakhs(price_min)
            max_lakh = format_lakhs(price_max)

            # Direct Spoken Speech (ZERO repetitive intros!)
            if has_explicit_year or has_explicit_km:
                speech_text = (
                    f"Your {vehicle_data['year']} {vehicle_data['brand']} {vehicle_data['model']} with "
                    f"{vehicle_data['km_driven']:,} kilometers is estimated at approximately "
                    f"{lakh_str.replace('₹', 'Rupees')}. "
                    f"The fair negotiation range is between {min_lakh.replace('₹', 'Rupees')} and {max_lakh.replace('₹', 'Rupees')}."
                )
            else:
                speech_text = (
                    f"A standard {vehicle_data['year']} {vehicle_data['brand']} {vehicle_data['model']} with "
                    f"{vehicle_data['km_driven']:,} kilometers is estimated at approximately "
                    f"{lakh_str.replace('₹', 'Rupees')}, with a fair range between {min_lakh.replace('₹', 'Rupees')} and {max_lakh.replace('₹', 'Rupees')}. "
                    f"Tell me your exact year or kilometers for a custom valuation."
                )

            # Clean Display Text
            custom_tip = ""
            if not (has_explicit_year and has_explicit_km):
                custom_tip = f"\n\n💡 *Tip: Say your exact year and km (e.g., '2023 {vehicle_data['model']} with 12,000 km') for a personalized quote.*"

            display_text = (
                f"✨ **Valuation Result:**\n\n"
                f"🚗 **Vehicle:** {vehicle_data['year']} {vehicle_data['brand']} {vehicle_data['model']} ({vehicle_data['condition']})\n"
                f"📍 **Specs:** {vehicle_data['location']} &bull; {vehicle_data['km_driven']:,} km &bull; {vehicle_data['fuel_type']}\n\n"
                f"💰 **Estimated Fair Price:** **₹ {inr_str}** (~{lakh_str})\n"
                f"📊 **Fair Negotiation Range:** ₹ {format_inr(price_min)} &ndash; ₹ {format_inr(price_max)}"
                f"{custom_tip}\n\n"
                f"🛡️ *Valuation saved as Record #{pred_id}.*"
            )

            return {
                'text': display_text,
                'spoken_text': speech_text,
                'action': 'prediction',
                'prediction_id': pred_id,
                'category': category,
                'brand': vehicle_data['brand'],
                'model': vehicle_data['model'],
                'year': vehicle_data['year'],
                'km_driven': vehicle_data['km_driven'],
                'price': pred_price,
                'price_formatted': inr_str,
                'price_lakhs': lakh_str,
                'price_min': format_inr(price_min),
                'price_max': format_inr(price_max),
                'result_url': f"/result/{pred_id}",
                'report_url': f"/report/{pred_id}"
            }
        except Exception as e:
            return {
                'text': f"Could not calculate valuation: {str(e)}. Please specify the vehicle year, brand, and kilometers.",
                'spoken_text': "Please specify the vehicle year, model name, and kilometers driven.",
                'action': 'error'
            }

    # Priority 3: Context-Aware Dynamic Fallback (NO repetitive identity intros!)
    if any(w in q_lower for w in ['price', 'cost', 'worth', 'value', 'rate']):
        resp = "Resale price depends mainly on manufacturing year, total kilometers driven, and physical condition. Tell me the vehicle model and year to calculate the exact price."
    elif any(w in q_lower for w in ['buy', 'buying', 'purchase']):
        resp = "When buying a used vehicle, verify the service history bills, check tyre manufacturing date codes, and test drive on open roads. Which model are you planning to buy?"
    elif any(w in q_lower for w in ['sell', 'selling', 'sold']):
        resp = "To get the highest selling price, keep all service invoices ready, clean the vehicle thoroughly, and sell before 50,000 km. Which vehicle are you planning to sell?"
    elif any(w in q_lower for w in ['under', 'budget', 'cheap', 'lakh', 'lakhs']):
        resp = "For cars under 5 Lakhs, consider a used Swift, Grand i10, or Baleno. For bikes under 1 Lakh, Classic 350, Pulsar 150, or Activa offer the best resale value."
    else:
        resp = "I am ready to help! You can ask for a valuation of any vehicle (like Classic 350, Swift, Creta, or Tata Truck), or ask about documentation, depreciation, and buying advice."

    return {
        'text': resp,
        'spoken_text': resp,
        'action': 'info'
    }
