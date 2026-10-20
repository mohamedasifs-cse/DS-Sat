"""
Data Preprocessing and Exploratory Data Analysis Module
CareBridge Hospitals - Hospital Appointment Insight (Challenge ID: U23AD491)

Includes:
- Data quality auditing and reporting across raw datasets
- Data cleaning: deduplication, schema standardization, date verification, waiting days correction
- Robust merging with cardinality validation (preventing row multiplication)
- Exploratory Data Analysis (EDA) figure generation
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication-quality plotting styles
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Helvetica"]
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

def load_raw_data(raw_dir="data/raw"):
    """Loads all five raw CSV files into a dictionary of DataFrames."""
    datasets = {
        "appointments": pd.read_csv(os.path.join(raw_dir, "appointments.csv")),
        "patients": pd.read_csv(os.path.join(raw_dir, "patients.csv")),
        "doctors": pd.read_csv(os.path.join(raw_dir, "doctors.csv")),
        "reminders": pd.read_csv(os.path.join(raw_dir, "reminders.csv")),
        "calendar": pd.read_csv(os.path.join(raw_dir, "calendar.csv"))
    }
    return datasets

def generate_data_quality_report(datasets, output_path="reports/data_quality_report.csv"):
    """
    Analyzes all raw datasets and outputs an audit table detailing:
    - Dataset name, row count, column count
    - Column name, data type, missing count, missing percentage
    - Number of unique values, duplicate rows count
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    report_rows = []

    for name, df in datasets.items():
        n_rows, n_cols = df.shape
        n_dups = df.duplicated().sum()

        for col in df.columns:
            n_missing = df[col].isna().sum()
            pct_missing = round((n_missing / n_rows) * 100, 2)
            n_unique = df[col].nunique()
            dtype = str(df[col].dtype)
            
            sample_vals = df[col].dropna().unique()[:3]
            sample_str = ", ".join(map(str, sample_vals))

            report_rows.append({
                "dataset": name,
                "total_rows": n_rows,
                "total_columns": n_cols,
                "duplicate_rows": n_dups,
                "column_name": col,
                "data_type": dtype,
                "missing_count": n_missing,
                "missing_percentage": pct_missing,
                "unique_values_count": n_unique,
                "sample_values": sample_str
            })

    report_df = pd.DataFrame(report_rows)
    report_df.to_csv(output_path, index=False)
    print(f"Data Quality Report successfully written to: {output_path}")
    return report_df

def clean_and_merge_data(raw_dir="data/raw", processed_dir="data/processed"):
    """
    Cleans all raw datasets and merges them into a unified, appointment-level analytical table.
    
    Cleaning steps:
    1. Removes exact duplicate appointment records.
    2. Standardizes department names (title case, strip whitespace).
    3. Re-computes and corrects waiting_days from booking_date and appointment_date.
    4. Handles negative/invalid waiting times.
    5. Categorizes missing reminders distinctly from confirmed unsent reminders.
    6. Ensures strict 1-to-1 cardinality when merging reminders to prevent row explosion.
    7. Retains appointment statuses while isolating missing/unresolved records.
    8. Validates patient age and relationships.
    """
    os.makedirs(processed_dir, exist_ok=True)
    datasets = load_raw_data(raw_dir)
    
    df_app = datasets["appointments"].copy()
    df_pat = datasets["patients"].copy()
    df_doc = datasets["doctors"].copy()
    df_rem = datasets["reminders"].copy()
    df_cal = datasets["calendar"].copy()

    initial_app_count = len(df_app)
    print(f"\n[Data Cleaning] Starting raw appointment records: {initial_app_count}")

    # 1. Deduplication
    dup_count = df_app.duplicated().sum()
    df_app = df_app.drop_duplicates().reset_index(drop=True)
    print(f"  - Identified and dropped {dup_count} exact duplicate appointment records. Remaining: {len(df_app)}")

    # 2. Standardize Department Names
    df_app["department"] = df_app["department"].astype(str).str.strip().str.title()
    # Normalize special acronyms
    df_app["department"] = df_app["department"].replace({
        "Ent": "ENT",
        "E.N.T.": "ENT",
        "General medicine": "General Medicine"
    })
    df_doc["specialty"] = df_doc["specialty"].astype(str).str.strip().str.title().replace({"Ent": "ENT"})

    # 3. Date Validation and Waiting Days Recalculation
    df_app["appointment_date"] = pd.to_datetime(df_app["appointment_date"])
    df_app["booking_date"] = pd.to_datetime(df_app["booking_date"])
    
    # Recalculate true waiting days from dates
    recalculated_wait = (df_app["appointment_date"] - df_app["booking_date"]).dt.days
    
    # Identify invalid/negative waiting days
    invalid_mask = recalculated_wait < 0
    num_invalid = invalid_mask.sum()
    if num_invalid > 0:
        print(f"  - Detected {num_invalid} records with negative waiting days (booking after appointment).")
        # Correct them: set booking_date to appointment_date (same-day booking), waiting_days = 0
        df_app.loc[invalid_mask, "booking_date"] = df_app.loc[invalid_mask, "appointment_date"]
        recalculated_wait = (df_app["appointment_date"] - df_app["booking_date"]).dt.days

    df_app["waiting_days"] = recalculated_wait.astype(int)

    # Convert back to standard string format YYYY-MM-DD
    df_app["appointment_date"] = df_app["appointment_date"].dt.strftime("%Y-%m-%d")
    df_app["booking_date"] = df_app["booking_date"].dt.strftime("%Y-%m-%d")

    # 4. Standardize Appointment Status
    # Unresolved or missing statuses are tagged as 'Unresolved' for tracking
    df_app["status_is_missing"] = df_app["appointment_status"].isna()
    df_app["appointment_status_clean"] = df_app["appointment_status"].fillna("Unresolved")

    # 5. Clean Reminders and Validate Cardinality
    # Deduplicate reminders by appointment_id if multiple exist (keep first/latest)
    rem_dup = df_rem.duplicated(subset=["appointment_id"]).sum()
    if rem_dup > 0:
        print(f"  - Found {rem_dup} duplicate reminder records for appointment IDs. Deduplicating.")
        df_rem = df_rem.drop_duplicates(subset=["appointment_id"], keep="last")

    # 6. Merging Datasets
    # A. Merge with Patients
    merged = df_app.merge(df_pat, on="patient_id", how="left")

    # B. Merge with Doctors
    merged = merged.merge(df_doc, on="doctor_id", how="left")

    # C. Merge with Reminders (Left join, validating 1:1 row count)
    before_rem_len = len(merged)
    merged = merged.merge(
        df_rem[["appointment_id", "reminder_type", "reminder_sent", "reminder_response"]],
        on="appointment_id",
        how="left"
    )
    assert len(merged) == before_rem_len, "Cardinality error: Reminders caused row multiplication!"

    # Handle missing reminders vs unsent reminders
    merged["reminder_type"] = merged["reminder_type"].fillna("No Reminder Scheduled")
    merged["reminder_sent"] = merged["reminder_sent"].fillna("Not Scheduled")
    merged["reminder_response"] = merged["reminder_response"].fillna("No Response Recorded")

    # D. Merge with Calendar
    df_cal["date"] = df_cal["date"].astype(str)
    merged = merged.merge(df_cal, left_on="appointment_date", right_on="date", how="left")
    if "date" in merged.columns:
        merged.drop(columns=["date"], inplace=True)

    # 7. Add Waiting Time Category Bin for Analysis
    def categorize_wait(days):
        if days == 0:
            return "0 days"
        elif 1 <= days <= 3:
            return "1–3 days"
        elif 4 <= days <= 7:
            return "4–7 days"
        elif 8 <= days <= 14:
            return "8–14 days"
        else:
            return "More than 14 days"

    merged["waiting_time_group"] = merged["waiting_days"].apply(categorize_wait)

    # 8. Add Point-in-Time Patient Historical Columns (Strictly Before Current Appointment)
    merged["dt_combined"] = pd.to_datetime(merged["appointment_date"] + " " + merged["appointment_time"])
    merged = merged.sort_values(by=["patient_id", "dt_combined"]).reset_index(drop=True)

    merged["prior_noshow_count"] = merged.groupby("patient_id")["appointment_status_clean"].transform(
        lambda s: (s == "No-show").cumsum().shift(1).fillna(0)
    ).astype(int)

    merged["prior_attended_count"] = merged.groupby("patient_id")["appointment_status_clean"].transform(
        lambda s: (s == "Attended").cumsum().shift(1).fillna(0)
    ).astype(int)

    merged["prior_appointments_count"] = merged["prior_noshow_count"] + merged["prior_attended_count"]

    merged["prior_noshow_rate"] = np.where(
        merged["prior_appointments_count"] > 0,
        merged["prior_noshow_count"] / merged["prior_appointments_count"],
        0.0
    )

    def categorize_prior_noshows(n):
        if n == 0:
            return "0 Prior Misses"
        elif n == 1:
            return "1 Prior Miss"
        elif n == 2:
            return "2 Prior Misses"
        else:
            return "3+ Prior Misses"

    merged["repeat_noshow_category"] = merged["prior_noshow_count"].apply(categorize_prior_noshows)

    # Re-sort to chronological appointment order
    merged = merged.sort_values(by=["dt_combined", "appointment_id"]).reset_index(drop=True)
    merged.drop(columns=["dt_combined"], inplace=True)

    final_count = len(merged)
    print(f"[Data Cleaning] Final merged appointment records: {final_count}")
    print(f"  - Missing status records preserved as 'Unresolved': {merged['status_is_missing'].sum()}")

    output_path = os.path.join(processed_dir, "cleaned_appointments.csv")
    merged.to_csv(output_path, index=False)
    print(f"Cleaned dataset saved to: {output_path}")

    return merged

def run_eda(df, output_fig_dir="reports/figures"):
    """
    Generates all 9 required exploratory analysis visualizations and saves them to reports/figures/.
    Focuses on resolved appointments (Attended vs No-show) for rate calculations.
    """
    os.makedirs(output_fig_dir, exist_ok=True)
    print("\n[EDA] Generating Exploratory Data Analysis Figures...")

    # Filter for resolved appointments for no-show rate analyses
    df_resolved = df[df["appointment_status_clean"].isin(["Attended", "No-show"])].copy()
    df_resolved["is_noshow"] = (df_resolved["appointment_status_clean"] == "No-show").astype(int)

    # -------------------------------------------------------------
    # Chart 1: Appointment Status Distribution (All records)
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    status_counts = df["appointment_status_clean"].value_counts()
    colors = ["#2b5c8f", "#d9534f", "#f0ad4e", "#5bc0de", "#777777", "#b0b0b0"]
    bars = plt.bar(status_counts.index, status_counts.values, color=colors[:len(status_counts)], edgecolor="#333333", alpha=0.9)
    plt.title("Figure 1: Overall Appointment Status Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Appointment Status", fontsize=11, labelpad=8)
    plt.ylabel("Number of Appointments", fontsize=11, labelpad=8)
    
    total = len(df)
    for bar in bars:
        h = bar.get_height()
        pct = (h / total) * 100
        plt.annotate(f"{h:,}\n({pct:.1f}%)",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="semibold")
    
    plt.ylim(0, max(status_counts.values) * 1.15)
    plt.tight_layout()
    p1 = os.path.join(output_fig_dir, "appointment_status_distribution.png")
    plt.savefig(p1, dpi=300)
    plt.close()
    print(f"  - Saved: {p1}")

    # -------------------------------------------------------------
    # Chart 2: Department-wise No-show Rates
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    dept_stats = df_resolved.groupby("department")["is_noshow"].agg(["count", "mean"]).reset_index()
    dept_stats["noshow_rate_pct"] = dept_stats["mean"] * 100
    dept_stats = dept_stats.sort_values(by="noshow_rate_pct", ascending=False)

    palette = sns.color_palette("Blues_r", len(dept_stats))
    bars = plt.bar(dept_stats["department"], dept_stats["noshow_rate_pct"], color=palette, edgecolor="#333333")
    plt.title("Figure 2: No-show Rate by Medical Department", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Department", fontsize=11, labelpad=8)
    plt.ylabel("No-show Rate (%)", fontsize=11, labelpad=8)
    plt.xticks(rotation=25, ha="right")

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.ylim(0, max(dept_stats["noshow_rate_pct"]) * 1.2)
    plt.tight_layout()
    p2 = os.path.join(output_fig_dir, "department_noshow_rate.png")
    plt.savefig(p2, dpi=300)
    plt.close()
    print(f"  - Saved: {p2}")

    # -------------------------------------------------------------
    # Chart 3: Waiting-Time Groups vs No-show Rates
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    wait_order = ["0 days", "1–3 days", "4–7 days", "8–14 days", "More than 14 days"]
    wait_stats = df_resolved.groupby("waiting_time_group")["is_noshow"].agg(["count", "mean"]).reindex(wait_order).reset_index()
    wait_stats["noshow_rate_pct"] = wait_stats["mean"] * 100

    bars = plt.bar(wait_stats["waiting_time_group"], wait_stats["noshow_rate_pct"], color="#3470a3", edgecolor="#222222")
    plt.plot(wait_stats["waiting_time_group"], wait_stats["noshow_rate_pct"], color="#d9534f", marker="o", linewidth=2.5, markersize=8)
    plt.title("Figure 3: Impact of Booking Lead Time on No-show Rates", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Waiting Time Window", fontsize=11, labelpad=8)
    plt.ylabel("No-show Rate (%)", fontsize=11, labelpad=8)

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 6), textcoords="offset points",
                     ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.ylim(0, max(wait_stats["noshow_rate_pct"]) * 1.25)
    plt.tight_layout()
    p3 = os.path.join(output_fig_dir, "waiting_time_vs_noshow.png")
    plt.savefig(p3, dpi=300)
    plt.close()
    print(f"  - Saved: {p3}")

    # -------------------------------------------------------------
    # Chart 4: Weekday-wise No-show Rates
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    day_stats = df_resolved.groupby("weekday")["is_noshow"].agg(["count", "mean"]).reindex(day_order).dropna().reset_index()
    day_stats["noshow_rate_pct"] = day_stats["mean"] * 100

    bars = plt.bar(day_stats["weekday"], day_stats["noshow_rate_pct"], color="#2f5597", edgecolor="#111111")
    plt.title("Figure 4: No-show Rate Variation Across Weekdays", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Appointment Weekday", fontsize=11, labelpad=8)
    plt.ylabel("No-show Rate (%)", fontsize=11, labelpad=8)

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.ylim(0, max(day_stats["noshow_rate_pct"]) * 1.25)
    plt.tight_layout()
    p4 = os.path.join(output_fig_dir, "weekday_noshow_rate.png")
    plt.savefig(p4, dpi=300)
    plt.close()
    print(f"  - Saved: {p4}")

    # -------------------------------------------------------------
    # Chart 5: Reminder Status vs Attendance
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    rem_stats = df_resolved.groupby("reminder_sent")["is_noshow"].agg(["count", "mean"]).reset_index()
    rem_stats["noshow_rate_pct"] = rem_stats["mean"] * 100
    rem_stats["attendance_rate_pct"] = 100 - rem_stats["noshow_rate_pct"]

    x = np.arange(len(rem_stats))
    width = 0.35

    plt.bar(x - width/2, rem_stats["attendance_rate_pct"], width, label="Attended (%)", color="#28a745", edgecolor="#222")
    plt.bar(x + width/2, rem_stats["noshow_rate_pct"], width, label="No-show (%)", color="#dc3545", edgecolor="#222")
    
    plt.title("Figure 5: Attendance vs No-show Rate Across Reminder Status", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Reminder Dispatch Status", fontsize=11, labelpad=8)
    plt.ylabel("Percentage (%)", fontsize=11, labelpad=8)
    plt.xticks(x, rem_stats["reminder_sent"])
    plt.legend(frameon=True, facecolor="#ffffff")

    for i in range(len(rem_stats)):
        att = rem_stats.loc[i, "attendance_rate_pct"]
        ns = rem_stats.loc[i, "noshow_rate_pct"]
        plt.annotate(f"{att:.1f}%", xy=(x[i] - width/2, att), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold")
        plt.annotate(f"{ns:.1f}%", xy=(x[i] + width/2, ns), xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9, fontweight="bold")

    plt.ylim(0, 115)
    plt.tight_layout()
    p5 = os.path.join(output_fig_dir, "reminder_status_vs_attendance.png")
    plt.savefig(p5, dpi=300)
    plt.close()
    print(f"  - Saved: {p5}")

    # -------------------------------------------------------------
    # Chart 6: Previous No-show History vs Current No-show Rate
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    # Bin prior no-shows into 0, 1, 2, 3+
    def bin_prior(n):
        if n == 0:
            return "0 Prior Misses"
        elif n == 1:
            return "1 Prior Miss"
        elif n == 2:
            return "2 Prior Misses"
        else:
            return "3+ Prior Misses"
            
    df_resolved["prior_noshow_bin"] = df_resolved["previous_no_shows"].apply(bin_prior)
    hist_order = ["0 Prior Misses", "1 Prior Miss", "2 Prior Misses", "3+ Prior Misses"]
    hist_stats = df_resolved.groupby("prior_noshow_bin")["is_noshow"].agg(["count", "mean"]).reindex(hist_order).dropna().reset_index()
    hist_stats["noshow_rate_pct"] = hist_stats["mean"] * 100

    bars = plt.bar(hist_stats["prior_noshow_bin"], hist_stats["noshow_rate_pct"], color="#b23b3b", edgecolor="#222")
    plt.title("Figure 6: Patient Attendance by Historical No-show Frequency", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Prior Missed Appointments (Patient History)", fontsize=11, labelpad=8)
    plt.ylabel("Current Appointment No-show Rate (%)", fontsize=11, labelpad=8)

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.ylim(0, max(hist_stats["noshow_rate_pct"]) * 1.25)
    plt.tight_layout()
    p6 = os.path.join(output_fig_dir, "previous_noshow_vs_current.png")
    plt.savefig(p6, dpi=300)
    plt.close()
    print(f"  - Saved: {p6}")

    # -------------------------------------------------------------
    # Chart 7: Age-Group-wise Attendance
    # -------------------------------------------------------------
    plt.figure(figsize=(9, 5))
    age_order = ["Pediatric (0-17)", "Young Adult (18-35)", "Middle-Aged (36-55)", "Senior (56+)"]
    age_stats = df_resolved.groupby("age_group")["is_noshow"].agg(["count", "mean"]).reindex(age_order).dropna().reset_index()
    age_stats["noshow_rate_pct"] = age_stats["mean"] * 100

    bars = plt.bar(age_stats["age_group"], age_stats["noshow_rate_pct"], color="#4a7c59", edgecolor="#222")
    plt.title("Figure 7: Appointment No-show Rate Across Patient Age Cohorts", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Patient Age Bracket", fontsize=11, labelpad=8)
    plt.ylabel("No-show Rate (%)", fontsize=11, labelpad=8)

    for bar in bars:
        h = bar.get_height()
        plt.annotate(f"{h:.1f}%",
                     xy=(bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.ylim(0, max(age_stats["noshow_rate_pct"]) * 1.25)
    plt.tight_layout()
    p7 = os.path.join(output_fig_dir, "age_group_attendance.png")
    plt.savefig(p7, dpi=300)
    plt.close()
    print(f"  - Saved: {p7}")

    # -------------------------------------------------------------
    # Chart 8: Doctor Specialty Comparison
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    spec_stats = df_resolved.groupby("specialty")["is_noshow"].agg(["count", "mean"]).reset_index()
    spec_stats["noshow_rate_pct"] = spec_stats["mean"] * 100
    spec_stats = spec_stats.sort_values(by="count", ascending=True)

    y_pos = np.arange(len(spec_stats))
    plt.barh(y_pos, spec_stats["count"], color="#6c757d", edgecolor="#222")
    plt.yticks(y_pos, spec_stats["specialty"])
    plt.title("Figure 8: Total Appointments by Medical Specialty", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Appointment Volume", fontsize=11, labelpad=8)
    plt.ylabel("Specialty", fontsize=11, labelpad=8)

    for i, v in enumerate(spec_stats["count"]):
        plt.text(v + 10, i, f"{v:,}", va="center", fontsize=9, fontweight="semibold")

    plt.xlim(0, max(spec_stats["count"]) * 1.15)
    plt.tight_layout()
    p8 = os.path.join(output_fig_dir, "doctor_specialty_comparison.png")
    plt.savefig(p8, dpi=300)
    plt.close()
    print(f"  - Saved: {p8}")

    # -------------------------------------------------------------
    # Chart 9: Monthly and Seasonal Appointment Trends
    # -------------------------------------------------------------
    plt.figure(figsize=(10, 5))
    month_order = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    month_stats = df_resolved.groupby("month")["is_noshow"].agg(["count", "mean"]).reindex(month_order).dropna().reset_index()
    month_stats["noshow_rate_pct"] = month_stats["mean"] * 100

    ax1 = plt.gca()
    ax2 = ax1.twinx()

    b = ax1.bar(month_stats["month"], month_stats["count"], alpha=0.35, color="#17a2b8", label="Appointment Volume")
    l = ax2.plot(month_stats["month"], month_stats["noshow_rate_pct"], color="#c82333", marker="s", linewidth=2.5, label="No-show Rate (%)")

    ax1.set_title("Figure 9: Monthly Appointment Volume and No-show Trends (2024)", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xlabel("Month", fontsize=11, labelpad=8)
    ax1.set_ylabel("Appointment Volume", fontsize=11, color="#0c5460", labelpad=8)
    ax2.set_ylabel("No-show Rate (%)", fontsize=11, color="#c82333", labelpad=8)
    ax1.tick_params(axis="x", rotation=30)
    ax2.grid(False)

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc="upper right", frameon=True)

    plt.tight_layout()
    p9 = os.path.join(output_fig_dir, "monthly_seasonal_trends.png")
    plt.savefig(p9, dpi=300)
    plt.close()
    print(f"  - Saved: {p9}")
    print("[EDA] All 9 charts successfully generated.")

if __name__ == "__main__":
    datasets = load_raw_data()
    generate_data_quality_report(datasets)
    cleaned_df = clean_and_merge_data()
    run_eda(cleaned_df)
