import joblib
import time

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


print("=" * 60)
print("HOTEL CANCELLATION - MODEL TRAINING")
print("=" * 60)


# --------------------------------------------------
# 1. Load preprocessed data
# --------------------------------------------------

X_train = joblib.load("models/X_train.pkl")
X_test = joblib.load("models/X_test.pkl")

y_train = joblib.load("models/y_train.pkl")
y_test = joblib.load("models/y_test.pkl")


print("\nTraining data:")
print(X_train.shape)

print("\nTesting data:")
print(X_test.shape)


# --------------------------------------------------
# 2. Define models
# --------------------------------------------------

models = {

    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        random_state=42
    ),

    "Decision Tree": DecisionTreeClassifier(
        max_depth=15,
        random_state=42
    ),

    "Random Forest": RandomForestClassifier(
        n_estimators=150,
        max_depth=20,
        random_state=42,
        n_jobs=-1
    )
}


# --------------------------------------------------
# 3. Train and evaluate models
# --------------------------------------------------

results = {}


for name, model in models.items():

    print("\n" + "-" * 60)
    print("Training:", name)
    print("-" * 60)

    start_time = time.time()

    # Train model
    model.fit(X_train, y_train)

    # Prediction
    y_pred = model.predict(X_test)

    # Probability
    y_probability = model.predict_proba(X_test)[:, 1]

    # Evaluation
    accuracy = accuracy_score(y_test, y_pred)

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    cm = confusion_matrix(
        y_test,
        y_pred
    )

    training_time = time.time() - start_time


    # Store results
    results[name] = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "confusion_matrix": cm,
        "training_time": training_time
    }


    # Print results
    print("\nAccuracy :", round(accuracy, 4))
    print("Precision:", round(precision, 4))
    print("Recall   :", round(recall, 4))
    print("F1 Score :", round(f1, 4))

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            zero_division=0
        )
    )

    print(
        "Training + prediction time:",
        round(training_time, 2),
        "seconds"
    )


# --------------------------------------------------
# 4. Compare models
# --------------------------------------------------

print("\n" + "=" * 60)
print("MODEL COMPARISON")
print("=" * 60)

print(
    "\n{:<22} {:<12} {:<12} {:<12} {:<12}".format(
        "Model",
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score"
    )
)

print("-" * 70)


for name, result in results.items():

    print(
        "{:<22} {:<12.4f} {:<12.4f} {:<12.4f} {:<12.4f}".format(
            name,
            result["accuracy"],
            result["precision"],
            result["recall"],
            result["f1_score"]
        )
    )


# --------------------------------------------------
# 5. Select best model
# --------------------------------------------------

best_model_name = max(
    results,
    key=lambda x: results[x]["f1_score"]
)


print("\n" + "=" * 60)
print("BEST MODEL")
print("=" * 60)

print("\nBest Model:", best_model_name)

print(
    "Best F1 Score:",
    round(
        results[best_model_name]["f1_score"],
        4
    )
)


# --------------------------------------------------
# 6. Train best model again
# --------------------------------------------------

best_model = models[best_model_name]


# --------------------------------------------------
# 7. Save best model
# --------------------------------------------------

joblib.dump(
    best_model,
    "models/hotel_cancellation_model.pkl"
)

print("\nBest model saved successfully!")

print(
    "models/hotel_cancellation_model.pkl"
)


# --------------------------------------------------
# 8. Save model results
# --------------------------------------------------

joblib.dump(
    results,
    "models/model_results.pkl"
)

print(
    "models/model_results.pkl"
)


print("\n" + "=" * 60)
print("MODEL TRAINING COMPLETED")
print("=" * 60)