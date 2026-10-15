import pandas as pd
import joblib
import os
import matplotlib.pyplot as plt

from sklearn.metrics import ConfusionMatrixDisplay


print("=" * 60)
print("HOTEL CANCELLATION - MODEL EVALUATION")
print("=" * 60)


# --------------------------------------------------
# 1. Create output folder
# --------------------------------------------------

os.makedirs("evaluation", exist_ok=True)


# --------------------------------------------------
# 2. Load trained model and test data
# --------------------------------------------------

model = joblib.load(
    "models/hotel_cancellation_model.pkl"
)

X_test = joblib.load(
    "models/X_test.pkl"
)

y_test = joblib.load(
    "models/y_test.pkl"
)


print("\nModel loaded successfully.")

print("Model type:")
print(type(model).__name__)


# --------------------------------------------------
# 3. Make predictions
# --------------------------------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]


# --------------------------------------------------
# 4. Confusion Matrix
# --------------------------------------------------

print("\nGenerating confusion matrix...")

plt.figure(figsize=(7, 6))

ConfusionMatrixDisplay.from_predictions(
    y_test,
    y_pred,
    display_labels=[
        "Not Cancelled",
        "Cancelled"
    ]
)

plt.title("Hotel Booking Cancellation - Confusion Matrix")

plt.tight_layout()

plt.savefig(
    "evaluation/confusion_matrix.png",
    dpi=300
)

plt.close()


print(
    "Saved: evaluation/confusion_matrix.png"
)


# --------------------------------------------------
# 5. Model Comparison
# --------------------------------------------------

results = joblib.load(
    "models/model_results.pkl"
)


model_names = list(results.keys())

accuracy = [
    results[name]["accuracy"]
    for name in model_names
]

precision = [
    results[name]["precision"]
    for name in model_names
]

recall = [
    results[name]["recall"]
    for name in model_names
]

f1 = [
    results[name]["f1_score"]
    for name in model_names
]


comparison_df = pd.DataFrame({
    "Model": model_names,
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1 Score": f1
})


print("\nModel comparison:")
print(comparison_df)


# --------------------------------------------------
# 6. Model comparison graph
# --------------------------------------------------

comparison_df.set_index("Model").plot(
    kind="bar",
    figsize=(10, 6)
)

plt.title(
    "Comparison of Machine Learning Models"
)

plt.ylabel("Score")

plt.ylim(0, 1)

plt.xticks(rotation=0)

plt.legend(
    loc="lower right"
)

plt.tight_layout()

plt.savefig(
    "evaluation/model_comparison.png",
    dpi=300
)

plt.close()


print(
    "Saved: evaluation/model_comparison.png"
)


# --------------------------------------------------
# 7. Feature Importance
# --------------------------------------------------

print("\nGenerating feature importance...")

preprocessor = joblib.load(
    "models/preprocessor.pkl"
)


# Get transformed feature names

feature_names = preprocessor.get_feature_names_out()


# Get decision tree importance

importance = model.feature_importances_


feature_importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importance
})


feature_importance_df = (
    feature_importance_df
    .sort_values(
        by="Importance",
        ascending=False
    )
)


print("\nTop 20 important features:")

print(
    feature_importance_df.head(20)
)


# --------------------------------------------------
# 8. Plot top 15 features
# --------------------------------------------------

top_features = feature_importance_df.head(15)

top_features = top_features.sort_values(
    by="Importance"
)


plt.figure(figsize=(10, 7))

plt.barh(
    top_features["Feature"],
    top_features["Importance"]
)

plt.title(
    "Top 15 Features Influencing Cancellation Prediction"
)

plt.xlabel("Importance")

plt.tight_layout()

plt.savefig(
    "evaluation/feature_importance.png",
    dpi=300
)

plt.close()


print(
    "Saved: evaluation/feature_importance.png"
)


# --------------------------------------------------
# 9. Cancellation probability distribution
# --------------------------------------------------

plt.figure(figsize=(9, 6))

plt.hist(
    y_probability[y_test == 0],
    bins=20,
    alpha=0.6,
    label="Not Cancelled"
)

plt.hist(
    y_probability[y_test == 1],
    bins=20,
    alpha=0.6,
    label="Cancelled"
)

plt.title(
    "Cancellation Probability Distribution"
)

plt.xlabel(
    "Predicted Cancellation Probability"
)

plt.ylabel(
    "Number of Bookings"
)

plt.legend()

plt.tight_layout()

plt.savefig(
    "evaluation/cancellation_probability.png",
    dpi=300
)

plt.close()


print(
    "Saved: evaluation/cancellation_probability.png"
)


# --------------------------------------------------
# 10. Save model comparison CSV
# --------------------------------------------------

comparison_df.to_csv(
    "evaluation/model_comparison.csv",
    index=False
)


# --------------------------------------------------
# 11. Save feature importance CSV
# --------------------------------------------------

feature_importance_df.to_csv(
    "evaluation/feature_importance.csv",
    index=False
)


print(
    "\nSaved evaluation CSV files."
)


print("\n" + "=" * 60)
print("MODEL EVALUATION COMPLETED")
print("=" * 60)