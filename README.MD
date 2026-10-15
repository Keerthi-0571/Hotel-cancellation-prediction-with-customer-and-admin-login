# Hotel Cancellation Prediction

## Quick start (Windows)

Extract the zip, double-click **run.bat**, and the login page opens in your browser.
(Details in `START_HERE.txt`.)

## Login system

| Page | Who | Purpose |
|------|-----|---------|
| `frontend/register.html` | customer | create an account |
| `frontend/login.html` | customer | customer login |
| `frontend/index.html` | customer | enter booking details, predict cancellation risk |
| `frontend/dashboard.html` | customer | "My History" - only their own predictions |
| `frontend/admin_login.html` | admin | separate admin login |
| `frontend/admin_dashboard.html` | admin | every customer's history: name, email, booking details, prediction, probability, risk level, date/time |

**Admin account** (created automatically on first start): `admin@hotel.com` / `Admin@123`.
Change it before real use by setting environment variables before starting the backend (PowerShell):

    $env:ADMIN_EMAIL="you@yourhotel.com"
    $env:ADMIN_PASSWORD="a-long-password"

The admin account is created only once. To reset it, delete `backend/hotel_app.db`
(this also deletes all users and history) and start again.

Data is stored in `backend/hotel_app.db` (SQLite: `users` and `predictions` tables).
Nobody can register as admin from the website; customers can never see other customers' data.

---

🏨 Hotel Booking Cancellation Prediction

## 📌 Project Overview

Hotel Booking Cancellation Prediction is a Machine Learning-based web application that predicts whether a hotel booking is likely to be cancelled or not.

The system uses historical hotel booking data to identify booking patterns and generate a cancellation prediction along with the cancellation probability and risk level.

The project combines Machine Learning, Python Flask, and a web-based frontend to provide an easy-to-use prediction system.

---

## 🎯 Objectives

- Predict hotel booking cancellations using Machine Learning.
- Analyze important hotel booking attributes.
- Provide cancellation probability for each booking.
- Classify the cancellation risk as Low, Medium, or High.
- Provide a simple and user-friendly web interface.
- Maintain prediction history through a dashboard.
- Visualize prediction statistics using charts.

---

## 🚀 Features

- Hotel booking cancellation prediction
- Cancellation probability calculation
- Risk-level classification
- Simple booking input form
- Flask REST API backend
- Interactive dashboard
- Prediction history
- Statistical summaries
- Data visualization
- Machine Learning model integration

---

## 🏗️ System Architecture

```text
                 USER
                   |
                   v
          WEB FRONTEND
       HTML + CSS + JavaScript
                   |
                   v
              FLASK API
                   |
                   v
         DATA PREPROCESSING
                   |
                   v
          TRAINED ML MODEL
                   |
                   v
        +----------------------+
        | Prediction           |
        | Probability          |
        | Risk Level            |
        +----------------------+
                   |
                   v
             DASHBOARD
          /      |       \
     Statistics Charts  History
🔄 Project Workflow
Hotel Booking Dataset
          ↓
Data Cleaning
          ↓
Data Preprocessing
          ↓
Feature Transformation
          ↓
Model Training
          ↓
Model Evaluation
          ↓
Save Trained Model
          ↓
Flask API
          ↓
User Booking Input
          ↓
Prediction
          ↓
Probability + Risk Level
          ↓
Dashboard
🤖 Machine Learning

The project uses supervised machine learning for binary classification.

Prediction Classes
0 – Not Cancelled
1 – Cancelled
Input Features

The system uses hotel booking information such as:

Hotel type
Lead time
Arrival month
Number of adults
Number of children
Weekend nights
Week nights
Market segment
Deposit type
Customer and booking-related attributes
💻 Technologies Used
Programming Language
Python
Machine Learning & Data Processing
Pandas
Scikit-learn
Joblib
Backend
Flask
Flask-CORS
Frontend
HTML5
CSS3
JavaScript
Bootstrap
Visualization
Chart.js
Development Tools
Visual Studio Code
Git
GitHub
📂 Project Structure
Hotel-Cancellation-Prediction/
│
├── backend/
│   └── app.py
│
├── dataset/
│   ├── hotel_bookings.csv
│   └── hotel_bookings_cleaned.csv
│
├── evaluation/
│   ├── cancellation_probability.png
│   ├── confusion_matrix.png
│   ├── feature_importance.csv
│   ├── feature_importance.png
│   ├── model_comparison.csv
│   └── model_comparison.png
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   ├── dashboard.js
│   │   └── script.js
│   ├── dashboard.html
│   └── index.html
│
├── models/
│   ├── hotel_cancellation_model.pkl
│   └── preprocessor.pkl
│
├── notebooks/
│   ├── 01_data_analysis.py
│   ├── 02_data_cleaning.py
│   ├── 03_preprocessing.py
│   ├── 04_model_training.py
│   └── 05_model_evaluation.py
│
├── .gitignore
└── README.md
⚙️ Installation
1. Clone the repository
git clone https://github.com/Keerthi-0571/Hotel-Cancellation-Prediction.git
2. Open the project
cd Hotel-Cancellation-Prediction
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment
Windows
venv\Scripts\activate
5. Install required packages
pip install flask flask-cors pandas scikit-learn joblib
▶️ Running the Project
Start the Flask Backend
python backend/app.py

The backend runs on:

http://127.0.0.1:5000
Start the Frontend

Open another terminal and run:

python -m http.server 5500

Then open:

http://127.0.0.1:5500/frontend/index.html
🔌 API Endpoints
Health Check
GET /health

Example response:

{
    "status": "healthy",
    "model": "loaded"
}
Prediction
POST /predict

The endpoint receives booking information and returns:

Prediction
Cancellation Probability
Risk Level
📊 Output

The system provides:

Prediction: Cancelled / Not Cancelled
Cancellation probability
Risk level:
Low
Medium
High

The dashboard also displays prediction statistics and historical predictions.

🖥️ Application Screens
Prediction Interface

Users enter hotel booking details and request a cancellation prediction.

Prediction Result

The application displays the predicted cancellation status, probability, and risk level.

Dashboard

The dashboard provides:

Total predictions
Cancelled bookings
Not cancelled bookings
Cancellation rate
Risk statistics
Prediction history
Charts
📈 Advantages
Easy to use
Automated prediction
Provides probability and risk level
Web-based interface
Useful visualization dashboard
No special hardware required
Can be extended for real-world hotel applications
🔮 Future Enhancements
Deploy the application on a cloud platform.
Improve model performance using additional feature engineering.
Compare additional machine learning algorithms.
Integrate with real hotel reservation systems.
Add automated alerts for high-risk bookings.
Add real-time hotel analytics.
Improve dashboard functionality.
📚 References
Hotel Booking Demand Dataset – Kaggle
Scikit-learn Documentation
Pandas Documentation
Flask Documentation
Bootstrap Documentation
Chart.js Documentation
👩‍💻 Author

K S KEERTHI

Department of Artificial Intelligence & Data Science

📄 License

This project is developed for academic and educational purposes.


### Now create it in your project

From:

```powershell
E:\Hotel_Cancellation_Prediction

run: