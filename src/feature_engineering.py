"""
Feature Engineering Module
CareBridge Hospitals - Hospital Appointment Insight (Challenge ID: U23AD491)

Transforms cleaned appointment data into high-value ML features while strictly
preventing target leakage and future-lookahead bias.
"""

import os
import numpy as np
import pandas as pd

def build_features(df_clean, is_training_data=True):
    """
    Constructs ML-ready features from cleaned appointments.
    
    Leakage Prevention:
    - Calculates strictly historical, point-in-time patient attendance statistics
      (prior appointments and prior no-shows strictly occurring before the current record).
    - Excludes identifiers (IDs, names) and direct outcome fields.
    - Excludes non-binary appointment statuses (Cancelled, Rescheduled, Pending, Unresolved)
      when preparing the classification training/testing set.
    """
    df = df_clean.copy()

    # Ensure chronological order by appointment date and time
    df["dt_combined"] = pd.to_datetime(df["appointment_date"] + " " + df["appointment_time"])
    df = df.sort_values(by=["patient_id", "dt_combined"]).reset_index(drop=True)

    # 1. Point-in-time historical patient features (strictly before current appointment)
    # Using shift(1) within patient grouping to strictly avoid target leakage
    is_attended = (df["appointment_status_clean"] == "Attended").astype(int)
    is_noshow = (df["appointment_status_clean"] == "No-show").astype(int)

    # Cumulative resolved visits before current appointment
    df["prior_noshow_count"] = df.groupby("patient_id")["appointment_status_clean"].transform(
        lambda s: (s == "No-show").cumsum().shift(1).fillna(0)
    ).astype(int)

    df["prior_attended_count"] = df.groupby("patient_id")["appointment_status_clean"].transform(
        lambda s: (s == "Attended").cumsum().shift(1).fillna(0)
    ).astype(int)

    df["prior_appointments_count"] = df["prior_noshow_count"] + df["prior_attended_count"]

    # Historical no-show rate prior to this appointment
    df["prior_noshow_rate"] = np.where(
        df["prior_appointments_count"] > 0,
        df["prior_noshow_count"] / df["prior_appointments_count"],
        0.0
    )

    # Prior no-show frequency category
    def categorize_prior_noshows(n):
        if n == 0:
            return "0 Prior Misses"
        elif n == 1:
            return "1 Prior Miss"
        elif n == 2:
            return "2 Prior Misses"
        else:
            return "3+ Prior Misses"

    df["repeat_noshow_category"] = df["prior_noshow_count"].apply(categorize_prior_noshows)

    # 2. Calendar and Time Features
    df["appointment_date_dt"] = pd.to_datetime(df["appointment_date"])
    df["is_weekend"] = df["weekday"].isin(["Saturday", "Sunday"]).astype(int)
    df["is_holiday"] = (df["holiday"] == "Yes").astype(int)
    df["appointment_hour"] = pd.to_datetime(df["appointment_time"], format="%H:%M").dt.hour

    # Re-sort back to global chronological order for chronological train/test splitting
    df = df.sort_values(by=["dt_combined", "appointment_id"]).reset_index(drop=True)

    # Define binary target for model training: 1 = No-show, 0 = Attended
    # Keep only Attended and No-show if is_training_data is True
    if is_training_data:
        ml_df = df[df["appointment_status_clean"].isin(["Attended", "No-show"])].copy()
        ml_df["target"] = (ml_df["appointment_status_clean"] == "No-show").astype(int)
    else:
        ml_df = df.copy()
        ml_df["target"] = np.where(ml_df["appointment_status_clean"] == "No-show", 1, 0)

    # Feature lists
    numerical_features = [
        "waiting_days",
        "age",
        "appointment_hour",
        "prior_appointments_count",
        "prior_noshow_count",
        "prior_noshow_rate",
        "is_weekend",
        "is_holiday"
    ]

    categorical_features = [
        "department",
        "specialty",
        "clinic_schedule",
        "age_group",
        "locality",
        "weekday",
        "month",
        "season",
        "reminder_type",
        "reminder_sent",
        "reminder_response",
        "waiting_time_group",
        "repeat_noshow_category"
    ]

    return ml_df, numerical_features, categorical_features

if __name__ == "__main__":
    cleaned_path = "data/processed/cleaned_appointments.csv"
    if os.path.exists(cleaned_path):
        df = pd.read_csv(cleaned_path)
        ml_df, num_cols, cat_cols = build_features(df)
        print(f"Engineered features successfully. ML records: {len(ml_df)}")
        print(f"Target distribution:\n{ml_df['target'].value_counts(normalize=True)}")
        print(f"Numerical features ({len(num_cols)}): {num_cols}")
        print(f"Categorical features ({len(cat_cols)}): {cat_cols}")
    else:
        print("Cleaned appointments not found. Run preprocessing first.")
