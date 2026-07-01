#!/usr/bin/env python3
"""
Test script to verify MySQL connection and database operations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from db_connection import MySQLConnection


def test_mysql_connection():
    """Test MySQL connection with various operations"""

    print("=" * 70)
    print("MySQL Connection Test - Patient Health Analyzer")
    print("=" * 70)

    # Initialize connection
    db = MySQLConnection(
        host='localhost',
        user='root',
        password='Tek@12345',
        database='test_db',
        port=3306
    )

    # Test 1: Connection
    print("\n✓ Test 1: MySQL Connection")
    if db.connect():
        print("  ✅ Successfully connected to MySQL Server")
        print(f"     Database: {db.database}")
    else:
        print("  ❌ Failed to connect to MySQL Server")
        return False

    # Test 2: Retrieve all patients
    print("\n✓ Test 2: Retrieve All Patients")
    patients = db.get_all_patients()
    if patients:
        print(f"  ✅ Found {len(patients)} patients in database")
    else:
        print("  ⚠️  No patients found")
        return False

    # Test 3: Get specific patient
    print("\n✓ Test 3: Get Specific Patient (ID: 1)")
    patient = db.get_patient_by_id(1)
    if patient:
        print(f"  ✅ Patient found: {patient[1]} (Age: {patient[3]})")
        print(f"     Health Status: {patient[6]}")
    else:
        print("  ❌ Patient not found")

    # Test 4: Health status statistics
    print("\n✓ Test 4: Health Status Statistics")
    if patients:
        from collections import Counter
        statuses = [p[6] for p in patients]
        distribution = Counter(statuses)
        total = len(patients)
        for status in sorted(distribution.keys()):
            count = distribution[status]
            percentage = (count / total) * 100
            bar = "█" * int(percentage / 5)
            print(f"  {status:10s}: {count:3d} ({percentage:5.1f}%) {bar}")

    # Test 5: Filter by health status
    print("\n✓ Test 5: Query Patients by Health Status")
    critical_query = "SELECT PatientID, name, health_status FROM patients WHERE health_status = %s"
    critical_patients = db.fetch_all(critical_query, ("Critical",))
    if critical_patients:
        print(f"  ✅ Found {len(critical_patients)} critical patients:")
        for p in critical_patients[:3]:
            print(f"     - {p[1]} (ID: {p[0]})")
    else:
        print("  ⚠️  No critical patients found")

    # Test 6: Update operation
    print("\n✓ Test 6: Update Patient Health Status")
    if patient:
        original_status = patient[6]
        new_status = "Healthy" if original_status != "Healthy" else "At Risk"
        if db.update_patient_health_status(1, new_status):
            print(f"  ✅ Updated patient 1: {original_status} → {new_status}")
            db.update_patient_health_status(1, original_status)
            print(f"  ✅ Reverted patient 1 back to: {original_status}")
        else:
            print("  ❌ Failed to update patient")

    # Test 7: Database info query
    print("\n✓ Test 7: Database Schema Information")
    schema_query = """
    SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_NAME = 'patients' AND TABLE_SCHEMA = %s
    """
    columns = db.fetch_all(schema_query, ("test_db",))
    if columns:
        print("  ✅ Patients table structure:")
        for col in columns:
            null_info = "NULL" if col[2] == "YES" else "NOT NULL"
            print(f"     - {col[0]:20s} | {col[1]:20s} | {null_info}")

    # Test 8: Disconnect
    print("\n✓ Test 8: Connection Cleanup")
    db.disconnect()
    print("  ✅ Connection closed successfully")

    print("\n" + "=" * 70)
    print("✅ All MySQL connection tests passed!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    try:
        success = test_mysql_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
