import pandas as pd

# Load dataset
df = pd.read_csv("dataset/hotel_bookings.csv")

print("=" * 50)
print("HOTEL BOOKING DATASET ANALYSIS")
print("=" * 50)

# 1. Dataset shape
print("\nDataset Shape:")
print(df.shape)

# 2. First five records
print("\nFirst 5 Records:")
print(df.head())

# 3. Column names
print("\nColumn Names:")
print(df.columns.tolist())

# 4. Data types
print("\nData Types:")
print(df.dtypes)

# 5. Missing values
print("\nMissing Values:")
print(df.isnull().sum().sort_values(ascending=False))

# 6. Duplicate rows
print("\nDuplicate Rows:")
print(df.duplicated().sum())

# 7. Target distribution
print("\nCancellation Distribution:")
print(df["is_canceled"].value_counts())

# 8. Target percentage
print("\nCancellation Percentage:")
print(df["is_canceled"].value_counts(normalize=True) * 100)