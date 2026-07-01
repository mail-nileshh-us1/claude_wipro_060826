#!/usr/bin/env python3
"""
Load CSV data to MySQL database
"""

import sys
import os
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_connection import MySQLConnection
from read_patients import categorize_health_status


def load_csv_to_database(csv_file, db_host='localhost', db_user='root',
                        db_password='Tek@12345', db_name='test_db',
                        clear_existing=False):
    """
    Load CSV data to MySQL database

    Args:
        csv_file (str): Path to CSV file
        db_host (str): Database host
        db_user (str): Database user
        db_password (str): Database password
        db_name (str): Database name
        clear_existing (bool): Clear existing data before loading
    """

    print("=" * 80)
    print("CSV to Database Loader")
    print("=" * 80)

    # Step 1: Read CSV file
    print(f"\n[Step 1] Reading CSV file: {csv_file}")
    try:
        df = pd.read_csv(csv_file)
        print(f"✅ Successfully read {len(df)} records from CSV")
        print(f"   Columns: {', '.join(df.columns)}")
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_file}")
        return False
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return False

    # Step 2: Connect to database
    print(f"\n[Step 2] Connecting to MySQL database...")
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

    # Step 3: Create table
    print(f"\n[Step 3] Creating/verifying patients table...")
    if not db.create_patients_table():
        print("❌ Failed to create patients table")
        db.disconnect()
        return False
    print("✅ Patients table ready")

    # Step 4: Clear existing data (optional)
    if clear_existing:
        print(f"\n[Step 4] Clearing existing data...")
        if db.execute_query("DELETE FROM patients"):
            print("✅ Cleared existing patient records")
        else:
            print("⚠️  Could not clear existing data")

    # Step 5: Apply health status categorization
    print(f"\n[Step 5] Applying health status categorization...")
    df['health_status'] = df.apply(
        lambda row: categorize_health_status(
            row['BMI'],
            row['Blood_pressure'],
            row['Glucose_level']
        ),
        axis=1
    )
    print("✅ Health status assigned to all records")

    # Step 6: Load data to database
    print(f"\n[Step 6] Loading data to database...")
    inserted = 0
    failed = 0
    duplicates = 0

    for idx, row in df.iterrows():
        try:
            if db.insert_patient(
                name=row['name'],
                age=int(row['age']) if pd.notna(row['age']) else None,
                bmi=float(row['BMI']) if pd.notna(row['BMI']) else None,
                blood_pressure=str(row['Blood_pressure']) if pd.notna(row['Blood_pressure']) else None,
                glucose_level=int(row['Glucose_level']) if pd.notna(row['Glucose_level']) else None,
                health_status=row['health_status']
            ):
                inserted += 1
            else:
                failed += 1
        except Exception as e:
            if 'Duplicate entry' in str(e):
                duplicates += 1
            else:
                failed += 1

        # Show progress every 10 records
        if (idx + 1) % 10 == 0:
            print(f"   Progress: {idx + 1}/{len(df)} records processed")

    print(f"\n✅ Data loading complete!")
    print(f"   Inserted: {inserted} records")
    print(f"   Failed: {failed} records")
    print(f"   Duplicates: {duplicates} records")

    # Step 7: Verify data
    print(f"\n[Step 7] Verifying loaded data...")
    all_patients = db.get_all_patients()
    if all_patients:
        print(f"✅ Total patients in database: {len(all_patients)}")

        # Display statistics
        print(f"\n[Step 8] Health Status Distribution:")
        from collections import Counter
        statuses = [p[6] for p in all_patients]
        distribution = Counter(statuses)
        for status in sorted(distribution.keys()):
            count = distribution[status]
            percentage = (count / len(all_patients)) * 100
            bar = "█" * int(percentage / 5)
            print(f"   {status:10s}: {count:3d} ({percentage:5.1f}%) {bar}")

        # Show sample records
        print(f"\n[Step 9] Sample Records from Database:")
        print("   " + "-" * 90)
        print(f"   {'ID':>3} | {'Name':<20} | {'Age':>3} | {'BMI':>5} | {'BP':>10} | {'Glucose':>7} | {'Status':<10}")
        print("   " + "-" * 90)
        for patient in all_patients[:5]:
            # patient structure: (PatientID, name, age, BMI, Blood_pressure, Glucose_level, health_status, created_at, updated_at)
            pid, name, age, bmi, bp, glucose, status, _, _ = patient
            age_str = str(age) if age else "N/A"
            bmi_str = f"{float(bmi):.1f}" if bmi else "N/A"
            glucose_str = str(glucose) if glucose else "N/A"
            print(f"   {pid:>3} | {name:<20} | {age_str:>3} | {bmi_str:>5} | {bp:>10} | {glucose_str:>7} | {status:<10}")
        print("   " + "-" * 90)

    db.disconnect()

    print("\n" + "=" * 80)
    print("✅ CSV to Database loading complete!")
    print("=" * 80)
    return True


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Load CSV data to MySQL database')
    parser.add_argument('--csv', '-f', default='data/generated_patients.csv',
                       help='Path to CSV file')
    parser.add_argument('--host', default='localhost',
                       help='Database host')
    parser.add_argument('--user', '-u', default='root',
                       help='Database user')
    parser.add_argument('--password', '-p', default='Tek@12345',
                       help='Database password')
    parser.add_argument('--database', '-db', default='test_db',
                       help='Database name')
    parser.add_argument('--clear', '-c', action='store_true',
                       help='Clear existing data before loading')

    args = parser.parse_args()

    return load_csv_to_database(
        csv_file=args.csv,
        db_host=args.host,
        db_user=args.user,
        db_password=args.password,
        db_name=args.database,
        clear_existing=args.clear
    )


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
