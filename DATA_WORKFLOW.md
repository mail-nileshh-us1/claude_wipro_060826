# Patient Health Analyzer - Data Workflow Documentation

## Overview
Complete end-to-end workflow for generating sample patient data, exporting to CSV, importing to MySQL database, and reading/analyzing the data.

## Workflow Steps

### 1. Generate Sample Data
**Script**: `generate_sample_data.py`

Generates realistic sample patient data with 50 patients.

```bash
python generate_sample_data.py
```

**Features**:
- Generates 50 unique patient records
- Realistic health metric distributions:
  - Age: 18-85 years
  - BMI: 18.6-38.5 (40% healthy, 40% overweight, 20% obese)
  - Blood Pressure: Realistic systolic/diastolic ranges
  - Glucose Level: 70-300 mg/dL (60% normal, 25% prediabetes, 15% diabetes)
- Exports to `data/generated_patients.csv`
- Displays statistical summaries

**Output Example**:
```
PatientID,name,age,BMI,Blood_pressure,Glucose_level
1,Christopher Anderson,80,30.5,110/110,88
2,Rebecca Hernandez,42,37.2,130/86,82
...
```

---

### 2. Load CSV to Database
**Script**: `csv_to_database.py`

Loads CSV data into MySQL database with health status categorization.

```bash
# Load with data clearing (fresh start)
python csv_to_database.py --clear

# Load without clearing (append data)
python csv_to_database.py
```

**Command Line Options**:
```
--csv, -f         Path to CSV file (default: data/generated_patients.csv)
--host            Database host (default: localhost)
--user, -u        Database user (default: root)
--password, -p    Database password (default: Tek@12345)
--database, -db   Database name (default: test_db)
--clear, -c       Clear existing data before loading
```

**Process**:
1. Read CSV file
2. Connect to MySQL database
3. Create/verify patients table
4. Apply health status categorization to all records
5. Insert records with progress tracking
6. Display health status distribution
7. Show sample records from database

**Example Output**:
```
[Step 1] Reading CSV file: data/generated_patients.csv
✅ Successfully read 50 records from CSV

[Step 6] Loading data to database...
   Progress: 10/50 records processed
   Progress: 20/50 records processed
   ...
✅ Data loading complete!
   Inserted: 50 records
   Failed: 0 records
   Duplicates: 0 records

[Step 8] Health Status Distribution:
   At Risk   :  38 ( 76.0%) 
   Critical  :   1 (  2.0%) 
   Healthy   :  11 ( 22.0%)
```

---

### 3. Read from Database
**Script**: `read_from_database.py`

Reads and analyzes all patient data from the database.

```bash
# Read and display data
python read_from_database.py

# Read and export to CSV
python read_from_database.py --export
```

**Command Line Options**:
```
--host            Database host (default: localhost)
--user, -u        Database user (default: root)
--password, -p    Database password (default: Tek@12345)
--database, -db   Database name (default: test_db)
--export, -e      Export data to CSV
```

**Analysis Provided**:

1. **Health Metrics Statistics**
   - Age: Mean, Median, Min, Max, Std Dev
   - BMI: Mean, Median, Min, Max, Std Dev
   - Glucose Level: Mean, Median, Min, Max, Std Dev

2. **Health Status Distribution**
   - Count and percentage for each status
   - Visual bar chart representation

3. **Sample Patient Records**
   - First 10 records from database with full details

4. **Age Group Analysis**
   - 18-30, 31-45, 46-60, 60+ age ranges
   - Count and percentage for each group

5. **BMI Category Analysis**
   - Underweight, Normal, Overweight, Obese
   - Count and percentage for each category

6. **High-Risk Patients**
   - Lists all patients with "Critical" status
   - Shows top 10 critical patients with details

7. **CSV Export** (optional)
   - Exports complete dataset to `data/database_export.csv`

**Example Output**:
```
[Step 5] Health Metrics Statistics:
----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- -----
Age Statistics:
  Mean: 50.1 years
  Median: 47.0 years
  Min: 18 years | Max: 85 years
  Std Dev: 20.3 years

BMI Statistics:
  Mean: 27.6
  Median: 26.8
  Min: 18.6 | Max: 38.5
  Std Dev: 5.3

Glucose Level Statistics:
  Mean: 105.7 mg/dL
  Median: 91.5 mg/dL
  Min: 70 mg/dL | Max: 234 mg/dL
  Std Dev: 37.6 mg/dL

[Step 6] Health Status Distribution:
  At Risk   : 190 patients ( 76.0%) 
  Critical  :   5 patients (  2.0%) 
  Healthy   :  55 patients ( 22.0%)

[Step 9] BMI Category Analysis:
  Normal    :  80 patients ( 32.0%)
  Overweight:  95 patients ( 38.0%)
  Obese     :  75 patients ( 30.0%)
```

---

## Complete Workflow Example

```bash
#!/bin/bash

# Step 1: Generate sample data
python generate_sample_data.py

# Step 2: Load to database (with data clearing)
python csv_to_database.py --clear

# Step 3: Read from database and export
python read_from_database.py --export

# View results
echo "Generated CSV:"
head -5 data/generated_patients.csv

echo -e "\nDatabase Export CSV:"
head -5 data/database_export.csv
```

---

## Data Files

### Input Files
- `data/generated_patients.csv` - Generated sample data (50 records)
  - Size: ~1.8 KB
  - Columns: PatientID, name, age, BMI, Blood_pressure, Glucose_level

### Output Files
- `data/database_export.csv` - Database export with health status (250 records)
  - Size: ~23 KB
  - Columns: PatientID, name, age, BMI, Blood_pressure, Glucose_level, health_status, created_at, updated_at, BMI_Category

---

## Database Details

### Table Structure
```sql
CREATE TABLE patients (
    PatientID INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    age INT,
    BMI FLOAT,
    Blood_pressure VARCHAR(20),
    Glucose_level INT,
    health_status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
```

### Connection Details
- **Host**: localhost
- **User**: root
- **Password**: Tek@12345
- **Database**: test_db
- **Port**: 3306

---

## Health Status Categorization

Health status is determined by risk factor accumulation:

| Factor | Condition | Risk Points |
|--------|-----------|------------|
| BMI | 25-29.9 (Overweight) | +1 |
| BMI | ≥30 (Obese) | +2 |
| Blood Pressure | 120-139/80-89 (Elevated) | +1 |
| Blood Pressure | ≥140/90 (High) | +2 |
| Glucose | 100-125 (Prediabetes) | +1 |
| Glucose | ≥126 (Diabetes) | +2 |

**Status Determination**:
- **Healthy**: 0-1 risk points
- **At Risk**: 2-4 risk points
- **Critical**: ≥5 risk points

---

## Current Database Statistics

- **Total Records**: 250 patients
- **Health Status Distribution**:
  - Healthy: 55 (22.0%)
  - At Risk: 190 (76.0%)
  - Critical: 5 (2.0%)

- **Age Distribution**:
  - 18-30: 55 (22.0%)
  - 31-45: 60 (24.0%)
  - 46-60: 50 (20.0%)
  - 60+: 85 (34.0%)

- **BMI Distribution**:
  - Normal: 80 (32.0%)
  - Overweight: 95 (38.0%)
  - Obese: 75 (30.0%)

---

## Error Handling

### Common Issues

1. **Connection Refused**
   - Verify MySQL server is running
   - Check credentials in scripts
   - Confirm database name exists

2. **File Not Found**
   - Ensure CSV file path is correct
   - Check file exists before loading
   - Use absolute paths if needed

3. **Duplicate Entry**
   - Use `--clear` flag to clear existing data
   - Or use different database name

### Troubleshooting

```bash
# Test MySQL connection
python test_mysql_connection.py

# Check database setup
python setup_database.py

# Verify CSV file
ls -lh data/*.csv
head -10 data/generated_patients.csv
```

---

## Performance Notes

- **Generate Sample Data**: < 1 second
- **Load 50 Records**: ~1 second
- **Read 250 Records**: ~0.5 seconds
- **Export to CSV**: < 1 second

---

## Future Enhancements

- [ ] Batch insert optimization for large datasets
- [ ] Data validation and error reporting
- [ ] Support for additional health metrics
- [ ] Real-time data streaming
- [ ] Advanced analytics and reporting
- [ ] Data visualization dashboard
- [ ] API endpoints for data access

---

## Quick Reference Commands

```bash
# Generate data
python generate_sample_data.py

# Load to database
python csv_to_database.py --clear

# Read from database
python read_from_database.py

# Read and export
python read_from_database.py --export

# Test connection
python test_mysql_connection.py

# Setup database
python setup_database.py

# Run all tests
pytest -v
```

---

## Support

For issues or questions:
1. Check the error messages in the script output
2. Verify database credentials
3. Ensure MySQL server is running
4. Run `test_mysql_connection.py` to diagnose connection issues
5. Check `CLAUDE.md` for project documentation
