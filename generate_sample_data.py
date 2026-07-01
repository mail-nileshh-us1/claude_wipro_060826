#!/usr/bin/env python3
"""
Generate sample patient data and export to CSV
"""

import pandas as pd
import random
import os
from datetime import datetime, timedelta


def generate_sample_patients(num_patients=50):
    """Generate sample patient data with realistic health metrics"""

    first_names = [
        'John', 'Sarah', 'Michael', 'Emma', 'David', 'Lisa', 'James', 'Maria',
        'Robert', 'Jennifer', 'William', 'Patricia', 'Richard', 'Barbara',
        'Joseph', 'Susan', 'Thomas', 'Jessica', 'Charles', 'Sarah', 'Christopher',
        'Karen', 'Daniel', 'Nancy', 'Matthew', 'Betty', 'Anthony', 'Sandra',
        'Mark', 'Ashley', 'Donald', 'Kimberly', 'Steven', 'Donna', 'Paul',
        'Carol', 'Andrew', 'Michelle', 'Joshua', 'Amanda', 'Kenneth', 'Melissa',
        'Kevin', 'Deborah', 'Brian', 'Stephanie', 'George', 'Rebecca', 'Edward',
        'Sharon', 'Ronald', 'Laura'
    ]

    last_names = [
        'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller',
        'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez',
        'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
        'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark',
        'Ramirez', 'Lewis', 'Robinson', 'Young', 'Allen', 'King', 'Wright',
        'Scott', 'Torres', 'Peterson', 'Phillips', 'Campbell', 'Parker',
        'Evans', 'Edwards', 'Collins', 'Reyes', 'Stewart', 'Morris', 'Morales'
    ]

    patients = []

    for i in range(num_patients):
        patient_id = i + 1
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        age = random.randint(18, 85)

        # BMI distribution (realistic: most normal-overweight, some obese)
        bmi_range = random.choices(
            [1, 2, 3],  # 1=Healthy, 2=Overweight, 3=Obese
            weights=[40, 40, 20],  # 40% healthy, 40% overweight, 20% obese
            k=1
        )[0]

        if bmi_range == 1:
            bmi = round(random.uniform(18.5, 24.9), 1)
        elif bmi_range == 2:
            bmi = round(random.uniform(25.0, 29.9), 1)
        else:
            bmi = round(random.uniform(30.0, 40.0), 1)

        # Blood pressure (realistic distribution)
        systolic = random.choices(
            [random.randint(110, 119), random.randint(120, 139), random.randint(140, 180)],
            weights=[50, 30, 20],
            k=1
        )[0]
        diastolic = random.choices(
            [random.randint(70, 79), random.randint(80, 89), random.randint(90, 120)],
            weights=[50, 30, 20],
            k=1
        )[0]
        blood_pressure = f"{systolic}/{diastolic}"

        # Glucose level (realistic distribution)
        glucose_range = random.choices(
            [1, 2, 3],  # 1=Normal, 2=Prediabetes, 3=Diabetes
            weights=[60, 25, 15],
            k=1
        )[0]

        if glucose_range == 1:
            glucose_level = random.randint(70, 99)
        elif glucose_range == 2:
            glucose_level = random.randint(100, 125)
        else:
            glucose_level = random.randint(126, 300)

        patients.append({
            'PatientID': patient_id,
            'name': name,
            'age': age,
            'BMI': bmi,
            'Blood_pressure': blood_pressure,
            'Glucose_level': glucose_level
        })

    return pd.DataFrame(patients)


def save_to_csv(df, filepath='data/generated_patients.csv'):
    """Save dataframe to CSV file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False)
    print(f"✅ Saved {len(df)} patients to {filepath}")
    return filepath


def display_sample_data(df, num_rows=10):
    """Display sample data from dataframe"""
    print("\n" + "=" * 80)
    print("Sample Patient Data")
    print("=" * 80)
    print(df.head(num_rows).to_string(index=False))
    print(f"\n... and {len(df) - num_rows} more patients")

    print("\n" + "-" * 80)
    print("Data Summary Statistics:")
    print("-" * 80)
    print(f"Total Patients: {len(df)}")
    print(f"\nAge Statistics:")
    print(f"  Mean: {df['age'].mean():.1f} years")
    print(f"  Min: {df['age'].min()} years")
    print(f"  Max: {df['age'].max()} years")

    print(f"\nBMI Statistics:")
    print(f"  Mean: {df['BMI'].mean():.1f}")
    print(f"  Min: {df['BMI'].min():.1f}")
    print(f"  Max: {df['BMI'].max():.1f}")

    print(f"\nGlucose Level Statistics:")
    print(f"  Mean: {df['Glucose_level'].mean():.1f} mg/dL")
    print(f"  Min: {df['Glucose_level'].min()} mg/dL")
    print(f"  Max: {df['Glucose_level'].max()} mg/dL")


def main():
    """Generate and save sample patient data"""
    print("=" * 80)
    print("Patient Health Analyzer - Sample Data Generator")
    print("=" * 80)

    # Generate sample data
    print("\n[Step 1] Generating sample patient data...")
    df = generate_sample_patients(num_patients=50)
    print(f"✅ Generated {len(df)} patient records")

    # Display statistics
    display_sample_data(df, num_rows=10)

    # Save to CSV
    print("\n[Step 2] Exporting to CSV...")
    csv_file = save_to_csv(df)

    print("\n" + "=" * 80)
    print("✅ Sample data generation complete!")
    print("=" * 80)

    return df, csv_file


if __name__ == "__main__":
    df, csv_file = main()
