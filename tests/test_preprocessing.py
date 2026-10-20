"""
Unit Tests for Data Preprocessing and Cleaning
CareBridge Hospitals - Challenge ID: U23AD491
"""

import os
import pytest
import pandas as pd
from src.data_preprocessing import clean_and_merge_data

def test_preprocessing_deduplication_and_waiting_days():
    df_clean = clean_and_merge_data(raw_dir="data/raw", processed_dir="data/processed")

    # 1. Deduplication check: appointment_id should be unique
    assert df_clean["appointment_id"].is_unique, "Duplicate appointment IDs remain after cleaning!"

    # 2. No negative waiting days
    assert (df_clean["waiting_days"] < 0).sum() == 0, "Negative waiting days found in cleaned data!"

    # 3. Department standardization
    valid_departments = {
        "Cardiology", "Orthopedics", "Dermatology", "Neurology",
        "Pediatrics", "General Medicine", "ENT", "Ophthalmology"
    }
    actual_departments = set(df_clean["department"].unique())
    assert actual_departments.issubset(valid_departments), f"Unstandardized departments: {actual_departments - valid_departments}"

    # 4. Cardinality check: reminders did not multiply rows
    assert len(df_clean) == 5000, f"Expected exactly 5,000 cleaned records, got {len(df_clean)}"
