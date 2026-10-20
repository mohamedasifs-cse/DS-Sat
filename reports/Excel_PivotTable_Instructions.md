# CareBridge Hospitals — Microsoft Excel PivotTable & PivotChart Guide
## DS Sprint Skill-Based Assessment 2 | Challenge ID: U23AD491
**Project Title:** Hospital Appointment Insight  
**Author:** Manojkumar S (Register No: U23AD491)

---

### Overview
This step-by-step instruction manual explains how to construct native **PivotTables** and **PivotCharts** inside Microsoft Excel using the cleaned appointment dataset stored in the **`Cleaned Data`** worksheet of `Hospital_Appointment_Insight.xlsx`.

The table in `Cleaned Data` is formally defined as an Excel Table named **`CleanedAppointmentsTable`** (`A1:AG5001`), which enables dynamic range references and automatic aggregation.

---

### Step-by-Step Instructions for Required Analyses

#### 1. Department Attendance PivotTable & PivotChart
- **Objective:** Compare appointment volume, attended visits, missed visits, and no-show rate across clinical departments.
- **Excel Steps:**
  1. Click anywhere inside the table in the **`Cleaned Data`** worksheet.
  2. Navigate to the top ribbon: **Insert** > **PivotTable** > select **New Worksheet** (rename tab to `Pivot_Department`).
  3. In the **PivotTable Fields** pane:
     - Drag **`department`** to **Rows**.
     - Drag **`appointment_status_clean`** to **Columns**.
     - Drag **`appointment_id`** to **Values** (summarized as `Count of appointment_id`).
  4. Filter column values: Click the dropdown next to **Column Labels** and uncheck `Cancelled`, `Rescheduled`, `Pending`, and `Unresolved` to isolate resolved visits (`Attended` and `No-show`).
  5. Add Calculated Field for No-show Rate:
     - Navigate to **PivotTable Analyze** > **Fields, Items, & Sets** > **Calculated Field**.
     - Name: `No_Show_Rate`.
     - Formula: `='No-show' / ('Attended' + 'No-show')`.
     - Click **OK**, then right-click the field > **Number Format** > **Percentage (0.0%)**.
  6. Insert PivotChart:
     - Go to **PivotTable Analyze** > **PivotChart** > select **Clustered Column** or **Clustered Bar**.
     - Title: `Department No-show Rate Comparison`.

---

#### 2. Waiting-Time Analysis PivotTable & PivotChart
- **Objective:** Analyze no-show rates grouped by appointment lead time windows (`0 days`, `1–3 days`, `4–7 days`, `8–14 days`, `More than 14 days`).
- **Excel Steps:**
  1. Go to **Insert** > **PivotTable** from `CleanedAppointmentsTable`.
  2. In the **PivotTable Fields** pane:
     - Drag **`waiting_time_group`** to **Rows**.
     - Drag **`appointment_status_clean`** to **Columns** (filter for `Attended` and `No-show`).
     - Drag **`appointment_id`** to **Values** (`Count`).
  3. Sort Rows: Right-click the row labels and manually reorder the categories logically from `0 days`, `1–3 days`, `4–7 days`, `8–14 days`, to `More than 14 days`.
  4. Add Calculated Field:
     - **Calculated Field**: Name: `Waiting_NoShow_Rate`, Formula: `='No-show' / ('Attended' + 'No-show')`.
     - Format as `0.0%`.
  5. Insert PivotChart:
     - Select **Insert** > **PivotChart** > **Clustered Column Chart**.
     - Title: `No-show Rate by Booking Lead Time Window`.

---

#### 3. Day-wise Attendance PivotTable & PivotChart
- **Objective:** Track outpatient attendance across days of the week in standard Monday–Sunday calendar order.
- **Excel Steps:**
  1. Insert a new PivotTable referencing `CleanedAppointmentsTable`.
  2. Drag **`weekday`** to **Rows**.
  3. Drag **`appointment_status_clean`** to **Columns** (filter for `Attended` and `No-show`).
  4. Drag **`appointment_id`** to **Values** (`Count`).
  5. Calendar Sort: Click the Row dropdown and drag row items to enforce chronological calendar order: `Monday`, `Tuesday`, `Wednesday`, `Thursday`, `Friday`, `Saturday`, `Sunday`.
  6. Add Calculated Field:
     - Name: `Weekday_NoShow_Rate`, Formula: `='No-show' / ('Attended' + 'No-show')`.
     - Format as `0.0%`.
  7. Insert PivotChart:
     - Select **PivotChart** > **Column Chart**.
     - Title: `Day-wise Outpatient No-show Distribution`.

---

#### 4. Reminder Comparison PivotTable & PivotChart
- **Objective:** Assess attendance differences across reminder communication channels (`SMS`, `Email`, `Phone Call`, `No Reminder Scheduled`) and transmission statuses (`Yes`, `No`, `Not Scheduled`).
- **Excel Steps:**
  1. Insert a new PivotTable referencing `CleanedAppointmentsTable`.
  2. Drag **`reminder_type`** to **Rows** (outer tier).
  3. Drag **`reminder_sent`** to **Rows** (inner tier below `reminder_type`).
  4. Drag **`appointment_status_clean`** to **Columns** (filter for `Attended` and `No-show`).
  5. Drag **`appointment_id`** to **Values** (`Count`).
  6. Add Calculated Field:
     - Name: `Reminder_Attendance_Rate`, Formula: `='Attended' / ('Attended' + 'No-show')`.
     - Format as `0.0%`.
  7. Insert PivotChart:
     - Select **PivotChart** > **Stacked Bar Chart** or **Clustered Bar Chart**.
     - Title: `Outpatient Attendance Across Reminder Channels and Dispatch Status`.
  8. *Analytical Notice:* Add a text box below the chart: *"Observed differences indicate statistical correlation rather than direct causation."*

---

#### 5. Repeat No-shows (Patient Recidivism) PivotTable & PivotChart
- **Objective:** Evaluate attendance recidivism conditioned on patient prior missed visits (`0 Prior Misses`, `1 Prior Miss`, `2 Prior Misses`, `3+ Prior Misses`).
- **Excel Steps:**
  1. Insert a new PivotTable referencing `CleanedAppointmentsTable`.
  2. Drag **`repeat_noshow_category`** to **Rows**.
  3. Drag **`appointment_status_clean`** to **Columns** (filter for `Attended` and `No-show`).
  4. Drag **`appointment_id`** to **Values** (`Count`).
  5. Reorder Rows: Order categories from `0 Prior Misses` to `3+ Prior Misses`.
  6. Add Calculated Field:
     - Name: `Recidivism_NoShow_Rate`, Formula: `='No-show' / ('Attended' + 'No-show')`.
     - Format as `0.0%`.
  7. Insert PivotChart:
     - Select **PivotChart** > **Clustered Column Chart**.
     - Title: `Current No-show Rate by Historical Missed Appointments`.

---

#### 6. Clinic Utilization & Physician Appointment Load PivotTable & PivotChart
- **Objective:** Determine clinic workload distribution across doctors and specialties as an operational capacity proxy.
- **Excel Steps:**
  1. Insert a new PivotTable referencing `CleanedAppointmentsTable`.
  2. Drag **`specialty`** to **Rows** (outer tier).
  3. Drag **`doctor_name`** to **Rows** (inner tier).
  4. Drag **`clinic_schedule`** to **Columns**.
  5. Drag **`appointment_id`** to **Values** (`Count of appointment_id`).
  6. Right-click the Values area > **Show Values As** > **% of Grand Total** to display appointment workload share.
  7. Insert PivotChart:
     - Select **PivotChart** > **Horizontal Bar Chart**.
     - Title: `Physician Appointment Workload by Clinic Shift`.
  8. *Capacity Note:* Add footnote: *"Appointment counts serve as an operational volume proxy in the absence of hourly clinician capacity caps."*

---

### Verification and Consistency Checklist
- Ensure Grand Totals match the 5,000 appointment count in `CleanedAppointmentsTable`.
- When calculating rates, always exclude `Cancelled`, `Rescheduled`, `Pending`, and `Unresolved` statuses to ensure exact denominator consistency with the formula-driven sheets in `Hospital_Appointment_Insight.xlsx`.
