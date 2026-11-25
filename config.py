import os
from datetime import datetime

# Base Directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'used-vehicle-prediction-secret-key-2026')
    DEBUG = True
    
    # Database Configuration
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'db.sqlite3')
    
    # Dataset Paths
    DATASET_DIR = os.path.join(BASE_DIR, 'dataset')
    DATASETS = {
        'cars': os.path.join(DATASET_DIR, 'cars.csv'),
        'bikes': os.path.join(DATASET_DIR, 'bikes.csv'),
        'lorries': os.path.join(DATASET_DIR, 'lorries.csv'),
        'autos': os.path.join(DATASET_DIR, 'autos.csv')
    }
    
    # Model Paths
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    MODELS = {
        'cars': os.path.join(MODELS_DIR, 'car_model.pkl'),
        'bikes': os.path.join(MODELS_DIR, 'bike_model.pkl'),
        'lorries': os.path.join(MODELS_DIR, 'lorry_model.pkl'),
        'autos': os.path.join(MODELS_DIR, 'auto_model.pkl')
    }
    
    # Reports Directory
    REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
    
    # Current Reference Year
    CURRENT_YEAR = datetime.now().year
    
    # Comprehensive Multi-Vehicle Catalog (Top 70+ Indian Automotive Brands & 400+ Models)
    CATEGORIES_INFO = {
        'cars': {
            'title': 'Car Price Prediction',
            'icon': 'bi-car-front-fill',
            'singular': 'Car',
            'description': 'Predict fair resale valuation for hatchbacks, sedans, compact SUVs, and luxury cars.',
            'brands': {
                'Maruti Suzuki': ['Swift', 'Baleno', 'Dzire', 'Brezza', 'Ertiga', 'Wagon R', 'Alto 800', 'Alto K10', 'Celerio', 'Ignis', 'XL6', 'Fronx', 'Jimny', 'Grand Vitara', 'Invicto', 'S-Presso', 'Ciaz'],
                'Hyundai': ['Creta', 'Venue', 'i20', 'Verna', 'Grand i10 Nios', 'Alcazar', 'Tucson', 'Exter', 'Aura', 'Kona Electric', 'Ioniq 5', 'Santro'],
                'Tata Motors': ['Nexon', 'Punch', 'Altroz', 'Harrier', 'Safari', 'Tiago', 'Tigor', 'Curvv', 'Nexon EV', 'Punch EV', 'Tiago EV', 'Hexa'],
                'Mahindra': ['Thar', 'Scorpio-N', 'Scorpio Classic', 'XUV700', 'XUV300', 'XUV 3XO', 'Bolero', 'Bolero Neo', 'Thar Roxx', 'Marazzo', 'XUV400 EV'],
                'Toyota': ['Innova Crysta', 'Innova Hycross', 'Fortuner', 'Urban Cruiser Hyryder', 'Glanza', 'Rumion', 'Hilux', 'Camry', 'Vellfire'],
                'Kia': ['Seltos', 'Sonet', 'Carens', 'EV6', 'Carnival'],
                'Honda': ['City', 'Amaze', 'Elevate', 'WR-V', 'Jazz', 'Civic', 'CR-V', 'Brio'],
                'Volkswagen': ['Virtus', 'Taigun', 'Polo', 'Vento', 'Tiguan', 'Jetta', 'Passat'],
                'Skoda': ['Slavia', 'Kushaq', 'Kodiaq', 'Octavia', 'Superb', 'Rapid'],
                'MG (Morris Garages)': ['Hector', 'Hector Plus', 'Astor', 'ZS EV', 'Comet EV', 'Gloster'],
                'Renault': ['Kwid', 'Triber', 'Kiger', 'Duster', 'Lodgy'],
                'Nissan': ['Magnite', 'Kicks', 'Micra', 'Sunny', 'Terrano'],
                'Ford': ['EcoSport', 'Endeavour', 'Figo', 'Aspire', 'Freestyle'],
                'Jeep': ['Compass', 'Meridian', 'Wrangler', 'Grand Cherokee'],
                'BMW': ['3 Series', '5 Series', '7 Series', 'X1', 'X3', 'X5', 'X7', '2 Series Gran Coupe', 'M340i'],
                'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLA', 'GLB', 'GLC', 'GLE', 'GLS', 'A-Class Limousine'],
                'Audi': ['A4', 'A6', 'Q3', 'Q5', 'Q7', 'Q8', 'A8L', 'e-tron'],
                'Volvo': ['XC40', 'XC60', 'XC90', 'S90', 'EX40', 'C40 Recharge'],
                'Land Rover': ['Range Rover Evoque', 'Range Rover Velar', 'Range Rover Sport', 'Defender', 'Discovery Sport'],
                'Jaguar': ['F-Pace', 'XE', 'XF', 'XJ', 'I-Pace'],
                'Porsche': ['Macan', 'Cayenne', '911', 'Panamera', 'Taycan'],
                'BYD': ['Atto 3', 'Seal', 'eMAX 7', 'e6'],
                'Citroen': ['C3', 'C3 Aircross', 'Basalt', 'C5 Aircross', 'eC3'],
                'Force Motors': ['Gurkha', 'Trax Cruiser', 'Urbania'],
                'Lexus': ['ES 300h', 'NX 350h', 'RX 350h', 'LX 500d'],
                'Mini': ['Cooper 3-Door', 'Countryman', 'Cooper SE'],
                'Isuzu': ['D-Max V-Cross', 'MU-X', 'Hi-Lander']
            },
            'fuel_types': ['Petrol', 'Diesel', 'CNG', 'Electric', 'Hybrid'],
            'transmissions': ['Manual', 'Automatic'],
            'conditions': ['Excellent', 'Good', 'Fair', 'Poor'],
            'owners': ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner & Above']
        },
        'bikes': {
            'title': 'Bike Price Prediction',
            'icon': 'bi-bicycle',
            'singular': 'Bike',
            'description': 'Calculate second-hand values for commuter bikes, sports bikes, cruisers, and electric scooters.',
            'brands': {
                'Hero MotoCorp': ['Splendor Plus', 'HF Deluxe', 'Glamour', 'Passion Plus', 'Xpulse 200 4V', 'Super Splendor', 'Xtreme 160R', 'Xtreme 125R', 'Destini 125', 'Pleasure Plus', 'Mavrick 440', 'Karizma XMR'],
                'Honda': ['Activa 6G', 'Activa 125', 'Shine 100', 'Shine 125', 'SP 125', 'Unicorn', 'Dio 110', 'Dio 125', 'Hornet 2.0', 'CB350 Hness', 'CB350RS', 'CB200X', 'CB300R'],
                'Bajaj': ['Pulsar 150', 'Pulsar NS200', 'Pulsar N160', 'Pulsar RS200', 'Pulsar 125', 'Pulsar N250', 'Platina 100', 'Platina 110', 'CT 110X', 'Dominar 400', 'Dominar 250', 'Avenger Cruise 220', 'Avenger Street 160', 'Chetak EV'],
                'TVS': ['Jupiter 110', 'Jupiter 125', 'Apache RTR 160 4V', 'Apache RTR 200 4V', 'Apache RR 310', 'Raider 125', 'Ntorq 125', 'Sport', 'Radeon', 'Star City Plus', 'Ronin', 'XL100', 'iQube EV'],
                'Royal Enfield': ['Classic 350', 'Hunter 350', 'Bullet 350', 'Meteor 350', 'Himalayan 450', 'Guerrilla 450', 'Interceptor 650', 'Continental GT 650', 'Super Meteor 650', 'Shotgun 650'],
                'Yamaha': ['FZ-S FI', 'FZ-X', 'MT-15 V2', 'R15 V4', 'R15M', 'RayZR 125 Fi', 'Aerox 155', 'Fascino 125', 'FZ 25'],
                'Suzuki': ['Access 125', 'Burgman Street', 'Avenis', 'Gixxer 150', 'Gixxer SF', 'Gixxer 250', 'Gixxer SF 250', 'V-Strom SX 250'],
                'KTM': ['200 Duke', '250 Duke', '390 Duke', 'RC 200', 'RC 390', '250 Adventure', '390 Adventure', '125 Duke'],
                'Kawasaki': ['Ninja 300', 'Ninja 400', 'Ninja 650', 'Z650', 'Z900', 'Versys 650', 'Eliminator 500'],
                'Harley-Davidson': ['X440', 'Iron 883', 'Fat Boy', 'Nightster', 'Street 750'],
                'Triumph': ['Speed 400', 'Scrambler 400 X', 'Street Triple', 'Tiger 900', 'Bonneville T100', 'Trident 660'],
                'Jawa': ['Jawa 350', 'Jawa 42', '42 Bobber', 'Jawa Perak'],
                'Yezdi': ['Roadster', 'Scrambler', 'Adventure'],
                'Ducati': ['Monster', 'Scrambler Icon', 'Panigale V2', 'Multistrada V4'],
                'BMW Motorrad': ['G 310 R', 'G 310 GS', 'G 310 RR', 'S 1000 RR', 'F 900 XR'],
                'Benelli': ['Imperiale 400', 'TRK 502', 'TRK 502X', 'Leoncino 500', '502C'],
                'Aprilia': ['RS 457', 'SR 125', 'SR 160', 'SXR 160', 'Tuono 660'],
                'Vespa': ['VXL 125', 'SXL 125', 'VXL 150', 'SXL 150', 'ZX 125'],
                'Ather Energy': ['450X Gen 3', '450S', '450 Apex', 'Rizta'],
                'Ola Electric': ['S1 Pro Gen 2', 'S1 Air', 'S1 X 3kWh', 'S1 X Plus'],
                'Revolt Motors': ['RV400', 'RV400 BRZ', 'RV1'],
                'Ultraviolette': ['F77 Mach 2', 'F77 Recon'],
                'Husqvarna': ['Svartpilen 250', 'Vitpilen 250', 'Svartpilen 401'],
                'Simple Energy': ['Simple One', 'Simple Dot One'],
                'Tork Motors': ['Kratos R', 'Kratos Urban']
            },
            'fuel_types': ['Petrol', 'Electric'],
            'conditions': ['Excellent', 'Good', 'Fair', 'Poor'],
            'owners': ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner & Above']
        },
        'lorries': {
            'title': 'Lorry & Truck Price Prediction',
            'icon': 'bi-truck-flatbed',
            'singular': 'Lorry',
            'description': 'Estimate commercial resale market value for LCVs, MCVs, HCVs, tippers, and haulage trucks.',
            'brands': {
                'Tata Motors': ['Tata Ace Gold', 'Tata 407 Gold', 'Tata LPT 1613', 'Tata Signa 4825.TK', 'Tata Signa 2823', 'Tata Prima 2830.K', 'Tata Intra V30', 'Tata Intra V50', 'Tata Ultra T.7', 'Tata Yodha Pickup'],
                'Ashok Leyland': ['Dost Strong', 'Bada Dost i4', 'Ecomet 1215 HE', 'Bada Dost i3', 'Captain 2825', 'AVTR 3120', 'Partner 6 Tyre', 'Partner 4 Tyre', 'Boss 1215 HB', '4220 Tipper'],
                'Eicher': ['Pro 2049', 'Pro 3019', 'Pro 6028', 'Pro 8035XM', 'Pro 2110XP', 'Pro 2095XP', 'Pro 2059', 'Pro 3015'],
                'BharatBenz': ['1217C', '1617R', '1917R', '2823R', '3528R', '4028T', '5528T', '2823C Tipper'],
                'Mahindra Commercial': ['Bolero Maxi Truck Plus', 'Bolero Camper', 'Furio 14', 'Furio 7', 'Blazo X 28', 'Blazo X 35', 'Loadking Optimo', 'Supro Profit Truck Maxi'],
                'Force Motors': ['Traveller 3050', 'Traveller 4020', 'Trax Delivery Van', 'Kargo King', 'Shaktiman 400'],
                'SML Isuzu': ['Sartaj GS', 'Sartaj HG72', 'Samrat GS', 'Prestige GS', 'Supreme GS', 'Super Giga'],
                'Volvo Trucks': ['FM 420 8x4 Tipper', 'FMX 460', 'FMX 500', 'FH 520 Puller'],
                'Scania': ['G410 Mining Tipper', 'P410 8x4 Tipper', 'R500 Heavy Puller'],
                'Piaggio Commercial': ['Porter 700', 'Ape Xtra LDX Plus'],
                'Maruti Suzuki Commercial': ['Super Carry Petrol', 'Super Carry CNG'],
                'KAMAZ': ['Kamaz 6520 Tipper', 'Kamaz 6540 8x4']
            },
            'vehicle_types': ['Light Commercial Vehicle (LCV)', 'Medium Commercial Vehicle (MCV)', 'Heavy Commercial Vehicle (HCV)', 'Tipper', 'Container Cargo'],
            'fuel_types': ['Diesel', 'CNG', 'Electric'],
            'conditions': ['Excellent', 'Good', 'Fair', 'Poor'],
            'owners': ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner & Above']
        },
        'autos': {
            'title': 'Auto-Rickshaw Price Prediction',
            'icon': 'bi-taxi-front-fill',
            'singular': 'Auto-rickshaw',
            'description': 'Predict realistic resale prices for 3-wheeler passenger and delivery autos.',
            'brands': {
                'Bajaj Auto': ['Compact 4S RE', 'Maxima Z Passenger', 'RE E-TEC 9.0 Electric', 'Maxima C Cargo', 'RE Optima Diesel', 'Maxima X Wide'],
                'Piaggio': ['Ape City Plus', 'Ape Auto DX', 'Ape E-City FX Electric', 'Ape Xtra LDX Cargo', 'Ape Auto Plus', 'Ape E-Xtra FX'],
                'Mahindra 3-Wheeler': ['Treo Electric Auto', 'Alfa DX Passenger', 'e-Alfa Mini', 'Alfa Plus Cargo', 'Zor Grand Electric Cargo', 'Treo Zor'],
                'TVS': ['King Deluxe 4S', 'King Duramax Petrol', 'King Duramax CNG', 'King Kargo CNG', 'King EV'],
                'Atul Auto': ['Atul Gem Paxx', 'Atul Elite Passenger', 'Atul Rik CNG', 'Atul Gemini', 'Atul Shakti Cargo'],
                'Saarthi': ['Saarthi Shavitri', 'Saarthi Star', 'Saarthi E-Rickshaw DLX'],
                'Kinetic Green': ['Kinetic Safar Smart', 'Kinetic Safar Jumbo Electric', 'Kinetic Super DX'],
                'Euler Motors': ['HiLoad EV 2024', 'HiLoad EV Cargo'],
                'Montra Electric': ['Montra Super Auto', 'Montra Super Auto e-Rickshaw'],
                'Terra Motors': ['Y4A Electric Rickshaw', 'Kiwami E-Auto'],
                'Lohia Auto': ['Narain DX', 'Narain Plus', 'Comfort FPlus'],
                'Baxy Mobility': ['Baxy Express G', 'Baxy Super King', 'Baxy M-Van']
            },
            'passenger_capacities': ['3 Seater', '4 Seater', '6 Seater'],
            'fuel_types': ['CNG', 'LPG', 'Petrol', 'Diesel', 'Electric'],
            'conditions': ['Excellent', 'Good', 'Fair', 'Poor'],
            'owners': ['1st Owner', '2nd Owner', '3rd Owner', '4th Owner & Above']
        }
    }

    # All 28 States and 8 Union Territories of India (100% Pan-India Coverage)
    LOCATIONS = [
        # 28 States
        'Andhra Pradesh',
        'Arunachal Pradesh',
        'Assam',
        'Bihar',
        'Chhattisgarh',
        'Goa',
        'Gujarat',
        'Haryana',
        'Himachal Pradesh',
        'Jharkhand',
        'Karnataka',
        'Kerala',
        'Madhya Pradesh',
        'Maharashtra',
        'Manipur',
        'Meghalaya',
        'Mizoram',
        'Nagaland',
        'Odisha',
        'Punjab',
        'Rajasthan',
        'Sikkim',
        'Tamil Nadu',
        'Telangana',
        'Tripura',
        'Uttar Pradesh',
        'Uttarakhand',
        'West Bengal',
        # 8 Union Territories
        'Andaman and Nicobar Islands',
        'Chandigarh',
        'Dadra and Nagar Haveli and Daman and Diu',
        'Delhi NCR',
        'Jammu and Kashmir',
        'Ladakh',
        'Lakshadweep',
        'Puducherry'
    ]
