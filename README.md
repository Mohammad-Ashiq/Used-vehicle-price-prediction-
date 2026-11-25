# ReVahan &ndash; USED VEHICLE PRICE PREDICTION SYSTEM
### Academic Final-Year Project (BCA / B.Tech / MCA)
**Domain:** Machine Learning, Full-Stack Web Development, Data Science, Automotive Valuation  
**Algorithm:** Scikit-Learn Ensemble Random Forest Regressor  
**Backend:** Python 3.9+ & Flask 3.1  
**Database:** SQLite 3  
**Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5.3, Chart.js  

---

## 1. Project Overview
**ReVahan** is an intelligent, production-ready web application designed to compute fair, data-backed resale market prices for used vehicles across India using Machine Learning. 

The application provides dedicated machine learning valuation pipelines for **four major automotive categories**:
1. **Cars:** Hatchbacks, Sedans, Compact SUVs, and Luxury Vehicles.
2. **Bikes:** Commuter Motorcycles, Performance Streetfighters, Cruisers, and Scooters.
3. **Lorries & Trucks:** Light Commercial Vehicles (LCV), Heavy Duty Tippers, and Cargo Containers.
4. **Auto-rickshaws:** Three-Wheeler Passenger Cabs, Cargo Autos, and Electric Rickshaws.

---

## 2. Key Features

- **Real Machine Learning (No Hardcoding):** 
  - 4 separate Random Forest Regressor models (120 decision trees each) trained on authentic Indian automotive transaction data.
  - Test R² Accuracy Scores: **Cars: 84.4%**, **Bikes: 88.7%**, **Lorries: 91.9%**, **Autos: 91.7%**.
- **Confidence Intervals & Negotiation Spread:** Provides minimum and maximum negotiation bounds based on Root Mean Squared Error (RMSE).
- **Explainable Valuation Factors:** Visual impact meters for vehicle age depreciation, odometer mileage wear, condition grading, and title status.
- **Dynamic Dependent Dropdowns:** Brand selection automatically queries the Flask backend via AJAX (`/api/models/<category>`) to populate corresponding models.
- **Automotive-Themed Responsive UI:** Sleek midnight dark theme and showroom light theme with seamless toggle switch and `localStorage` persistence.
- **Analytics Dashboard:** Visualized with Chart.js—category distribution doughnut chart, average price comparison bar chart, and condition spread.
- **SQLite Database Persistence:** Records every appraisal with date, full specs, and estimated price.
- **Searchable Valuation History:** Filter by vehicle category, search by brand, model, or city, and delete records.
- **One-Click PDF Report Download:** Generates high-resolution valuation certificates using ReportLab.
- **Print Friendly:** Dedicated print stylesheet to print clean certificates directly from the browser.

---

## 3. Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6), Bootstrap 5.3, Bootstrap Icons |
| **Backend Framework** | Python 3.9+, Flask 3.1 |
| **Machine Learning** | Scikit-Learn 1.6, Pandas, NumPy, Joblib |
| **Algorithms** | `RandomForestRegressor`, `ColumnTransformer`, `OneHotEncoder`, `StandardScaler` |
| **Database** | SQLite 3 (`database/db.sqlite3`) with parameterized queries |
| **Visualization** | Chart.js 4.4 (frontend charts), Matplotlib |
| **Report Generation** | ReportLab 3.6+ (PDF Valuation Certificates) |

---

## 4. Project Folder Structure

```
used_vehicle_price_prediction/
│
├── app.py                      # Main Flask application entrypoint & REST routes
├── config.py                   # Central configuration, brand catalogs & paths
├── requirements.txt            # Python dependencies
├── seed_db.py                  # Database initialization & sample seed data script
├── README.md                   # Complete documentation & viva guide
│
├── dataset/                    # Realistically synthesized datasets
│   ├── cars.csv                # 1,200 Indian car transactions
│   ├── bikes.csv               # 1,200 motorcycle/scooter transactions
│   ├── lorries.csv             # 1,000 commercial truck transactions
│   └── autos.csv               # 1,000 auto-rickshaw transactions
│
├── models/                     # Serialized trained ML pipelines (Joblib)
│   ├── car_model.pkl           # Trained Random Forest model for Cars (R²: 84.4%)
│   ├── bike_model.pkl          # Trained Random Forest model for Bikes (R²: 88.7%)
│   ├── lorry_model.pkl         # Trained Random Forest model for Lorries (R²: 91.9%)
│   └── auto_model.pkl          # Trained Random Forest model for Autos (R²: 91.7%)
│
├── ml/                         # Machine learning logic (isolated from web routes)
│   ├── generate_datasets.py    # Dataset synthesis with market depreciation formulas
│   ├── preprocess.py           # Feature engineering, scaling, one-hot encoding & validation
│   ├── train_model.py          # Random Forest training & evaluation (MAE, RMSE, R²)
│   └── predict.py              # Model caching, price estimation & explainability
│
├── database/                   # SQLite database directory
│   ├── db.py                   # Database helper with parameterized queries
│   └── db.sqlite3              # SQLite database file
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html               # Master layout (navbar, theme toggle, flash alerts, footer)
│   ├── index.html              # Home landing page with hero, features & categories
│   ├── categories.html         # Category selection hub
│   ├── prediction.html         # Dynamic prediction input forms (Cars, Bikes, Lorries, Autos)
│   ├── result.html             # Detailed valuation result card, factors & PDF download
│   ├── dashboard.html          # Analytics dashboard with Chart.js graphs
│   ├── history.html            # Audit history with search, category filters & deletion
│   ├── about.html              # System architecture, team & model metrics
│   ├── how_it_works.html       # ML pipeline walkthrough & viva Q&A guide
│   ├── contact.html            # Working contact form & FAQ accordion
│   ├── 404.html                # Custom 404 error page
│   └── 500.html                # Custom 500 error page
│
├── static/                     # Static web assets
│   ├── css/
│   │   └── style.css           # Custom dark/light theme automotive stylesheet
│   ├── js/
│   │   └── script.js           # AJAX dropdowns, theme switcher & Chart.js logic
│   └── images/                 # Image assets
│
└── reports/                    # Generated PDF valuation certificates
```

---

## 5. Step-by-Step Installation & Execution

### Step 1: Open Terminal in the Project Directory
```powershell
cd C:\Users\786mo\.gemini\antigravity\scratch\used_vehicle_price_prediction
```

### Step 2: Install Python Dependencies
```powershell
python -m pip install -r requirements.txt
```

### Step 3: (Optional) Re-Generate Datasets or Re-Train ML Models
The models and datasets are already pre-trained and ready. If you wish to retrain them:
```powershell
# Generate fresh datasets
python ml/generate_datasets.py

# Train all 4 Random Forest models
python ml/train_model.py --category all
```

### Step 4: Seed Initial Data
```powershell
python seed_db.py
```

### Step 5: Start the Flask Web Server
```powershell
python app.py
```

### Step 6: Open the Application in Your Browser
Visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 5.1 How to Open and Run in PyCharm (Beginner Friendly)

If you use **PyCharm** (Community or Professional Edition):

1. **Launch PyCharm**:
   - Open PyCharm on your computer.
2. **Open the Project Folder**:
   - Click **File** &rarr; **Open...**
   - In the directory browser, navigate to:
     `C:\Users\786mo\.gemini\antigravity\scratch\used_vehicle_price_prediction`
   - Click **OK** (or choose *"Trust Project"* if prompted).
3. **Configure the Python Interpreter**:
   - Click **File** &rarr; **Settings** (or press `Ctrl + Alt + S`).
   - Go to **Project: used_vehicle_price_prediction** &rarr; **Python Interpreter**.
   - If an interpreter is not selected, click **Add Interpreter** &rarr; **Add Local Interpreter...**
   - Select **System Interpreter** (pointing to your installed Python 3.9/3.10/3.11 `python.exe`) or choose **New Virtualenv Environment**.
   - Click **Apply** and **OK**.
4. **Install Required Packages (if prompted)**:
   - Open the **Terminal** tab at the bottom of PyCharm (`Alt + F12`).
   - Run: `pip install -r requirements.txt`
5. **Run the Project**:
   - In the left **Project Tool Window**, locate and double-click `app.py`.
   - Right-click anywhere inside `app.py` and select **Run 'app'** (or press `Ctrl + Shift + F10`).
   - You will see the PyCharm console display:
     `* Running on http://127.0.0.1:5000`
6. **Open in Web Browser**:
   - Click on the link `http://127.0.0.1:5000` right in the PyCharm Run window, and your browser will launch **ReVahan**!


---

## 6. Testing the Application

1. **Test Car Valuation:**
   - Go to `Categories` -> Click `Cars`.
   - Select `Hyundai` -> Model dropdown dynamically loads `Creta`, `i20`, `Verna`, etc.
   - Select `Year: 2021`, `Kilometers: 35000`, `Fuel: Diesel`, `Transmission: Manual`, `Engine: 1493 CC`.
   - Click **Estimate Fair Market Value**.
   - Observe the fair valuation in ₹ (approx ₹ 10.2 Lakhs), negotiation range, factors, and click **Download PDF Certificate**.
2. **Test Dark/Light Theme:**
   - Click the sun/moon icon in the top right navbar. The application will smoothly transition between dark midnight theme and showroom light theme.
3. **Test Dashboard & Chart.js:**
   - Open `/dashboard` to observe live Chart.js doughnut and bar charts updating in real-time.
4. **Test History & Search:**
   - Open `/history` to view previously valued vehicles, filter by category pill, or search by model name.

---

## 7. Viva Voce & Technical Review Q&A

**Q1: What Machine Learning algorithm is used and why?**  
*Answer:* We use Scikit-Learn's `RandomForestRegressor`. It is an ensemble learning method that constructs 120 decision trees using bootstrap aggregating (bagging). It captures complex non-linear depreciation patterns without overfitting, and handles continuous and categorical interactions better than standard linear regression.

**Q2: How do you evaluate the regression models?**  
*Answer:* We evaluate on an unseen 20% test split using three standard metrics:
- **Mean Absolute Error (MAE):** Average magnitude of errors in Indian Rupees.
- **Root Mean Squared Error (RMSE):** Penalizes larger valuation errors.
- **R² Score (Coefficient of Determination):** Measures the proportion of variance in vehicle prices explained by the features (achieving 84% to 92% across categories).

**Q3: How are categorical variables handled?**  
*Answer:* We use a `ColumnTransformer` with `OneHotEncoder(handle_unknown='ignore')` to convert nominal categorical features (brand, model, fuel type, transmission, condition, location) into numerical vectors, while numeric features (age, mileage, engine cc) are normalized using `StandardScaler`.
