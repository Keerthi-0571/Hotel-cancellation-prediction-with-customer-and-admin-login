"""
Hotel Cancellation Prediction API
=================================

Adds to the original prediction API:
  * Customer registration + login
  * Separate admin login
  * Per-customer prediction history (customers only ever see their own)
  * Admin history of ALL customers (name, email, booking details,
    prediction, probability, risk level, date/time)

Storage : SQLite file  backend/hotel_app.db   (created automatically)
Auth    : signed bearer tokens (Authorization: Bearer <token>)
"""

import os
import re
import sqlite3
import secrets
import traceback
from datetime import datetime, timezone
from functools import wraps

import joblib
import pandas as pd
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import generate_password_hash, check_password_hash


# ==========================================================
# APP + PATHS
# ==========================================================

app = Flask(__name__)
CORS(app)  # frontend runs on a different port (5500)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "models", "hotel_cancellation_model.pkl"))
PREPROCESSOR_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "models", "preprocessor.pkl"))

DB_PATH = os.environ.get("HOTEL_DB_PATH", os.path.join(BASE_DIR, "hotel_app.db"))
SECRET_FILE = os.path.join(BASE_DIR, ".secret_key")

TOKEN_MAX_AGE = 8 * 60 * 60  # login stays valid for 8 hours


# ==========================================================
# SECRET KEY  (persisted so logins survive Flask auto-reload)
# ==========================================================

def load_secret_key():
    env_key = os.environ.get("SECRET_KEY")
    if env_key:
        return env_key
    if os.path.exists(SECRET_FILE):
        with open(SECRET_FILE, "r") as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(SECRET_FILE, "w") as f:
        f.write(key)
    return key


SECRET_KEY = load_secret_key()
serializer = URLSafeTimedSerializer(SECRET_KEY, salt="hotel-auth")


# ==========================================================
# LOAD MODEL + PREPROCESSOR  (unchanged behaviour)
# ==========================================================

model = None
preprocessor = None
model_load_error = None
preprocessor_load_error = None

print("\n" + "=" * 70)
print("HOTEL CANCELLATION PREDICTION API")
print("=" * 70)

if not os.path.exists(MODEL_PATH):
    model_load_error = "Model file not found: " + MODEL_PATH
    print("MODEL STATUS       : FAILED -", model_load_error)
else:
    try:
        model = joblib.load(MODEL_PATH)
        print("MODEL STATUS       : READY (" + type(model).__name__ + ")")
    except Exception as e:
        model_load_error = str(e)
        print("MODEL STATUS       : FAILED -", model_load_error)
        traceback.print_exc()

if not os.path.exists(PREPROCESSOR_PATH):
    preprocessor_load_error = "Preprocessor file not found: " + PREPROCESSOR_PATH
    print("PREPROCESSOR STATUS: FAILED -", preprocessor_load_error)
else:
    try:
        preprocessor = joblib.load(PREPROCESSOR_PATH)
        if not hasattr(preprocessor, "transform"):
            preprocessor_load_error = "Loaded preprocessor has no transform()."
            preprocessor = None
            print("PREPROCESSOR STATUS: FAILED -", preprocessor_load_error)
        else:
            print("PREPROCESSOR STATUS: READY (" + type(preprocessor).__name__ + ")")
    except Exception as e:
        preprocessor_load_error = str(e)
        print("PREPROCESSOR STATUS: FAILED -", preprocessor_load_error)
        traceback.print_exc()


# ==========================================================
# DATABASE
# ==========================================================

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL CHECK (role IN ('customer', 'admin')),
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                  INTEGER NOT NULL REFERENCES users(id),
    hotel                    TEXT NOT NULL,
    lead_time                INTEGER NOT NULL,
    arrival_date_month       TEXT NOT NULL,
    total_nights             INTEGER NOT NULL,
    adults                   INTEGER NOT NULL,
    children                 INTEGER NOT NULL,
    market_segment           TEXT NOT NULL,
    deposit_type             TEXT NOT NULL,
    prediction               INTEGER NOT NULL,
    prediction_label         TEXT NOT NULL,
    cancellation_probability REAL NOT NULL,
    risk_level               TEXT NOT NULL,
    created_at               TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_time ON predictions(created_at);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db():
    """Create tables and make sure the admin account exists."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    admin_email = os.environ.get("ADMIN_EMAIL", "admin@hotel.com").strip().lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    admin_name = os.environ.get("ADMIN_NAME", "Administrator")

    exists = conn.execute(
        "SELECT 1 FROM users WHERE role = 'admin' LIMIT 1").fetchone()

    if not exists:
        conn.execute(
            "INSERT INTO users (name, email, password_hash, role, created_at) "
            "VALUES (?, ?, ?, 'admin', ?)",
            (admin_name, admin_email, generate_password_hash(admin_password), now_iso()))
        conn.commit()
        print("\nADMIN ACCOUNT CREATED")
        print("  Email   :", admin_email)
        if "ADMIN_PASSWORD" not in os.environ:
            print("  Password: Admin@123   <-- DEFAULT. Set ADMIN_PASSWORD before real use.")
    conn.close()


init_db()


# ==========================================================
# AUTH HELPERS
# ==========================================================

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def make_token(user):
    return serializer.dumps({"uid": user["id"]})


def user_payload(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "role": user["role"],
    }


def current_user():
    """Resolve the bearer token to a user row (or None).

    The role is always read from the database, never trusted from the token.
    """
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    token = header[len("Bearer "):].strip()
    try:
        data = serializer.loads(token, max_age=TOKEN_MAX_AGE)
    except (BadSignature, SignatureExpired):
        return None
    return get_db().execute(
        "SELECT * FROM users WHERE id = ?", (data.get("uid"),)).fetchone()


def login_required(role=None):
    """Require a valid login, and optionally a specific role."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return jsonify({"error": "Please log in to continue."}), 401
            if role and user["role"] != role:
                return jsonify({"error": "You do not have permission to access this."}), 403
            g.user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def json_body():
    return request.get_json(silent=True) or {}


# ==========================================================
# ROUTES: BASIC
# ==========================================================

@app.route("/")
def home():
    return jsonify({
        "message": "Hotel Cancellation Prediction API",
        "status": "running",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
    })


@app.route("/health")
def health():
    if model is not None and preprocessor is not None:
        return jsonify({
            "status": "healthy",
            "model": "loaded",
            "preprocessor": "loaded",
            "model_type": type(model).__name__,
            "preprocessor_type": type(preprocessor).__name__,
        })
    return jsonify({
        "status": "error",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
        "model_error": model_load_error,
        "preprocessor_error": preprocessor_load_error,
    }), 500


# ==========================================================
# ROUTES: CUSTOMER REGISTER / LOGIN
# ==========================================================

@app.route("/api/register", methods=["POST"])
def register():
    data = json_body()
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(name) < 2 or len(name) > 80:
        return jsonify({"error": "Please enter your name (2-80 characters)."}), 400
    if not EMAIL_RE.match(email) or len(email) > 120:
        return jsonify({"error": "Please enter a valid email address."}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters."}), 400

    db = get_db()
    if db.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
        return jsonify({"error": "An account with this email already exists."}), 409

    # Role is ALWAYS 'customer' here - nobody can self-register as admin.
    cur = db.execute(
        "INSERT INTO users (name, email, password_hash, role, created_at) "
        "VALUES (?, ?, ?, 'customer', ?)",
        (name, email, generate_password_hash(password), now_iso()))
    db.commit()

    user = db.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify({"token": make_token(user), "user": user_payload(user)}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = json_body()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = get_db().execute(
        "SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401

    if user["role"] != "customer":
        return jsonify({"error": "Administrators must use the Admin Login page."}), 403

    return jsonify({"token": make_token(user), "user": user_payload(user)})


# ==========================================================
# ROUTES: ADMIN LOGIN
# ==========================================================

@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    data = json_body()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = get_db().execute(
        "SELECT * FROM users WHERE email = ?", (email,)).fetchone()

    if user is None or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401

    if user["role"] != "admin":
        return jsonify({"error": "This account does not have admin access."}), 403

    return jsonify({"token": make_token(user), "user": user_payload(user)})


@app.route("/api/me")
@login_required()
def me():
    return jsonify({"user": user_payload(g.user)})


# ==========================================================
# PREDICTION  (customers only)
# ==========================================================

HOTELS = {"Resort Hotel", "City Hotel"}
MONTHS = {"January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"}
MARKET_SEGMENTS = {"Online TA", "Offline TA/TO", "Direct", "Groups", "Corporate"}
DEPOSIT_TYPES = {"No Deposit", "Non Refund", "Refundable"}

# Features the form does not collect - the model still needs them.
MODEL_DEFAULTS = {
    "arrival_date_year": 2017,
    "arrival_date_week_number": 28,
    "arrival_date_day_of_month": 10,
    "babies": 0,
    "meal": "BB",
    "country": "PRT",
    "distribution_channel": "TA/TO",
    "is_repeated_guest": 0,
    "previous_cancellations": 0,
    "previous_bookings_not_canceled": 0,
    "reserved_room_type": "A",
    "assigned_room_type": "A",
    "booking_changes": 0,
    "agent": 9,
    "company": 0,
    "days_in_waiting_list": 0,
    "customer_type": "Transient",
    "adr": 100,
    "required_car_parking_spaces": 0,
    "total_of_special_requests": 0,
}


def to_int(data, field, low, high):
    try:
        value = int(float(data.get(field)))
    except (TypeError, ValueError):
        raise ValueError(f"'{field}' must be a number.")
    if value < low or value > high:
        raise ValueError(f"'{field}' must be between {low} and {high}.")
    return value


def validate_booking(data):
    """Return a clean booking dict, or raise ValueError with a friendly message."""
    booking = {}

    for field, allowed in (("hotel", HOTELS),
                           ("arrival_date_month", MONTHS),
                           ("market_segment", MARKET_SEGMENTS),
                           ("deposit_type", DEPOSIT_TYPES)):
        value = data.get(field)
        if value in (None, ""):
            raise ValueError(f"'{field}' is required.")
        if value not in allowed:
            raise ValueError(f"'{field}' has an invalid value.")
        booking[field] = value

    booking["lead_time"] = to_int(data, "lead_time", 0, 1000)
    booking["stays_in_weekend_nights"] = to_int(data, "stays_in_weekend_nights", 0, 365)
    booking["stays_in_week_nights"] = to_int(data, "stays_in_week_nights", 0, 365)
    booking["adults"] = to_int(data, "adults", 1, 20)
    booking["children"] = to_int(data, "children", 0, 20)

    if booking["stays_in_weekend_nights"] + booking["stays_in_week_nights"] < 1:
        raise ValueError("The stay must be at least 1 night.")
    return booking


def risk_from_probability(p):
    if p < 40:
        return "Low"
    if p < 70:
        return "Medium"
    return "High"


@app.route("/predict", methods=["POST"])
@login_required(role="customer")
def predict():
    try:
        if model is None or preprocessor is None:
            return jsonify({
                "error": "Prediction model is not available.",
                "details": model_load_error or preprocessor_load_error,
            }), 500

        try:
            booking = validate_booking(json_body())
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Model input = server defaults + the validated booking fields.
        row = dict(MODEL_DEFAULTS)
        row.update(booking)
        input_data = pd.DataFrame([row])

        processed = preprocessor.transform(input_data)
        prediction = int(model.predict(processed)[0])

        classes = list(model.classes_)
        if hasattr(model, "predict_proba") and 1 in classes:
            proba = model.predict_proba(processed)[0]
            probability = float(proba[classes.index(1)]) * 100
        else:
            probability = 100.0 if prediction == 1 else 0.0
        probability = round(probability, 2)

        label = "Cancelled" if prediction == 1 else "Not Cancelled"
        risk = risk_from_probability(probability)
        total_nights = booking["stays_in_weekend_nights"] + booking["stays_in_week_nights"]
        created_at = now_iso()

        # ---- save to history (linked to the logged-in customer) ----
        db = get_db()
        cur = db.execute(
            """INSERT INTO predictions
               (user_id, hotel, lead_time, arrival_date_month, total_nights,
                adults, children, market_segment, deposit_type,
                prediction, prediction_label, cancellation_probability,
                risk_level, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (g.user["id"], booking["hotel"], booking["lead_time"],
             booking["arrival_date_month"], total_nights, booking["adults"],
             booking["children"], booking["market_segment"],
             booking["deposit_type"], prediction, label, probability,
             risk, created_at))
        db.commit()

        return jsonify({
            "id": cur.lastrowid,
            "prediction": prediction,
            "prediction_label": label,
            "cancellation_probability": probability,
            "risk_level": risk,
            "hotel_received": booking["hotel"],
            "lead_time_received": booking["lead_time"],
            "total_nights_received": total_nights,
            "created_at": created_at,
        }), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e), "error_type": type(e).__name__}), 500


# ==========================================================
# HISTORY
# ==========================================================

BOOKING_COLUMNS = """
    p.id, p.hotel, p.lead_time, p.arrival_date_month, p.total_nights,
    p.adults, p.children, p.market_segment, p.deposit_type,
    p.prediction, p.prediction_label, p.cancellation_probability,
    p.risk_level, p.created_at
"""


@app.route("/api/history")
@login_required(role="customer")
def my_history():
    """A customer only ever gets their OWN predictions (filtered by token user)."""
    rows = get_db().execute(
        f"SELECT {BOOKING_COLUMNS} FROM predictions p "
        "WHERE p.user_id = ? ORDER BY p.id DESC", (g.user["id"],)).fetchall()
    return jsonify({"history": [dict(r) for r in rows]})


@app.route("/api/admin/history")
@login_required(role="admin")
def admin_history():
    """Every customer's predictions, with the customer's name and email."""
    rows = get_db().execute(
        f"""SELECT {BOOKING_COLUMNS},
                   u.name  AS customer_name,
                   u.email AS customer_email
            FROM predictions p
            JOIN users u ON u.id = p.user_id
            ORDER BY p.id DESC""").fetchall()
    return jsonify({"history": [dict(r) for r in rows]})


@app.route("/api/admin/stats")
@login_required(role="admin")
def admin_stats():
    db = get_db()
    total = db.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
    cancelled = db.execute(
        "SELECT COUNT(*) FROM predictions WHERE prediction = 1").fetchone()[0]
    risk = {r["risk_level"]: r["n"] for r in db.execute(
        "SELECT risk_level, COUNT(*) AS n FROM predictions GROUP BY risk_level")}
    customers = db.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'customer'").fetchone()[0]

    return jsonify({
        "total_customers": customers,
        "total_predictions": total,
        "cancelled": cancelled,
        "not_cancelled": total - cancelled,
        "cancellation_rate": round(cancelled / total * 100, 1) if total else 0.0,
        "high_risk": risk.get("High", 0),
        "medium_risk": risk.get("Medium", 0),
        "low_risk": risk.get("Low", 0),
    })


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    print("\nServer : http://127.0.0.1:5000")
    print("Health : http://127.0.0.1:5000/health\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
