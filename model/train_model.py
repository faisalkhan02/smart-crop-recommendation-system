"""
train_model.py

Trains a model to recommend the best crop based on soil and climate data.

Steps:
1. Load the dataset (Crop_recommendation.csv)
2. Train 3 different models and compare them:
   - Logistic Regression (simple baseline)
   - Random Forest (multiple decision trees combined)
   - Gradient Boosting (trees built one after another, correcting previous errors)
3. Select whichever model gives the best accuracy
4. Save that model to disk so the backend can load it later

Run with: python train_model.py
"""

# for reading the CSV and working with tabular data
import pandas as pd

# used internally for array operations
import numpy as np

# for saving/loading the trained model to a file
import joblib

# splits dataset into train and test sets
from sklearn.model_selection import train_test_split

# converts crop names (text) into numbers, since models need numeric input
from sklearn.preprocessing import LabelEncoder

# baseline model
from sklearn.linear_model import LogisticRegression

# tree-based models being compared against the baseline
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

# metrics used to check how good each model is
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

# ------------------- PATHS -------------------
# dataset is one folder up, inside data/
DATA_PATH = "../data/Crop_recommendation.csv"

# trained model gets saved into backend/ so main.py can load it directly
MODEL_OUT = "../backend/model.pkl"

# label encoder saved too, needed to convert predicted numbers back to crop names
ENCODER_OUT = "../backend/label_encoder.pkl"

# ------------------- FEATURES & TARGET -------------------
# columns used as input
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# column being predicted
TARGET = "label"


def main():
    # ---------- loading the dataset ----------
    print("Loading dataset...")
    df = pd.read_csv(DATA_PATH)

    print(f"Shape: {df.shape}")  # rows/columns count check
    print(f"Classes: {df[TARGET].nunique()}")  # number of different crops

    # checking for missing values before training
    print(f"Missing values:\n{df.isnull().sum()}")

    # ---------- splitting into features and target ----------
    X = df[FEATURES]
    y = df[TARGET]

    # ---------- encoding crop names into numbers ----------
    # e.g. rice -> 0, maize -> 1, chickpea -> 2, and so on
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # ---------- train/test split ----------
    # 20% kept aside to test the model on data it hasn't seen
    # stratify ensures each crop is proportionally represented in both sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )

    # ---------- the 3 models being compared ----------
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=150, random_state=42),
    }

    # tracking results and the best model found so far
    results = {}
    best_model = None
    best_score = -1
    best_name = ""

    # ---------- training and evaluating each model ----------
    for name, model in models.items():
        print(f"\nTraining {name}...")

        # training the model
        model.fit(X_train, y_train)

        # testing on data not seen before
        preds = model.predict(X_test)

        # percentage of predictions that were correct
        acc = accuracy_score(y_test, preds)

        # balance of precision and recall, useful alongside accuracy
        f1 = f1_score(y_test, preds, average="weighted")

        results[name] = {"accuracy": acc, "f1": f1}
        print(f"{name} -> Accuracy: {acc:.4f}, F1: {f1:.4f}")

        # keeping track of whichever model performs best so far
        if acc > best_score:
            best_score = acc
            best_model = model
            best_name = name

    # ---------- printing a summary of all 3 models ----------
    print("\n" + "=" * 50)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 50)
    for name, r in results.items():
        print(f"{name:25s} Accuracy: {r['accuracy']:.4f}  F1: {r['f1']:.4f}")

    print(f"\nBest model: {best_name} (Accuracy: {best_score:.4f})")

    # ---------- detailed report for the winning model ----------
    # shows precision/recall for each individual crop -
    # useful to see which crops the model confuses with others
    final_preds = best_model.predict(X_test)
    print("\nClassification Report (best model):")
    print(classification_report(y_test, final_preds, target_names=le.classes_))

    # ---------- saving the best model and encoder ----------
    # backend/main.py loads these two files to make predictions
    joblib.dump(best_model, MODEL_OUT)
    joblib.dump(le, ENCODER_OUT)

    print(f"\nSaved model to {MODEL_OUT}")
    print(f"Saved label encoder to {ENCODER_OUT}")
    print(f"Best model name for report: {best_name}")


# runs main() only when this file is executed directly, not when imported
if __name__ == "__main__":
    main()