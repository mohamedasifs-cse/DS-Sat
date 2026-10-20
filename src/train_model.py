"""
Model Training Module
CareBridge Hospitals - Hospital Appointment Insight (Challenge ID: U23AD491)

Trains three classification models with Scikit-learn Pipelines:
1. DummyClassifier (Baseline)
2. Logistic Regression (Linear Model with Class Balancing)
3. Random Forest Classifier (Ensemble Model with Feature Importances)

Employs chronological train-test split to respect temporal structure.
"""

import os
import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

from src.feature_engineering import build_features

def get_preprocessor(numerical_cols, categorical_cols):
    """Creates a Scikit-learn ColumnTransformer for numerical and categorical features."""
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numerical_cols),
            ("cat", cat_pipeline, categorical_cols)
        ]
    )
    return preprocessor

def train_all_models(df_clean, test_ratio=0.20):
    """
    Splits data chronologically and trains Dummy, Logistic Regression,
    and Random Forest models.
    """
    print("\n[Model Training] Engineering features and preparing datasets...")
    ml_df, num_cols, cat_cols = build_features(df_clean, is_training_data=True)

    # Sort strictly by chronological order
    ml_df = ml_df.sort_values(by="appointment_date").reset_index(drop=True)
    
    # Chronological train/test split
    split_idx = int(len(ml_df) * (1 - test_ratio))
    train_df = ml_df.iloc[:split_idx].copy()
    test_df = ml_df.iloc[split_idx:].copy()

    X_train = train_df[num_cols + cat_cols]
    y_train = train_df["target"].values
    X_test = test_df[num_cols + cat_cols]
    y_test = test_df["target"].values

    print(f"  - Chronological split: {len(X_train)} training records | {len(X_test)} testing records")
    print(f"  - Training date range: {train_df['appointment_date'].min()} to {train_df['appointment_date'].max()}")
    print(f"  - Testing date range:  {test_df['appointment_date'].min()} to {test_df['appointment_date'].max()}")
    print(f"  - Training no-show rate: {y_train.mean()*100:.2f}% | Testing no-show rate: {y_test.mean()*100:.2f}%")

    # Define models
    models = {
        "Dummy Classifier": DummyClassifier(strategy="most_frequent"),
        "Logistic Regression": LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", random_state=42)
    }

    trained_pipelines = {}
    for name, clf in models.items():
        print(f"  - Fitting {name} pipeline...")
        pipe = Pipeline([
            ("preprocessor", get_preprocessor(num_cols, cat_cols)),
            ("classifier", clf)
        ])
        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

    return trained_pipelines, X_train, y_train, X_test, y_test, num_cols, cat_cols

if __name__ == "__main__":
    from src.data_preprocessing import clean_and_merge_data
    df = clean_and_merge_data()
    trained_pipes, X_tr, y_tr, X_te, y_te, n_cols, c_cols = train_all_models(df)
    print("Models trained successfully.")
