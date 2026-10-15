import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


print("=" * 60)
print("HOTEL CANCELLATION - DATA PREPROCESSING")
print("=" * 60)


# --------------------------------------------------
# 1. Load cleaned dataset
# --------------------------------------------------

df = pd.read_csv("dataset/hotel_bookings_cleaned.csv")

print("\nDataset shape:")
print(df.shape)


# --------------------------------------------------
# 2. Define target variable
# --------------------------------------------------

target = "is_canceled"

X = df.drop(columns=[target])
y = df[target]


print("\nTarget variable:")
print(target)

print("\nTarget distribution:")
print(y.value_counts())


# --------------------------------------------------
# 3. Select features
# --------------------------------------------------

numerical_features = [
    "lead_time",
    "arrival_date_year",
    "arrival_date_week_number",
    "arrival_date_day_of_month",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "booking_changes",
    "agent",
    "company",
    "days_in_waiting_list",
    "adr",
    "required_car_parking_spaces",
    "total_of_special_requests"
]


categorical_features = [
    "hotel",
    "arrival_date_month",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "assigned_room_type",
    "deposit_type",
    "customer_type"
]


# --------------------------------------------------
# 4. Check features
# --------------------------------------------------

print("\nNumerical features:")
print(numerical_features)

print("\nCategorical features:")
print(categorical_features)


# --------------------------------------------------
# 5. Train-test split
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining data shape:")
print(X_train.shape)

print("\nTesting data shape:")
print(X_test.shape)


# --------------------------------------------------
# 6. Numerical preprocessing
# --------------------------------------------------

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        ),
        (
            "scaler",
            StandardScaler()
        )
    ]
)


# --------------------------------------------------
# 7. Categorical preprocessing
# --------------------------------------------------

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


# --------------------------------------------------
# 8. Combine preprocessing
# --------------------------------------------------

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            numerical_pipeline,
            numerical_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# --------------------------------------------------
# 9. Fit preprocessing on training data
# --------------------------------------------------

X_train_processed = preprocessor.fit_transform(X_train)

X_test_processed = preprocessor.transform(X_test)


print("\nProcessed training data shape:")
print(X_train_processed.shape)

print("\nProcessed testing data shape:")
print(X_test_processed.shape)


# --------------------------------------------------
# 10. Create models directory
# --------------------------------------------------

os.makedirs("models", exist_ok=True)


# --------------------------------------------------
# 11. Save preprocessor
# --------------------------------------------------

joblib.dump(
    preprocessor,
    "models/preprocessor.pkl"
)


# --------------------------------------------------
# 12. Save processed data
# --------------------------------------------------

joblib.dump(
    X_train_processed,
    "models/X_train.pkl"
)

joblib.dump(
    X_test_processed,
    "models/X_test.pkl"
)

joblib.dump(
    y_train,
    "models/y_train.pkl"
)

joblib.dump(
    y_test,
    "models/y_test.pkl"
)


print("\nPreprocessing files saved successfully!")

print("\nSaved files:")
print("models/preprocessor.pkl")
print("models/X_train.pkl")
print("models/X_test.pkl")
print("models/y_train.pkl")
print("models/y_test.pkl")


print("\n" + "=" * 60)
print("PREPROCESSING COMPLETED")
print("=" * 60)
