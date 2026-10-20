# CareBridge Hospitals — Outpatient Appointment Attendance & Scheduling Optimization
## Final Analytical Findings, Machine Learning Benchmarks & Strategic Report
**Assessment:** DS Sprint Skill-Based Assessment 2 | **Challenge ID:** U23AD491  
**Candidate:** Manojkumar S (Register No: U23AD491)  
**Organization:** CareBridge Hospitals | **Domain:** Healthcare Analytics

---

### Executive Summary

CareBridge Hospitals initiated this study to evaluate outpatient attendance patterns, understand the drivers of missed visits (no-shows), and improve clinic scheduling. Missed appointments disrupt clinical operations, increase waiting lists, and cause substantial physician downtime.

Using a rigorous end-to-end Data Science approach across 5,012 outpatient records, this project implemented data cleaning, leakage-free temporal feature engineering, supervised classification modeling, and an interactive 10-sheet Microsoft Excel reporting workbook (`outputs/Hospital_Appointment_Insight.xlsx`).

---

### 1. Data Understanding & Quality Control (Round 1)

#### 1.1 Dataset Architecture
The project analyzed five relational tables:
1. **`appointments.csv`**: 5,012 outpatient appointments covering 8 specialties across 2024.
2. **`patients.csv`**: 1,500 unique patient demographics, age cohorts, and localities.
3. **`doctors.csv`**: 30 attending physicians, specialties, schedules, and working days.
4. **`reminders.csv`**: 4,278 automated reminder logs (SMS, Email, Phone Call) and delivery responses.
5. **`calendar.csv`**: 366 calendar days with weekday, month, holiday flags, and season indicators.

#### 1.2 Data Preprocessing Results
- **Deduplication:** Identified and eliminated 12 exact duplicate booking records, leaving 5,000 distinct appointment bookings.
- **Negative Waiting Times:** Identified 20 records where `booking_date` was logged after `appointment_date`. These anomalies were corrected to same-day bookings (0 days waiting).
- **Label Integrity:** Preserved 45 appointments with unresolved/missing status under a dedicated flag (`status_is_missing = True`), excluding them from binary target modeling to prevent label contamination.
- **Join Cardinality:** Validated strict 1:1 join relationships across patients, clinicians, calendar days, and deduplicated reminders to prevent row explosion.

---

### 2. Exploratory Data Analysis & Empirical Findings

#### Key Finding 1: Booking Lead-Time Decay
Outpatient attendance exhibits severe degradation as advance booking windows expand:
- **Same-day & Short Lead Time (0–3 days):** No-show rate is only **12.2%**.
- **Moderate Lead Time (4–7 days):** No-show rate rises to **21.5%**.
- **Long Lead Time (8–14 days):** No-show rate reaches **29.1%**.
- **Extended Lead Time (>14 days):** No-show rate surges to **33.8%** (>2.7x higher than short lead times).

*Operational Implication:* Appointments booked weeks in advance suffer memory decay and resolution of acute symptoms, requiring structured reinforcement.

#### Key Finding 2: Behavioral Recidivism (Prior No-show History)
Conditioned on strictly prior visits:
- **0 Prior Misses:** Current appointment no-show rate is **18.7%**.
- **1 Prior Miss:** Current appointment no-show rate increases to **31.2%**.
- **2+ Prior Misses:** Current appointment no-show rate exceeds **45.1%**.

*Operational Implication:* A patient's prior compliance record is the single strongest behavioral indicator of future visit adherence.

#### Key Finding 3: Reminder Engagement & Dispatch Channels
- **Confirmed Reminders (SMS/Phone Call):** Attendance rate exceeds **86.4%**.
- **Failed / Unsent Reminders:** No-show rate increases to **32.8%**.
- **Uncontacted (No Reminder Scheduled):** Attendance remains below average at **73.1%**.

*Methodological Notice:* Observed differences reflect strong statistical association rather than pure causation; patient engagement correlates with both reminder responsiveness and clinic attendance.

#### Key Finding 4: Departmental & Temporal Variations
- **Departmental Load:** High-volume disciplines such as **General Medicine** and **Orthopedics** experience the highest absolute missed visit counts (~26% no-show rate), whereas procedural clinics (**Ophthalmology**) exhibit stronger attendance (~82%).
- **Weekday Patterns:** **Mondays** and **Fridays** experience elevated no-show rates (~26.5%) compared to mid-week sessions (Tuesday–Thursday at ~21.8%).

---

### 3. Feature Engineering & Supervised Machine Learning (Round 2)

#### 3.1 Target Variable Definition
- **Positive Class (`1`):** No-show (patient missed scheduled visit).
- **Negative Class (`0`):** Attended (patient completed visit).
- Non-binary statuses (`Cancelled`, `Rescheduled`, `Pending`, `Unresolved`) were strictly excluded from binary classification.

#### 3.2 Leakage Prevention Strategy
Historical patient features (`prior_appointments_count`, `prior_noshow_count`, `prior_noshow_rate`) were computed dynamically using a strictly chronological cumulative sum shifted by 1 record (`shift(1)` within patient group). This mathematically guarantees that no future or concurrent appointment outcome is leaked into predictors.

#### 3.3 Hold-Out Test Set Performance Benchmark (Chronological Split: 20% Holdout)

| Model Pipeline | Accuracy | Precision (No-show) | Recall (No-show) | F1-Score (No-show) | ROC-AUC | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Dummy Classifier (Baseline)** | 75.28% | 0.00% | 0.00% | 0.0000 | 0.5000 | Candidate |
| **Logistic Regression (Class-Balanced)** | **61.30%** | **33.06%** | **55.20%** | **0.4136** | **0.6212** | **Selected Champion** |
| **Random Forest Classifier** | 72.15% | 38.14% | 20.36% | 0.2655 | 0.6009 | Candidate |

#### 3.4 Champion Model Selection Justification
In hospital outpatient management, the cost of a false negative (failing to predict a missed visit, resulting in an unutilized doctor hour) far exceeds the cost of a false positive (sending an extra reminder). While the Dummy baseline achieves 75.28% accuracy by predicting "Attended" for every patient, its clinical utility is zero (0% recall). **Logistic Regression with class-balanced weighting was selected as Champion** because it achieves **55.20% Recall** and the highest **F1-Score (0.4136)**, identifying over half of all imminent no-shows for proactive mitigation.

---

### 4. Excel Analysis & Executive Reporting (Round 3)

The project deliverable `outputs/Hospital_Appointment_Insight.xlsx` contains 10 structured worksheets:
1. **Summary Dashboard:** Executive KPI cards, 4 embedded Excel charts, key observations, and recommendations.
2. **Cleaned Data:** Formatted Excel Table (`CleanedAppointmentsTable`), frozen headers, filters, and conditional formatting.
3. **Department Analysis:** Formula-driven summary (`COUNTIF`, `COUNTIFS`, `IFERROR`) and department bar chart.
4. **Waiting-Time Analysis:** 5 lead-time windows, attendance rates, and column chart.
5. **Day-wise Attendance:** Monday–Sunday calendar order tracking and chart.
6. **Reminder Analysis:** Communication channel and delivery breakdown with association disclosure.
7. **Repeat No-shows:** Point-in-time patient recidivism brackets (`0`, `1`, `2`, `3+` prior misses).
8. **Clinic Utilization:** Physician appointment load breakdown with capacity proxy disclosure.
9. **ML Model Results:** Benchmarking table and comparison chart displaying real model metrics.
10. **Final Summary:** Complete project synthesis, problem statement, methodology, and conclusions.

---

### 5. Practical, Evidence-Based Recommendations

1. **Targeted Predictive Reminder Cadence:**
   Deploy automated multi-channel (SMS + Phone) interactive confirmations at **7 days** and **48 hours** prior to appointments for patients identified as high risk (lead time >7 days or prior missed visits). Reminders must feature one-click digital confirmation or rescheduling.
2. **Algorithmic Dynamic Double-Booking:**
   In departments with severe no-show rates (General Medicine, Orthopedics), introduce controlled 1-slot overbooking for morning clinic sessions when model-predicted no-show probabilities exceed 40%, protecting clinician utilization without expanding patient waiting room times.
3. **Frictionless Rescheduling System:**
   Enable instant rescheduling via SMS/WhatsApp links, converting unannounced no-shows into scheduled reallocations and releasing booked slots to waitlisted patients.
