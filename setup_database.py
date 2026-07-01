#!/usr/bin/env python3
"""
Database setup script for Patient Health Analyzer
Initializes MySQL database and creates tables with sample data
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_connection import MySQLConnection
import pandas as pd


def setup_database():
    """Initialize database with tables and sample data"""

    # Connection credentials from mcp.json
    db = MySQLConnection(
        host='localhost',
        user='root',
        password='Tek@12345',
        database='test_db',
        port=3306
    )

    print("=" * 60)
    print("Patient Health Analyzer - Database Setup")
    print("=" * 60)

    # Step 1: Connect to MySQL
    print("\n[Step 1] Connecting to MySQL Server...")
    if not db.connect():
        print("❌ Failed to connect to MySQL server")
        return False
    print("✅ Connected successfully")

    # Step 2: Create patients table
    print("\n[Step 2] Creating patients table...")
    if db.create_patients_table():
        print("✅ Patients table created/verified")
    else:
        print("❌ Failed to create patients table")
        return False

    # Step 3: Load sample data from CSV
    print("\n[Step 3] Loading sample patient data...")
    try:
        df = pd.read_csv('data/sample_patients.csv')
        print(f"   Found {len(df)} patients in CSV file")

        # Apply health status categorization
        from read_patients import categorize_health_status
        df['health_status'] = df.apply(
            lambda row: categorize_health_status(
                row['BMI'],
                row['Blood_pressure'],
                row['Glucose_level']
            ),
            axis=1
        )

        # Insert patients into database
        inserted = 0
        for idx, row in df.iterrows():
            if db.insert_patient(
                name=row['name'],
                age=row['age'],
                bmi=row['BMI'],
                blood_pressure=row['Blood_pressure'],
                glucose_level=row['Glucose_level'],
                health_status=row['health_status']
            ):
                inserted += 1

        print(f"✅ Inserted {inserted}/{len(df)} patients into database")

    except FileNotFoundError:
        print("⚠️  Sample CSV file not found, skipping data load")
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

    # Step 4: Verify data
    print("\n[Step 4] Verifying inserted data...")
    patients = db.get_all_patients()
    if patients:
        print(f"✅ Total patients in database: {len(patients)}")
        print("\nSample records:")
        for patient in patients[:3]:
            print(f"   ID: {patient[0]}, Name: {patient[1]}, Status: {patient[7]}")
    else:
        print("⚠️  No patients found in database")

    # Step 5: Display health status distribution
    if patients:
        print("\n[Step 5] Health Status Distribution:")
        from collections import Counter
        statuses = [p[6] for p in patients]  # health_status is index 6
        distribution = Counter(statuses)
        for status, count in sorted(distribution.items()):
            percentage = (count / len(patients)) * 100
            print(f"   {status:10s}: {count:2d} patients ({percentage:5.1f}%)")

    # Disconnect
    db.disconnect()

    print("\n" + "=" * 60)
    print("✅ Database setup completed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)
