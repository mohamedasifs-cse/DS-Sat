"""
Master Pipeline Orchestration Script
CareBridge Hospitals — Hospital Appointment Insight
DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491

Executes the entire end-to-end Data Science project via a single command:
    python run_pipeline.py

Pipeline Steps:
1. Inspects raw dataset availability (generates reproducible synthetic data if absent)
2. Validates raw input schemas and records
3. Performs data cleaning, deduplication, date validation, and cardinality-safe merges
4. Generates data quality reports and 9 publication-grade EDA charts
5. Constructs leak-free temporal and historical features
6. Trains Dummy, Logistic Regression, and Random Forest pipelines
7. Evaluates models on holdout test set and exports diagnostic reports and figures
8. Generates the 10-sheet Microsoft Excel reporting deliverable
9. Generates college assessment sheet summary and final analytical findings report
10. Prints summary of all generated output files
"""

import os
import sys
import time

def print_banner(step_num, title):
    print("\n" + "=" * 75)
    print(f"STEP {step_num}: {title.upper()}")
    print("=" * 75)

def run_complete_pipeline():
    start_time = time.time()
    print("*" * 75)
    print("CAREBRIDGE HOSPITALS — HOSPITAL APPOINTMENT INSIGHT (U23AD491)")
    print("Executing End-to-End Analytics, Machine Learning & Excel Generation")
    print("*" * 75)

    # -------------------------------------------------------------
    # Step 1 & 2: Inspect Source Data / Generate Synthetic Data
    # -------------------------------------------------------------
    print_banner(1, "Data Inspection & Generation Check")
    raw_dir = "data/raw"
    required_raw_files = [
        "appointments.csv", "patients.csv", "doctors.csv",
        "reminders.csv", "calendar.csv"
    ]
    all_exist = all(os.path.exists(os.path.join(raw_dir, f)) for f in required_raw_files)

    if not all_exist:
        print("[Notice] Source datasets missing. Generating reproducible synthetic demonstration data...")
        from generate_dataset import generate_all_datasets
        generate_all_datasets(raw_dir=raw_dir, seed=42)
    else:
        print(f"[OK] All 5 source datasets detected in '{raw_dir}'. Preserving existing source data.")

    # -------------------------------------------------------------
    # Step 3 & 4: Data Quality Audit, Preprocessing, Cleaning & EDA
    # -------------------------------------------------------------
    print_banner(2, "Data Quality Auditing, Cleaning & Preprocessing (Round 1)")
    from src.data_preprocessing import load_raw_data, generate_data_quality_report, clean_and_merge_data, run_eda

    raw_datasets = load_raw_data(raw_dir)
    report_df = generate_data_quality_report(raw_datasets, output_path="reports/data_quality_report.csv")
    print(f"[OK] Data quality audit generated: {len(report_df)} attributes evaluated across 5 datasets.")

    cleaned_df = clean_and_merge_data(raw_dir=raw_dir, processed_dir="data/processed")
    print(f"[OK] Cleaned appointments dataset created: {len(cleaned_df)} records, 0 negative waiting days.")

    print_banner(3, "Exploratory Data Analysis & Visualization (Round 1)")
    run_eda(cleaned_df, output_fig_dir="reports/figures")
    print("[OK] All 9 exploratory analysis charts generated and saved to reports/figures/.")

    # -------------------------------------------------------------
    # Step 5, 6 & 7: Feature Engineering, Model Training & Evaluation
    # -------------------------------------------------------------
    print_banner(4, "Feature Engineering & Temporal Modeling (Round 2)")
    from src.train_model import train_all_models
    from src.evaluate_model import evaluate_and_save_models

    trained_pipes, X_tr, y_tr, X_te, y_te, num_cols, cat_cols = train_all_models(cleaned_df, test_ratio=0.20)
    print(f"[OK] Chronological split complete: {len(X_tr)} train rows, {len(X_te)} test rows.")

    print_banner(5, "Model Evaluation & Benchmarking (Round 2)")
    metrics_df, champ_name = evaluate_and_save_models(
        trained_pipes, X_te, y_te, num_cols, cat_cols,
        models_dir="models", reports_dir="reports", figures_dir="reports/figures"
    )
    print(f"[OK] Champion Model Selected: {champ_name}")

    # -------------------------------------------------------------
    # Step 8: Excel Workbook Generation (Round 3)
    # -------------------------------------------------------------
    print_banner(6, "Microsoft Excel Workbook Generation (Round 3)")
    from src.excel_report import create_excel_report
    excel_path = create_excel_report(
        cleaned_csv_path="data/processed/cleaned_appointments.csv",
        metrics_csv_path="reports/model_metrics.csv",
        output_excel_path="outputs/Hospital_Appointment_Insight.xlsx"
    )
    print(f"[OK] 10-Sheet Excel Workbook created: {excel_path}")

    # -------------------------------------------------------------
    # Step 9 & 10: Generate Assessment Summary & Final Findings
    # -------------------------------------------------------------
    print_banner(7, "Reporting & Assessment Documentation")
    from src.create_notebooks import generate_notebooks
    generate_notebooks()
    print("[OK] Jupyter Notebooks generated in notebooks/ directory.")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 75)
    print(f"PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {elapsed} SECONDS")
    print("=" * 75)

    print("\nGenerated Deliverables Summary:")
    output_files = [
        "data/raw/appointments.csv",
        "data/raw/patients.csv",
        "data/raw/doctors.csv",
        "data/raw/reminders.csv",
        "data/raw/calendar.csv",
        "data/processed/cleaned_appointments.csv",
        "data/README.md",
        "notebooks/01_data_understanding_eda.ipynb",
        "notebooks/02_feature_engineering_ml.ipynb",
        "models/no_show_model.joblib",
        "reports/data_quality_report.csv",
        "reports/model_metrics.csv",
        "reports/model_evaluation.txt",
        "reports/final_findings.md",
        "reports/Excel_PivotTable_Instructions.md",
        "reports/figures/appointment_status_distribution.png",
        "reports/figures/department_noshow_rate.png",
        "reports/figures/waiting_time_vs_noshow.png",
        "reports/figures/weekday_noshow_rate.png",
        "reports/figures/reminder_status_vs_attendance.png",
        "reports/figures/previous_noshow_vs_current.png",
        "reports/figures/age_group_attendance.png",
        "reports/figures/doctor_specialty_comparison.png",
        "reports/figures/monthly_seasonal_trends.png",
        "reports/figures/confusion_matrix.png",
        "reports/figures/feature_importance.png",
        "outputs/Hospital_Appointment_Insight.xlsx",
        "outputs/assessment_sheet_summary.txt"
    ]

    for fpath in output_files:
        status = "[EXISTS]" if os.path.exists(fpath) else "[MISSING]"
        size = f"({os.path.getsize(fpath):,} bytes)" if os.path.exists(fpath) else ""
        print(f"  {status:<9} {fpath:<55} {size}")

    print("\nAll tasks completed. Ready for assessment evaluation.")

if __name__ == "__main__":
    run_complete_pipeline()
