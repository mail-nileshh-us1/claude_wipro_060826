import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_patient_data(file_path, rows=5):
    """
    Read patient data from CSV file and apply health status categorization to every row.

    Args:
        file_path (str): Path to the CSV file
        rows (int): Number of rows to display (default: 5)

    Returns:
        DataFrame: Patient data with health_status column
    """
    df = pd.read_csv(file_path)

    # Apply categorize_health_status to every row and create health_status column
    df['health_status'] = df.apply(
        lambda row: categorize_health_status(row['BMI'], row['Blood_pressure'], row['Glucose_level']),
        axis=1
    )

    print(f"First {rows} rows of patient data with health status:")
    print(df.head(rows))
    return df

def categorize_health_status(bmi, blood_pressure, glucose_level):
    """
    Categorize patient health status based on BMI, Blood Pressure, and Glucose Level.

    Args:
        bmi (float): Body Mass Index
        blood_pressure (str): Blood pressure in format "systolic/diastolic"
        glucose_level (int): Glucose level in mg/dL

    Returns:
        str: Health status - "Healthy", "At Risk", or "Critical"
    """
    # Parse blood pressure
    try:
        systolic, diastolic = map(int, blood_pressure.split('/'))
    except (ValueError, AttributeError):
        return "Critical"

    # Count risk factors
    risk_count = 0

    # BMI categorization
    if bmi >= 30:
        risk_count += 2
    elif bmi >= 25:
        risk_count += 1

    # Blood Pressure categorization
    if systolic >= 140 or diastolic >= 90:
        risk_count += 2
    elif systolic >= 120 or diastolic >= 80:
        risk_count += 1

    # Glucose Level categorization
    if glucose_level >= 126:
        risk_count += 2
    elif glucose_level >= 100:
        risk_count += 1

    # Determine status based on risk count
    if risk_count >= 5:
        return "Critical"
    elif risk_count >= 2:
        return "At Risk"
    else:
        return "Healthy"

def plot_health_status_distribution(df):
    """
    Create a bar chart showing the count of patients by health status category.

    Args:
        df (DataFrame): Patient data dataframe with health_status column
    """
    status_counts = df['health_status'].value_counts()

    plt.figure(figsize=(8, 6))
    colors = {'Healthy': '#2ecc71', 'At Risk': '#f39c12', 'Critical': '#e74c3c'}
    bar_colors = [colors.get(status, '#95a5a6') for status in status_counts.index]

    plt.bar(status_counts.index, status_counts.values, color=bar_colors, edgecolor='black', linewidth=1.5)
    plt.xlabel('Health Status', fontsize=12, fontweight='bold')
    plt.ylabel('Number of Patients', fontsize=12, fontweight='bold')
    plt.title('Patient Distribution by Health Status', fontsize=14, fontweight='bold')
    plt.grid(axis='y', alpha=0.3)

    for i, v in enumerate(status_counts.values):
        plt.text(i, v + 0.1, str(v), ha='center', fontweight='bold')

    plt.tight_layout()
    plt.savefig('data/health_status_chart.png', dpi=300, bbox_inches='tight')
    print("Chart saved to: data/health_status_chart.png")
    plt.show()

if __name__ == "__main__":
    csv_file = "data/sample_patients.csv"
    df = read_patient_data(csv_file, rows=5)
    print("\nAll patients with health status:")
    print(df[['PatientID', 'name', 'health_status']])
    print("\nGenerating health status distribution chart...")
    plot_health_status_distribution(df)
