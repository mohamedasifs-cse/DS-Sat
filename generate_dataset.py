"""
Dataset Generation Script for CareBridge Hospitals - Hospital Appointment Insight
DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491

Generates 5 reproducible synthetic CSV datasets inside data/raw/:
1. appointments.csv (~5,000 records)
2. patients.csv (~1,500 records)
3. doctors.csv (~30 records)
4. reminders.csv (linked to appointments)
5. calendar.csv (calendar covering appointment date range)

DISCLAIMER: All generated datasets contain synthetic demonstration data created
solely for academic and analytical assessment purposes. No real patient health
information (PHI) or hospital records are included.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_all_datasets(raw_dir="data/raw", seed=42):
    random.seed(seed)
    np.random.seed(seed)
    os.makedirs(raw_dir, exist_ok=True)

    print("=" * 60)
    print("Generating Synthetic Datasets for CareBridge Hospitals")
    print(f"Target Directory: {raw_dir} | Random Seed: {seed}")
    print("=" * 60)

    # -------------------------------------------------------------
    # 1. DOCTORS (30 records)
    # -------------------------------------------------------------
    specialties = [
        "Cardiology", "Orthopedics", "Dermatology", "Neurology",
        "Pediatrics", "General Medicine", "ENT", "Ophthalmology"
    ]
    
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
        "Matthew", "Margaret", "Anthony", "Betty", "Donald", "Sandra"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]

    doctor_records = []
    schedules = [
        "Morning Shift (08:30-12:30)",
        "Afternoon Shift (13:30-17:30)",
        "Full Day (09:00-17:00)"
    ]
    working_day_patterns = [
        "Mon-Wed-Fri", "Tue-Thu-Sat", "Mon-Tue-Wed-Thu-Fri",
        "Mon-Tue-Thu", "Wed-Fri-Sat"
    ]

    for i in range(30):
        doc_id = f"DOC-{101 + i}"
        doc_name = f"Dr. {first_names[i]} {last_names[i]}"
        spec = specialties[i % len(specialties)]
        schedule = schedules[i % len(schedules)]
        work_days = working_day_patterns[i % len(working_day_patterns)]
        doctor_records.append({
            "doctor_id": doc_id,
            "doctor_name": doc_name,
            "specialty": spec,
            "clinic_schedule": schedule,
            "working_days": work_days
        })
    df_doctors = pd.DataFrame(doctor_records)
    doctors_path = os.path.join(raw_dir, "doctors.csv")
    df_doctors.to_csv(doctors_path, index=False)
    print(f"Generated {len(df_doctors)} doctors -> {doctors_path}")

    # -------------------------------------------------------------
    # 2. PATIENTS (~1,500 unique records)
    # -------------------------------------------------------------
    num_patients = 1500
    localities = [
        "North District", "South District", "East District", "West District",
        "Central Valley", "Riverside", "Metro Core", "Suburbia"
    ]

    patient_records = []
    for i in range(num_patients):
        pat_id = f"PAT-{1001 + i}"
        age = int(np.clip(np.random.normal(45, 20), 1, 88))
        if age <= 17:
            age_group = "Pediatric (0-17)"
        elif age <= 35:
            age_group = "Young Adult (18-35)"
        elif age <= 55:
            age_group = "Middle-Aged (36-55)"
        else:
            age_group = "Senior (56+)"
        
        locality = random.choice(localities)
        patient_records.append({
            "patient_id": pat_id,
            "age": age,
            "age_group": age_group,
            "locality": locality
        })
    df_patients = pd.DataFrame(patient_records)

    # -------------------------------------------------------------
    # 3. CALENDAR (Full year 2024: 2024-01-01 to 2024-12-31)
    # -------------------------------------------------------------
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = [start_date + timedelta(days=d) for d in range((end_date - start_date).days + 1)]

    # Public holidays in 2024 (sample major holiday dates)
    public_holidays = {
        datetime(2024, 1, 1).date(),
        datetime(2024, 1, 15).date(),
        datetime(2024, 2, 19).date(),
        datetime(2024, 5, 27).date(),
        datetime(2024, 7, 4).date(),
        datetime(2024, 9, 2).date(),
        datetime(2024, 11, 28).date(),
        datetime(2024, 12, 25).date()
    }

    def get_season(month):
        if month in [12, 1, 2]:
            return "Winter"
        elif month in [3, 4, 5]:
            return "Spring"
        elif month in [6, 7, 8]:
            return "Summer"
        else:
            return "Fall"

    calendar_records = []
    for dt in date_range:
        d = dt.date()
        calendar_records.append({
            "date": d.strftime("%Y-%m-%d"),
            "weekday": dt.strftime("%A"),
            "month": dt.strftime("%B"),
            "holiday": "Yes" if d in public_holidays else "No",
            "season": get_season(dt.month)
        })
    df_calendar = pd.DataFrame(calendar_records)
    calendar_path = os.path.join(raw_dir, "calendar.csv")
    df_calendar.to_csv(calendar_path, index=False)
    print(f"Generated {len(df_calendar)} calendar days -> {calendar_path}")

    # -------------------------------------------------------------
    # 4. APPOINTMENTS (~5,000 records)
    # -------------------------------------------------------------
    num_appointments = 5000
    appointment_times = [
        "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"
    ]

    # Department mapping to doctor IDs
    dept_to_docs = {spec: df_doctors[df_doctors["specialty"] == spec]["doctor_id"].tolist() for spec in specialties}

    # Weightings for realistic distribution
    dept_weights = [0.18, 0.16, 0.12, 0.10, 0.12, 0.18, 0.08, 0.06]

    appointments = []
    # Patient appointment simulation
    # To maintain realistic history, we select dates throughout 2024
    all_dates = [dt.date() for dt in date_range]

    # Patient tendency factor for no-show (latent behavioral tendency)
    patient_tendencies = {
        pat["patient_id"]: np.clip(np.random.beta(2, 7), 0.05, 0.70)
        for _, pat in df_patients.iterrows()
    }

    # Track patient history chronologically
    patient_history = {pat["patient_id"]: {"total": 0, "noshows": 0} for _, pat in df_patients.iterrows()}

    for i in range(num_appointments):
        app_id = f"APP-{10001 + i}"
        pat_id = f"PAT-{random.randint(1001, 1000 + num_patients)}"
        pat_info = df_patients.loc[df_patients["patient_id"] == pat_id].iloc[0]
        
        # Select department
        dept = np.random.choice(specialties, p=dept_weights)
        doc_id = random.choice(dept_to_docs[dept])

        # Appointment date: random date in 2024
        app_date = random.choice(all_dates)
        
        # Waiting days: exponential distribution with realistic spread
        # 0 to 45 days
        raw_waiting = int(np.random.exponential(scale=6.5))
        waiting_days = min(raw_waiting, 45)
        booking_date = app_date - timedelta(days=waiting_days)

        app_time = random.choice(appointment_times)

        # Baseline no-show probability calculated dynamically:
        # 1. Patient baseline tendency
        base_p = patient_tendencies[pat_id]

        # 2. Waiting days impact: longer wait -> higher no-show probability
        if waiting_days == 0:
            wait_mult = 0.45
        elif waiting_days <= 3:
            wait_mult = 0.75
        elif waiting_days <= 7:
            wait_mult = 1.05
        elif waiting_days <= 14:
            wait_mult = 1.35
        else:
            wait_mult = 1.70

        # 3. Day of week impact (Mondays and Fridays slightly higher no-show)
        weekday = app_date.strftime("%A")
        if weekday in ["Monday", "Friday"]:
            day_mult = 1.15
        elif weekday in ["Tuesday", "Wednesday", "Thursday"]:
            day_mult = 0.90
        else: # Weekend
            day_mult = 1.10

        # 4. Age impact (young adults higher, seniors lower)
        if pat_info["age_group"] == "Young Adult (18-35)":
            age_mult = 1.25
        elif pat_info["age_group"] == "Senior (56+)":
            age_mult = 0.80
        else:
            age_mult = 1.00

        # Combined probability of no-show
        prob_noshow = np.clip(base_p * wait_mult * day_mult * age_mult, 0.04, 0.75)

        # Status distribution:
        # Most appointments are Attended or No-show (~90% resolved),
        # remaining are Cancelled, Rescheduled, or Pending
        rand_val = random.random()
        if rand_val < 0.05:
            status = "Cancelled"
        elif rand_val < 0.08:
            status = "Rescheduled"
        elif rand_val < 0.10:
            status = "Pending"
        else:
            # Resolved appointment
            if random.random() < prob_noshow:
                status = "No-show"
                patient_history[pat_id]["noshows"] += 1
            else:
                status = "Attended"
            patient_history[pat_id]["total"] += 1

        appointments.append({
            "appointment_id": app_id,
            "patient_id": pat_id,
            "doctor_id": doc_id,
            "appointment_date": app_date.strftime("%Y-%m-%d"),
            "booking_date": booking_date.strftime("%Y-%m-%d"),
            "department": dept,
            "appointment_status": status,
            "waiting_days": waiting_days,
            "appointment_time": app_time
        })

    df_appointments = pd.DataFrame(appointments)

    # Sort appointments by appointment_date and appointment_time to establish proper timeline
    df_appointments.sort_values(by=["appointment_date", "appointment_time"], inplace=True)
    df_appointments.reset_index(drop=True, inplace=True)

    # Update patient historical counts in df_patients consistently
    df_patients["previous_appointments"] = df_patients["patient_id"].map(
        lambda pid: patient_history[pid]["total"]
    )
    df_patients["previous_no_shows"] = df_patients["patient_id"].map(
        lambda pid: patient_history[pid]["noshows"]
    )
    patients_path = os.path.join(raw_dir, "patients.csv")
    df_patients.to_csv(patients_path, index=False)
    print(f"Generated {len(df_patients)} patients with consistent history -> {patients_path}")

    # -------------------------------------------------------------
    # 5. INTRODUCE CONTROLLED DATA QUALITY ISSUES IN APPOINTMENTS
    # -------------------------------------------------------------
    # A. Missing appointment statuses (~45 records, ~0.9%)
    missing_status_idx = np.random.choice(df_appointments.index, size=45, replace=False)
    df_appointments.loc[missing_status_idx, "appointment_status"] = np.nan

    # B. Inconsistent department names (casing & whitespace differences)
    messy_dept_idx = np.random.choice(df_appointments.index, size=150, replace=False)
    for idx in messy_dept_idx:
        orig = df_appointments.loc[idx, "department"]
        variant = random.choice([
            orig.upper(),
            orig.lower(),
            f" {orig} ",
            orig.capitalize() + " ",
            " " + orig.lower()
        ])
        df_appointments.loc[idx, "department"] = variant

    # C. Invalid or negative waiting days (~20 records)
    invalid_wait_idx = np.random.choice(df_appointments.index, size=20, replace=False)
    for idx in invalid_wait_idx:
        # e.g., negative waiting day where booking date is set after appointment date
        app_dt = datetime.strptime(df_appointments.loc[idx, "appointment_date"], "%Y-%m-%d")
        neg_val = -random.randint(1, 5)
        df_appointments.loc[idx, "waiting_days"] = neg_val
        df_appointments.loc[idx, "booking_date"] = (app_dt - timedelta(days=neg_val)).strftime("%Y-%m-%d")

    # D. A few duplicate booking records (~12 exact duplicate rows)
    dup_rows = df_appointments.sample(n=12, random_state=seed)
    df_appointments = pd.concat([df_appointments, dup_rows], ignore_index=True)

    # Re-shuffle slightly to blend duplicates naturally
    df_appointments = df_appointments.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    appointments_path = os.path.join(raw_dir, "appointments.csv")
    df_appointments.to_csv(appointments_path, index=False)
    print(f"Generated {len(df_appointments)} appointments (with controlled quality issues) -> {appointments_path}")

    # -------------------------------------------------------------
    # 6. REMINDERS (linked to appointments)
    # -------------------------------------------------------------
    # Unique appointment IDs (drop duplicate appointment_ids when generating reminder pool)
    unique_app_ids = df_appointments["appointment_id"].drop_duplicates().tolist()
    
    # Realistic nuances:
    # - ~14% appointments have no reminder scheduled at all
    # - reminder types: SMS, Email, Phone Call
    # - reminder_sent: 'Yes', 'No'
    # - reminder_response: 'Confirmed', 'Reschedule Requested', 'No Response', or blank/NaN
    reminder_records = []
    rem_id_counter = 20001

    for app_id in unique_app_ids:
        # 14% chance of no reminder scheduled
        if random.random() < 0.14:
            continue

        rem_type = np.random.choice(["SMS", "Email", "Phone Call"], p=[0.60, 0.25, 0.15])
        
        # 92% sent, 8% failed to send / not sent
        sent = "Yes" if random.random() < 0.92 else "No"

        if sent == "Yes":
            # Response behavior
            resp_choice = np.random.choice(
                ["Confirmed", "Reschedule Requested", "No Response", np.nan],
                p=[0.55, 0.10, 0.25, 0.10]
            )
            response = resp_choice if pd.notna(resp_choice) else np.nan
        else:
            response = np.nan  # Not sent cannot have a response

        reminder_records.append({
            "reminder_id": f"REM-{rem_id_counter}",
            "appointment_id": app_id,
            "reminder_type": rem_type,
            "reminder_sent": sent,
            "reminder_response": response
        })
        rem_id_counter += 1

    df_reminders = pd.DataFrame(reminder_records)
    reminders_path = os.path.join(raw_dir, "reminders.csv")
    df_reminders.to_csv(reminders_path, index=False)
    print(f"Generated {len(df_reminders)} reminders -> {reminders_path}")

    # -------------------------------------------------------------
    # 7. DATA README (data/README.md)
    # -------------------------------------------------------------
    readme_path = "data/README.md"
    readme_content = f"""# CareBridge Hospitals - Dataset Documentation
## DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491

> **SYNTHETIC DEMONSTRATION DATA NOTICE**  
> All datasets located in `data/raw/` and `data/processed/` are synthetically generated for demonstration and educational assessment purposes.  
> They do **not** represent real hospital records or identifiable protected health information (PHI).  
> Random seed used: `{seed}`. Generated on: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`.

---

### 1. Dataset Schemas and Record Counts

| Dataset | File Path | Record Count | Attributes | Primary Key / Join Key |
| :--- | :--- | :--- | :--- | :--- |
| **Appointments** | `data/raw/appointments.csv` | ~5,012 | `appointment_id`, `patient_id`, `doctor_id`, `appointment_date`, `booking_date`, `department`, `appointment_status`, `waiting_days`, `appointment_time` | `appointment_id` |
| **Patients** | `data/raw/patients.csv` | 1,500 | `patient_id`, `age`, `age_group`, `locality`, `previous_appointments`, `previous_no_shows` | `patient_id` |
| **Doctors** | `data/raw/doctors.csv` | 30 | `doctor_id`, `doctor_name`, `specialty`, `clinic_schedule`, `working_days` | `doctor_id` |
| **Reminders** | `data/raw/reminders.csv` | ~4,300 | `reminder_id`, `appointment_id`, `reminder_type`, `reminder_sent`, `reminder_response` | `reminder_id`, `appointment_id` |
| **Calendar** | `data/raw/calendar.csv` | 366 | `date`, `weekday`, `month`, `holiday`, `season` | `date` |

---

### 2. Deliberate Data Quality Issues for Preprocessing Practice

To simulate real-world electronic health record (EHR) anomalies, the raw datasets include controlled data quality defects:
1. **Missing Appointment Statuses**: Approximately 45 records have missing (`NaN`) `appointment_status`. These must be excluded from supervised model training and target-dependent metrics.
2. **Duplicate Bookings**: 12 exact duplicate rows were introduced to test deduplication pipelines.
3. **Inconsistent Department Names**: Department names contain inconsistent casing (e.g., `CARDIOLOGY`, `orthopedics`) and leading/trailing whitespace.
4. **Invalid / Negative Waiting Days**: Approximately 20 records exhibit negative waiting times where `booking_date` was logged after `appointment_date`.
5. **Incomplete Reminders**: ~14% of appointments have no reminder record, and some sent reminders have missing response logs.

---

### 3. Preprocessing and Join Logic
- **Primary Merge**: Cleaned appointments are left-joined with `patients` (on `patient_id`), `doctors` (on `doctor_id`), deduplicated `reminders` (on `appointment_id`), and `calendar` (on `appointment_date == date`).
- **Join Cardinality**: Validated 1:1 join between appointments and reminders to avoid row multiplication.
- **Output**: Cleaned and merged dataset saved to `data/processed/cleaned_appointments.csv`.
"""
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    print(f"Generated documentation -> {readme_path}")
    print("=" * 60)
    print("Dataset generation completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    generate_all_datasets()
