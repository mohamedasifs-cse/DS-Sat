"""
Unit Tests for Feature Engineering and Target Leakage Prevention
CareBridge Hospitals - Challenge ID: U23AD491
"""

import os
import pytest
import pandas as pd
from src.feature_engineering import build_features

def test_leakage_free_feature_engineering():
    cleaned_path = "data/processed/cleaned_appointments.csv"
    assert os.path.exists(cleaned_path), "Cleaned appointments file not found"
    df_clean = pd.read_csv(cleaned_path)

    ml_df, num_cols, cat_cols = build_features(df_clean, is_training_data=True)

    # 1. Target definition check: only 0 and 1
    assert set(ml_df["target"].unique()).issubset({0, 1}), "Invalid target values"

    # 2. Mathematical consistency: prior_appointments >= prior_noshows
    assert (ml_df["prior_appointments_count"] >= ml_df["prior_noshow_count"]).all()

    # 3. Leakage prevention check:
    # For every patient, their first chronological appointment MUST have 0 prior appointments and 0 prior no-shows
    ml_df_sorted = ml_df.sort_values(by=["patient_id", "appointment_date", "appointment_time"])
    first_visits = ml_df_sorted.groupby("patient_id").first()
    assert (first_visits["prior_appointments_count"] == 0).all(), "Leakage detected: First visit has prior appointments!"
    assert (first_visits["prior_noshow_count"] == 0).all(), "Leakage detected: First visit has prior no-shows!"
    assert (first_visits["prior_noshow_rate"] == 0.0).all(), "Leakage detected: First visit has non-zero prior no-show rate!"
