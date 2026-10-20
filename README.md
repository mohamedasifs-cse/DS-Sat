# Hospital Appointment Insight — CareBridge Hospitals
## DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491

**Author / Candidate:** Manojkumar S  
**Register Number:** U23AD491  
**Organization:** CareBridge Hospitals  
**Domain:** Healthcare Analytics & Outpatient Operations  
**Core Objective:** Understand Attendance Drivers. Reduce Missed Visits. Improve Clinic Scheduling.

---

### Project Overview & Architecture

Outpatient missed appointments ("no-shows") represent a major operational and financial challenge for hospital networks, resulting in idle clinical capacity, delayed patient treatments, and disrupted care coordination.

This project delivers an end-to-end, reproducible Data Science solution satisfying all three rounds of the DS Sprint assessment:
- **Round 1:** Relational Data Understanding, Preprocessing, Quality Auditing, and Exploratory Data Analysis.
- **Round 2:** Leakage-Free Temporal Feature Engineering, Supervised Machine Learning Modeling, and Model Selection.
- **Round 3:** Microsoft Excel Executive Analytics Workbook featuring formula-driven aggregation, Excel tables, conditional formatting, and inserted charts.

```
DS-SAT/
├── generate_dataset.py           # Reproducible synthetic dataset generator (Seed: 42)
├── run_pipeline.py               # Master single-command orchestration script
├── requirements.txt              # Project dependencies
├── README.md                     # Comprehensive documentation and setup guide
├── .gitignore                    # Standard exclusion rules
├── data/
│   ├── README.md                 # Data schema and synthetic data notice
│   ├── raw/                      # 5 relational source CSVs
│   │   ├── appointments.csv      # ~5,012 outpatient appointment records
│   │   ├── patients.csv          # 1,500 unique patient demographic records
│   │   ├── doctors.csv           # 30 physician specialties and schedules
│   │   ├── reminders.csv         # 4,278 reminder delivery logs
│   │   └── calendar.csv          # 366 full-year calendar records (2024)
│   └── processed/
│       └── cleaned_appointments.csv # 5,000 merged, validated appointment records
├── notebooks/
│   ├── 01_data_understanding_eda.ipynb # Executed Round 1 notebook
│   └── 02_feature_engineering_ml.ipynb # Executed Round 2 notebook
├── src/
│   ├── data_preprocessing.py     # Data cleaning, deduplication, auditing, and EDA
│   ├── feature_engineering.py    # Temporal and leakage-free point-in-time features
│   ├── train_model.py            # Preprocessing pipelines and model training
│   ├── evaluate_model.py         # Benchmarking, confusion matrix, feature importance
│   ├── excel_report.py           # OpenPyXL 10-sheet Excel workbook generator
│   └── create_notebooks.py       # Programmatic notebook builder
├── models/
│   └── no_show_model.joblib      # Serialized Champion model (Logistic Regression)
├── outputs/
│   ├── Hospital_Appointment_Insight.xlsx # 10-sheet Microsoft Excel deliverable
│   └── assessment_sheet_summary.txt      # Formatted summary ready for college assessment
├── reports/
│   ├── data_quality_report.csv   # Comprehensive audit across all raw attributes
│   ├── model_metrics.csv         # Test-set metrics (Accuracy, Precision, Recall, F1, AUC)
│   ├── model_evaluation.txt      # Clinical justification and diagnostic evaluation
│   ├── final_findings.md         # Comprehensive analytical report
│   ├── Excel_PivotTable_Instructions.md # Step-by-step native PivotTable instructions
│   └── figures/                  # 11 publication-grade visualizations
│       ├── appointment_status_distribution.png
│       ├── department_noshow_rate.png
│       ├── waiting_time_vs_noshow.png
│       ├── weekday_noshow_rate.png
│       ├── reminder_status_vs_attendance.png
│       ├── previous_noshow_vs_current.png
│       ├── age_group_attendance.png
│       ├── doctor_specialty_comparison.png
│       ├── monthly_seasonal_trends.png
│       ├── confusion_matrix.png
│       └── feature_importance.png
└── tests/
    ├── test_data_generation.py   # Raw dataset creation and schema validation tests
    ├── test_preprocessing.py     # Deduplication, date, and cardinality tests
    └── test_feature_engineering.py # Leakage prevention and mathematical consistency tests
```

---

### Synthetic Data Disclosure

All datasets in `data/raw/` were generated synthetically using a fixed random seed (`42`) solely for demonstration and academic evaluation. No real patient health information (PHI) is used.

The raw data intentionally includes real-world data quality anomalies for preprocessing practice:
1. **Missing appointment statuses:** 45 records tagged and excluded from supervised training to prevent target contamination.
2. **Duplicate bookings:** 12 duplicate bookings identified and removed.
3. **Inconsistent department casing:** Normalized to standard title case.
4. **Invalid waiting times:** 20 records with negative waiting times corrected to same-day bookings.
5. **Incomplete reminders:** Walk-in patients categorized as `'No Reminder Scheduled'`.

---

### Setup & Installation Instructions

#### 1. Environment Setup
Ensure Python 3.10+ is installed:
```bash
python --version
```

Clone or open the repository directory:
```bash
cd DS-SAT
```

#### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### Pipeline Execution

To run the complete data processing, model training, evaluation, and Excel report generation in a single command:
```bash
python run_pipeline.py
```

To run the automated test suite:
```bash
python -m pytest tests/
```

---

### Microsoft Excel Deliverable (`outputs/Hospital_Appointment_Insight.xlsx`)

The workbook contains 10 worksheets:

| Sheet # | Worksheet Title | Description & Features |
| :---: | :--- | :--- |
| **1** | **Summary Dashboard** | Executive KPI cards, 4 embedded Excel charts (Status, Department, Day, Reminder), Key Findings, and Strategic Recommendations. |
| **2** | **Cleaned Data** | 5,000 cleaned appointment records in an Excel Table (`CleanedAppointmentsTable`), frozen headers, auto-filters, and soft conditional formatting. |
| **3** | **Department Analysis** | Formula-driven summary table (`COUNTIF`, `COUNTIFS`, `IFERROR`) and department bar chart. |
| **4** | **Waiting-Time Analysis** | Lead-time brackets (`0 days`, `1–3 days`, `4–7 days`, `8–14 days`, `>14 days`) and column chart. |
| **5** | **Day-wise Attendance** | Calendar order analysis (Monday through Sunday) and day-wise attendance chart. |
| **6** | **Reminder Analysis** | Communication channel breakdown (SMS, Email, Phone Call) with association disclosure. |
| **7** | **Repeat No-shows** | Point-in-time patient recidivism history brackets (`0`, `1`, `2`, `3+` prior misses). |
| **8** | **Clinic Utilization** | Physician appointment load breakdown with capacity proxy disclosure. |
| **9** | **ML Model Results** | Supervised benchmarking table and model comparison chart using real test metrics. |
| **10** | **Final Summary** | Complete executive synthesis covering problem statement, methodology, metrics, and recommendations. |

*Note on PivotTables:* Comprehensive step-by-step instructions for creating native PivotTables and PivotCharts from `CleanedAppointmentsTable` are provided in [`reports/Excel_PivotTable_Instructions.md`](reports/Excel_PivotTable_Instructions.md).

---

### Machine Learning Benchmark & Results

Models were evaluated on a hold-out test set using a strict chronological split (80% train, 20% test) to prevent future-lookahead leakage:

| Model Pipeline | Accuracy | Precision (No-show) | Recall (No-show) | F1-Score (No-show) | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dummy Classifier (Baseline)** | 75.28% | 0.00% | 0.00% | 0.0000 | 0.5000 | Candidate |
| **Logistic Regression (Class-Balanced)** | **61.30%** | **33.06%** | **55.20%** | **0.4136** | **0.6212** | **Selected Champion** |
| **Random Forest Classifier** | 72.15% | 38.14% | 20.36% | 0.2655 | 0.6009 | Candidate |

**Champion Selection Rationale:**  
In clinical outpatient operations, unpredicted missed visits result in permanent loss of physician time. Although the Dummy baseline yields an apparent 75.28% accuracy by predicting "Attended" for all patients, its clinical utility is 0 (0% recall). **Logistic Regression with class balancing was selected as Champion** because it achieves **55.20% Recall** and the highest **F1-score (0.4136)**, identifying over half of upcoming missed visits for targeted outreach and managed overbooking.

---

### Strategic Recommendations for CareBridge Hospitals

1. **Automated Two-Tier Predictive Reminders:** Trigger conversational multi-channel (SMS + Phone) interactive confirmations at 7 days and 48 hours before appointments for patients identified as high risk (lead times >7 days or prior missed visits).
2. **Dynamic Algorithmic Double-Booking:** Implement controlled 1-slot overbooking for high-no-show clinics (General Medicine, Orthopedics) during peak risk hours (Monday mornings, Friday afternoons) when predicted risk exceeds 40%.
3. **One-Click Rescheduling Links:** Embed digital rescheduling links inside reminder messages, allowing patients to instantly rebook and release their slot to waitlisted individuals.

---

### GitHub Upload Instructions

To push this repository to GitHub:
```bash
git init
git add .
git commit -m "Complete Hospital Appointment Insight end-to-end Data Science project (U23AD491)"
git branch -M main
git remote add origin https://github.com/manojkumar-s/hospital-appointment-insight.git
git push -u origin main
```
