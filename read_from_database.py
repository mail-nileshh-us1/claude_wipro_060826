#!/usr/bin/env python3
"""
Read and display data from MySQL database
"""

import sys
import os
import pandas as pd
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_connection import MySQLConnection


def read_all_patients(db_host='localhost', db_user='root',
                     db_password='Tek@12345', db_name='test_db',
                     export_csv=False):
    """
    Read all patient data from database

    Args:
        db_host (str): Database host
        db_user (str): Database user
        db_password (str): Database password
        db_name (str): Database name
        export_csv (bool): Export to CSV file
    """

    print("=" * 90)
    print("Database Patient Data Reader")
    print("=" * 90)

    # Connect to database
    print(f"\n[Step 1] Connecting to MySQL database...")
    db = MySQLConnection(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

    if not db.connect():
        print("❌ Failed to connect to database")
        return False
    print(f"✅ Connected to database: {db_name}")

    # Fetch all patients
    print(f"\n[Step 2] Fetching patient data...")
    patients = db.get_all_patients()

    if not patients:
        print("⚠️  No patients found in database")
        db.disconnect()
        return False

    print(f"✅ Retrieved {len(patients)} patient records")

    # Create DataFrame
    print(f"\n[Step 3] Creating DataFrame...")
    df = pd.DataFrame(patients, columns=[
        'PatientID', 'name', 'age', 'BMI', 'Blood_pressure',
        'Glucose_level', 'health_status', 'created_at', 'updated_at'
    ])
    print("✅ DataFrame created successfully")

    # Display overview
    print(f"\n[Step 4] Patient Data Overview:")
    print("-" * 90)
    print(f"Total Records: {len(df)}")
    print(f"Date Range: {df['created_at'].min()} to {df['created_at'].max()}")

    # Display statistics
    print(f"\n[Step 5] Health Metrics Statistics:")
    print("-" * 90)
    print(f"\nAge Statistics:")
    print(f"  Mean: {df['age'].mean():.1f} years")
    print(f"  Median: {df['age'].median():.1f} years")
    print(f"  Min: {df['age'].min()} years | Max: {df['age'].max()} years")
    print(f"  Std Dev: {df['age'].std():.1f} years")

    print(f"\nBMI Statistics:")
    print(f"  Mean: {df['BMI'].mean():.1f}")
    print(f"  Median: {df['BMI'].median():.1f}")
    print(f"  Min: {df['BMI'].min():.1f} | Max: {df['BMI'].max():.1f}")
    print(f"  Std Dev: {df['BMI'].std():.1f}")

    print(f"\nGlucose Level Statistics:")
    print(f"  Mean: {df['Glucose_level'].mean():.1f} mg/dL")
    print(f"  Median: {df['Glucose_level'].median():.1f} mg/dL")
    print(f"  Min: {df['Glucose_level'].min()} mg/dL | Max: {df['Glucose_level'].max()} mg/dL")
    print(f"  Std Dev: {df['Glucose_level'].std():.1f} mg/dL")

    # Health status distribution
    print(f"\n[Step 6] Health Status Distribution:")
    print("-" * 90)
    status_counts = df['health_status'].value_counts()
    for status in sorted(status_counts.index):
        count = status_counts[status]
        percentage = (count / len(df)) * 100
        bar = "█" * int(percentage / 2.5)
        print(f"  {status:10s}: {count:3d} patients ({percentage:5.1f}%) {bar}")

    # Display sample records
    print(f"\n[Step 7] Sample Patient Records:")
    print("-" * 90)
    print(df.head(10).to_string(index=False))

    # Age group analysis
    print(f"\n[Step 8] Age Group Analysis:")
    print("-" * 90)
    age_groups = pd.cut(df['age'], bins=[0, 30, 45, 60, 100],
                       labels=['18-30', '31-45', '46-60', '60+'])
    age_dist = age_groups.value_counts().sort_index()
    for group, count in age_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {group}: {count:3d} patients ({percentage:5.1f}%)")

    # BMI category analysis
    print(f"\n[Step 9] BMI Category Analysis:")
    print("-" * 90)
    def get_bmi_category(bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25:
            return 'Normal'
        elif bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    df['BMI_Category'] = df['BMI'].apply(get_bmi_category)
    bmi_dist = df['BMI_Category'].value_counts()
    for category in ['Underweight', 'Normal', 'Overweight', 'Obese']:
        if category in bmi_dist.index:
            count = bmi_dist[category]
            percentage = (count / len(df)) * 100
            print(f"  {category:10s}: {count:3d} patients ({percentage:5.1f}%)")

    # High-risk patients (Critical status)
    print(f"\n[Step 10] High-Risk Patients (Critical Status):")
    print("-" * 90)
    critical = df[df['health_status'] == 'Critical']
    if len(critical) > 0:
        print(f"Found {len(critical)} critical patients:")
        print(critical[['PatientID', 'name', 'age', 'BMI', 'Blood_pressure', 'Glucose_level']].head(10).to_string(index=False))
    else:
        print("No critical patients found")

    # Export to CSV (optional)
    if export_csv:
        print(f"\n[Step 11] Exporting data to CSV...")
        export_file = 'data/database_export.csv'
        os.makedirs(os.path.dirname(export_file), exist_ok=True)
        df.to_csv(export_file, index=False)
        print(f"✅ Data exported to {export_file}")

    db.disconnect()

    print("\n" + "=" * 90)
    print("✅ Database read operation complete!")
    print("=" * 90)
    return True


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Read patient data from MySQL database')
    parser.add_argument('--host', default='localhost',
                       help='Database host')
    parser.add_argument('--user', '-u', default='root',
                       help='Database user')
    parser.add_argument('--password', '-p', default='Tek@12345',
                       help='Database password')
    parser.add_argument('--database', '-db', default='test_db',
                       help='Database name')
    parser.add_argument('--export', '-e', action='store_true',
                       help='Export data to CSV')

    args = parser.parse_args()

    return read_all_patients(
        db_host=args.host,
        db_user=args.user,
        db_password=args.password,
        db_name=args.database,
        export_csv=args.export
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
