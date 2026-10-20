"""
Unit Tests for Synthetic Data Generation
CareBridge Hospitals - Challenge ID: U23AD491
"""

import os
import pytest
import pandas as pd
from generate_dataset import generate_all_datasets

def test_data_generation_creates_all_files(tmp_path):
    test_raw_dir = str(tmp_path / "raw")
    generate_all_datasets(raw_dir=test_raw_dir, seed=123)

    expected_files = [
        "appointments.csv", "patients.csv", "doctors.csv",
        "reminders.csv", "calendar.csv"
    ]
    for fname in expected_files:
        fpath = os.path.join(test_raw_dir, fname)
        assert os.path.exists(fpath), f"Missing generated file: {fname}"

def test_record_counts_and_schemas(tmp_path):
    test_raw_dir = str(tmp_path / "raw")
    generate_all_datasets(raw_dir=test_raw_dir, seed=123)

    df_app = pd.read_csv(os.path.join(test_raw_dir, "appointments.csv"))
    df_pat = pd.read_csv(os.path.join(test_raw_dir, "patients.csv"))
    df_doc = pd.read_csv(os.path.join(test_raw_dir, "doctors.csv"))
    df_cal = pd.read_csv(os.path.join(test_raw_dir, "calendar.csv"))

    # Record counts
    assert 4900 <= len(df_app) <= 5100, f"Unexpected appointments count: {len(df_app)}"
    assert len(df_pat) == 1500, f"Unexpected patients count: {len(df_pat)}"
    assert len(df_doc) == 30, f"Unexpected doctors count: {len(df_doc)}"
    assert len(df_cal) == 366, f"Unexpected calendar days count: {len(df_cal)}"

    # Check required columns
    required_app_cols = [
        "appointment_id", "patient_id", "doctor_id", "appointment_date",
        "booking_date", "department", "appointment_status", "waiting_days"
    ]
    for col in required_app_cols:
        assert col in df_app.columns, f"Missing column {col} in appointments"
