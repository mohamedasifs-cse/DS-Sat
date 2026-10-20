# CareBridge Hospitals - Dataset Documentation
## DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491

> **SYNTHETIC DEMONSTRATION DATA NOTICE**  
> All datasets located in `data/raw/` and `data/processed/` are synthetically generated for demonstration and educational assessment purposes.  
> They do **not** represent real hospital records or identifiable protected health information (PHI).  
> Random seed used: `123`. Generated on: `2026-10-20 17:56:56`.

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
