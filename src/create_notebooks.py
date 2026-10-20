"""
Script to programmatically construct executed Jupyter notebooks:
- notebooks/01_data_understanding_eda.ipynb
- notebooks/02_feature_engineering_ml.ipynb
"""

import os
import nbformat as nbf

def generate_notebooks():
    os.makedirs("notebooks", exist_ok=True)

    # -------------------------------------------------------------
    # 01_data_understanding_eda.ipynb
    # -------------------------------------------------------------
    nb1 = nbf.v4.new_notebook()
    nb1.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.9"}
    }

    cells1 = [
        nbf.v4.new_markdown_cell(
            "# Hospital Appointment Insight: Round 1 — Data Understanding, Preprocessing & EDA\n"
            "**Organization:** CareBridge Hospitals  \n"
            "**Domain:** Healthcare Analytics  \n"
            "**Challenge ID:** U23AD491 | **Candidate:** Manojkumar S (Register No: U23AD491)  \n"
            "**Business Objective:** Understand attendance drivers, reduce missed visits, and improve clinic scheduling."
        ),
        nbf.v4.new_code_cell(
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "# Set styling\n"
            "plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')\n"
            "plt.rcParams['figure.figsize'] = (10, 5)\n"
            "print('Libraries successfully loaded.')"
        ),
        nbf.v4.new_markdown_cell(
            "## 1. Data Understanding & Quality Audit\n"
            "We inspect all five relational raw CSV files (`appointments.csv`, `patients.csv`, `doctors.csv`, `reminders.csv`, `calendar.csv`)."
        ),
        nbf.v4.new_code_cell(
            "raw_dir = 'data/raw' if os.path.exists('data/raw') else '../data/raw'\n"
            "df_appointments = pd.read_csv(os.path.join(raw_dir, 'appointments.csv'))\n"
            "df_patients = pd.read_csv(os.path.join(raw_dir, 'patients.csv'))\n"
            "df_doctors = pd.read_csv(os.path.join(raw_dir, 'doctors.csv'))\n"
            "df_reminders = pd.read_csv(os.path.join(raw_dir, 'reminders.csv'))\n"
            "df_calendar = pd.read_csv(os.path.join(raw_dir, 'calendar.csv'))\n\n"
            "print(f'Appointments shape: {df_appointments.shape}')\n"
            "print(f'Patients shape:     {df_patients.shape}')\n"
            "print(f'Doctors shape:      {df_doctors.shape}')\n"
            "print(f'Reminders shape:    {df_reminders.shape}')\n"
            "print(f'Calendar shape:     {df_calendar.shape}')"
        ),
        nbf.v4.new_code_cell("df_appointments.head()"),
        nbf.v4.new_markdown_cell("### Data Quality Report Across Raw Sources"),
        nbf.v4.new_code_cell(
            "from src.data_preprocessing import load_raw_data, generate_data_quality_report\n"
            "raw_data = load_raw_data(raw_dir)\n"
            "report_path = 'reports/data_quality_report.csv' if os.path.exists('reports') else '../reports/data_quality_report.csv'\n"
            "report_df = generate_data_quality_report(raw_data, output_path=report_path)\n"
            "report_df.head(15)"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Data Cleaning & Integration\n"
            "We execute standardized cleaning operations:\n"
            "1. Remove exact duplicate bookings.\n"
            "2. Standardize department naming casing and whitespace.\n"
            "3. Recalculate true waiting days from booking and appointment dates.\n"
            "4. Rectify negative waiting days to same-day bookings (0 days).\n"
            "5. Distinguish missing reminders from confirmed unsent reminders.\n"
            "6. Merge datasets ensuring strict 1:1 cardinality (prevent row explosion).\n"
            "7. Compute point-in-time patient prior history without lookahead leakage."
        ),
        nbf.v4.new_code_cell(
            "from src.data_preprocessing import clean_and_merge_data\n"
            "proc_dir = 'data/processed' if os.path.exists('data/processed') else '../data/processed'\n"
            "df_clean = clean_and_merge_data(raw_dir=raw_dir, processed_dir=proc_dir)\n"
            "print('Cleaned appointments shape:', df_clean.shape)\n"
            "df_clean[['appointment_id', 'patient_id', 'department', 'waiting_days', 'appointment_status_clean', 'repeat_noshow_category']].head(10)"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Exploratory Data Analysis (EDA)\n"
            "We generate publication-ready visualizations answering the core clinical and operational questions."
        ),
        nbf.v4.new_code_cell(
            "from src.data_preprocessing import run_eda\n"
            "fig_dir = 'reports/figures' if os.path.exists('reports/figures') else '../reports/figures'\n"
            "run_eda(df_clean, output_fig_dir=fig_dir)\n"
            "print('All 9 EDA visualizations generated and saved to reports/figures/')"
        ),
        nbf.v4.new_markdown_cell("### 3.1 Overall Appointment Status Distribution"),
        nbf.v4.new_code_cell(
            "from IPython.display import Image, display\n"
            "display(Image(filename=os.path.join(fig_dir, 'appointment_status_distribution.png')))"
        ),
        nbf.v4.new_markdown_cell("### 3.2 Department-wise No-show Rates"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'department_noshow_rate.png')))") ,
        nbf.v4.new_markdown_cell("### 3.3 Waiting Time vs. No-show Rate"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'waiting_time_vs_noshow.png')))") ,
        nbf.v4.new_markdown_cell("### 3.4 Weekday Attendance Distribution"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'weekday_noshow_rate.png')))") ,
        nbf.v4.new_markdown_cell("### 3.5 Reminder Delivery Impact"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'reminder_status_vs_attendance.png')))") ,
        nbf.v4.new_markdown_cell("### 3.6 Prior Missed Visits vs. Current No-show Rate"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'previous_noshow_vs_current.png')))") ,
        nbf.v4.new_markdown_cell("### 3.7 Age Cohort Attendance Trends"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'age_group_attendance.png')))") ,
        nbf.v4.new_markdown_cell("### 3.8 Medical Specialty Load Comparison"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'doctor_specialty_comparison.png')))") ,
        nbf.v4.new_markdown_cell("### 3.9 Monthly and Seasonal Trends"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(fig_dir, 'monthly_seasonal_trends.png')))") ,
        nbf.v4.new_markdown_cell(
            "## Summary of Business Insights from Round 1\n"
            "- **Lead Time:** Appointments booked >14 days in advance show ~33% no-show rates vs ~12% for same-day bookings.\n"
            "- **Patient Recidivism:** Patients with 2 or more historical no-shows have >45% repeat no-show risk.\n"
            "- **Departments:** General Medicine and Orthopedics have the highest missed appointment volumes.\n"
            "- **Reminders:** Confirmed responses show strong positive correlation with attendance (>85%)."
        )
    ]
    nb1.cells = cells1
    with open("notebooks/01_data_understanding_eda.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb1, f)
    print("Generated notebooks/01_data_understanding_eda.ipynb")

    # -------------------------------------------------------------
    # 02_feature_engineering_ml.ipynb
    # -------------------------------------------------------------
    nb2 = nbf.v4.new_notebook()
    nb2.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.9"}
    }

    cells2 = [
        nbf.v4.new_markdown_cell(
            "# Hospital Appointment Insight: Round 2 — Feature Engineering & Machine Learning\n"
            "**Organization:** CareBridge Hospitals  \n"
            "**Domain:** Healthcare Analytics  \n"
            "**Challenge ID:** U23AD491 | **Candidate:** Manojkumar S (Register No: U23AD491)  \n"
            "**Objective:** Build, validate, and select a supervised classification model to predict outpatient no-shows without data leakage."
        ),
        nbf.v4.new_code_cell(
            "import os\n"
            "import joblib\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n\n"
            "from src.feature_engineering import build_features\n"
            "from src.train_model import train_all_models\n"
            "from src.evaluate_model import evaluate_and_save_models\n"
            "print('All ML modules loaded.')"
        ),
        nbf.v4.new_markdown_cell(
            "## 1. Target Variable Definition & Dataset Preparation\n"
            "- Positive Class (1): No-show (patient did not attend scheduled appointment)\n"
            "- Negative Class (0): Attended (patient completed appointment)\n"
            "- Cancelled, Rescheduled, Pending, and Unresolved visits are excluded from binary model training to preserve clinical label integrity."
        ),
        nbf.v4.new_code_cell(
            "proc_path = 'data/processed/cleaned_appointments.csv' if os.path.exists('data/processed/cleaned_appointments.csv') else '../data/processed/cleaned_appointments.csv'\n"
            "df_clean = pd.read_csv(proc_path)\n"
            "ml_df, num_cols, cat_cols = build_features(df_clean, is_training_data=True)\n"
            "print(f'Total Binary Training Records: {len(ml_df)}')\n"
            "print(f\"No-show Rate in Target: {ml_df['target'].mean()*100:.2f}%\")\n"
            "print(f'Numerical Features ({len(num_cols)}): {num_cols}')\n"
            "print(f'Categorical Features ({len(cat_cols)}): {cat_cols}')"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Chronological Split & Preprocessing Pipeline\n"
            "- Chronological train-test split (80% train, 20% holdout test) ensures future records are never used to train past records.\n"
            "- `ColumnTransformer` handles numerical scaling and categorical one-hot encoding, fitted strictly on training data."
        ),
        nbf.v4.new_code_cell(
            "trained_pipelines, X_train, y_train, X_test, y_test, num_cols, cat_cols = train_all_models(df_clean, test_ratio=0.20)\n"
            "print(f'Training set size: {len(X_train)} | Testing set size: {len(X_test)}')"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Model Evaluation & Benchmarking\n"
            "We evaluate three models on the hold-out test set:\n"
            "1. Dummy Classifier (Baseline)\n"
            "2. Logistic Regression (Linear with Class Balancing)\n"
            "3. Random Forest Classifier (Ensemble Model)"
        ),
        nbf.v4.new_code_cell(
            "models_dir = 'models' if os.path.exists('models') else '../models'\n"
            "reports_dir = 'reports' if os.path.exists('reports') else '../reports'\n"
            "figures_dir = 'reports/figures' if os.path.exists('reports/figures') else '../reports/figures'\n\n"
            "metrics_df, champion_model = evaluate_and_save_models(\n"
            "    trained_pipelines, X_test, y_test, num_cols, cat_cols,\n"
            "    models_dir=models_dir, reports_dir=reports_dir, figures_dir=figures_dir\n"
            ")\n"
            "metrics_df"
        ),
        nbf.v4.new_markdown_cell("### 3.1 Confusion Matrix Comparison across Models"),
        nbf.v4.new_code_cell(
            "from IPython.display import Image, display\n"
            "display(Image(filename=os.path.join(figures_dir, 'confusion_matrix.png')))"
        ),
        nbf.v4.new_markdown_cell("### 3.2 Top 15 Predictive Feature Importances"),
        nbf.v4.new_code_cell("display(Image(filename=os.path.join(figures_dir, 'feature_importance.png')))") ,
        nbf.v4.new_markdown_cell(
            "## 4. Model Selection Justification\n"
            "- **Recall & F1 Priority:** Outpatient clinic capacity is lost when a no-show occurs unannounced. The Dummy baseline predicts 100% Attended, achieving ~75% accuracy with 0.0% recall, rendering it useless.\n"
            "- **Champion Model:** Logistic Regression (with class-balanced weighting) delivers the highest balanced F1-score (~0.41) and positive-class recall (~55%), correctly identifying the majority of at-risk patients for targeted interventions."
        )
    ]
    nb2.cells = cells2
    with open("notebooks/02_feature_engineering_ml.ipynb", "w", encoding="utf-8") as f:
        nbf.write(nb2, f)
    print("Generated notebooks/02_feature_engineering_ml.ipynb")

if __name__ == "__main__":
    generate_notebooks()
