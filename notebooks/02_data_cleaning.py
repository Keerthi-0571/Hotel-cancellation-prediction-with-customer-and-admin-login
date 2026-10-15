import pandas as pd
import os

print("=" * 60)
print("HOTEL BOOKING DATA CLEANING")
print("=" * 60)

# Load dataset
df = pd.read_csv("dataset/hotel_bookings.csv")

print("\nOriginal dataset shape:")
print(df.shape)

# --------------------------------------------------
# 1. Remove duplicate rows
# --------------------------------------------------

duplicate_count = df.duplicated().sum()

print("\nDuplicate rows found:", duplicate_count)

df = df.drop_duplicates()

print("Shape after removing duplicates:")
print(df.shape)

# --------------------------------------------------
# 2. Remove data leakage columns
# --------------------------------------------------

columns_to_remove = [
    "reservation_status",
    "reservation_status_date"
]

df = df.drop(columns=columns_to_remove)

print("\nRemoved columns:")
print(columns_to_remove)

# --------------------------------------------------
# 3. Handle missing values
# --------------------------------------------------

# Company and agent:
# Missing values indicate that no company/agent was recorded.
# Replace missing values with 0.

df["company"] = df["company"].fillna(0)
df["agent"] = df["agent"].fillna(0)

# Country:
# Replace missing country with "Unknown".

df["country"] = df["country"].fillna("Unknown")

# Children:
# Replace missing children values with 0.

df["children"] = df["children"].fillna(0)

# --------------------------------------------------
# 4. Check missing values
# --------------------------------------------------

print("\nMissing values after cleaning:")

missing_values = df.isnull().sum()

print(missing_values[missing_values > 0])

# --------------------------------------------------
# 5. Check duplicates again
# --------------------------------------------------

print("\nDuplicates after cleaning:")
print(df.duplicated().sum())

# --------------------------------------------------
# 6. Final dataset information
# --------------------------------------------------

print("\nFinal dataset shape:")
print(df.shape)

print("\nFinal columns:")
print(df.columns.tolist())

# --------------------------------------------------
# 7. Save cleaned dataset
# --------------------------------------------------

os.makedirs("dataset", exist_ok=True)

output_file = "dataset/hotel_bookings_cleaned.csv"

df.to_csv(output_file, index=False)

print("\nCleaned dataset saved successfully!")
print(output_file)

print("\n" + "=" * 60)
print("DATA CLEANING COMPLETED")
print("=" * 60)