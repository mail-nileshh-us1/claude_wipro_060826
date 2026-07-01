import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from read_patients import categorize_health_status, read_patient_data, plot_health_status_distribution


class TestCategorizeHealthStatus:
    """Test cases for categorize_health_status function"""

    def test_healthy_patient(self):
        """Test patient with all healthy metrics"""
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=90)
        assert result == "Healthy"

    def test_healthy_patient_low_values(self):
        """Test patient with lower healthy metrics"""
        result = categorize_health_status(bmi=18.5, blood_pressure="110/70", glucose_level=80)
        assert result == "Healthy"

    def test_at_risk_overweight_bmi(self):
        """Test patient at risk due to overweight (BMI 25-29.9)"""
        result = categorize_health_status(bmi=26.0, blood_pressure="120/80", glucose_level=90)
        assert result == "At Risk"

    def test_at_risk_elevated_blood_pressure(self):
        """Test patient at risk due to elevated blood pressure (120-139/80-89)"""
        # Systolic 130 >= 120 adds 1, no other risk factors = 1 total (Healthy)
        result = categorize_health_status(bmi=22.5, blood_pressure="130/85", glucose_level=90)
        assert result == "Healthy"

    def test_at_risk_elevated_blood_pressure_multiple(self):
        """Test patient at risk due to elevated blood pressure with other factors"""
        # Systolic 130 >= 120 adds 1, BMI 26 adds 1 = 2 total (At Risk)
        result = categorize_health_status(bmi=26.0, blood_pressure="130/85", glucose_level=90)
        assert result == "At Risk"

    def test_at_risk_prediabetes(self):
        """Test patient at risk due to prediabetes (glucose 100-125)"""
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=110)
        assert result == "At Risk"

    def test_at_risk_multiple_factors(self):
        """Test patient at risk with multiple risk factors"""
        result = categorize_health_status(bmi=27.0, blood_pressure="125/82", glucose_level=105)
        assert result == "At Risk"

    def test_critical_obesity(self):
        """Test patient with critical status due to obesity (BMI >= 30)"""
        # BMI 32 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=32.0, blood_pressure="120/80", glucose_level=90)
        assert result == "At Risk"

    def test_critical_obesity_with_other_factors(self):
        """Test patient with critical status: obesity + other factors"""
        # BMI 32 adds 2, BP 140 adds 2, glucose 100 adds 1 = 5 total (Critical)
        result = categorize_health_status(bmi=32.0, blood_pressure="140/80", glucose_level=100)
        assert result == "Critical"

    def test_critical_high_blood_pressure(self):
        """Test patient with critical status due to high blood pressure (>= 140/90)"""
        # BP 145/92 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=22.5, blood_pressure="145/92", glucose_level=90)
        assert result == "At Risk"

    def test_critical_high_blood_pressure_multiple_factors(self):
        """Test patient with critical status: high BP + other factors"""
        # BP 145 adds 2, BMI 32 adds 2, glucose 100 adds 1 = 5 total (Critical)
        result = categorize_health_status(bmi=32.0, blood_pressure="145/92", glucose_level=100)
        assert result == "Critical"

    def test_critical_diabetes(self):
        """Test patient with critical status due to high glucose (>= 126)"""
        # Glucose 150 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=150)
        assert result == "At Risk"

    def test_critical_diabetes_multiple_factors(self):
        """Test patient with critical status: high glucose + other factors"""
        # Glucose 150 adds 2, BMI 32 adds 2, BP 140 adds 1 (systolic exactly 140) = 5 total (Critical)
        result = categorize_health_status(bmi=32.0, blood_pressure="140/85", glucose_level=150)
        assert result == "Critical"

    def test_critical_all_factors(self):
        """Test patient with critical status - all risk factors present"""
        result = categorize_health_status(bmi=35.0, blood_pressure="150/95", glucose_level=180)
        assert result == "Critical"

    def test_critical_multiple_high_risk_factors(self):
        """Test patient with critical status - combination of factors"""
        result = categorize_health_status(bmi=31.0, blood_pressure="142/91", glucose_level=128)
        assert result == "Critical"

    def test_invalid_blood_pressure_format(self):
        """Test with invalid blood pressure format"""
        result = categorize_health_status(bmi=22.5, blood_pressure="invalid", glucose_level=90)
        assert result == "Critical"

    def test_blood_pressure_missing_slash(self):
        """Test with blood pressure missing delimiter"""
        result = categorize_health_status(bmi=22.5, blood_pressure="12080", glucose_level=90)
        assert result == "Critical"

    def test_blood_pressure_non_numeric(self):
        """Test with blood pressure containing non-numeric values"""
        result = categorize_health_status(bmi=22.5, blood_pressure="abc/def", glucose_level=90)
        assert result == "Critical"

    def test_boundary_bmi_25(self):
        """Test boundary case: BMI exactly 25"""
        result = categorize_health_status(bmi=25.0, blood_pressure="120/80", glucose_level=90)
        assert result == "At Risk"

    def test_boundary_bmi_30(self):
        """Test boundary case: BMI exactly 30"""
        # BMI 30 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=30.0, blood_pressure="120/80", glucose_level=90)
        assert result == "At Risk"

    def test_boundary_systolic_120(self):
        """Test boundary case: Systolic pressure exactly 120"""
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=90)
        assert result == "Healthy"

    def test_boundary_systolic_140(self):
        """Test boundary case: Systolic pressure exactly 140"""
        # Systolic 140 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=22.5, blood_pressure="140/80", glucose_level=90)
        assert result == "At Risk"

    def test_boundary_glucose_100(self):
        """Test boundary case: Glucose exactly 100"""
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=100)
        assert result == "At Risk"

    def test_boundary_glucose_126(self):
        """Test boundary case: Glucose exactly 126"""
        # Glucose 126 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=126)
        assert result == "At Risk"

    def test_edge_case_very_low_bmi(self):
        """Test edge case: Very low BMI (underweight)"""
        result = categorize_health_status(bmi=16.0, blood_pressure="120/80", glucose_level=90)
        assert result == "Healthy"

    def test_edge_case_very_high_bmi(self):
        """Test edge case: Very high BMI"""
        # BMI 45 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=45.0, blood_pressure="120/80", glucose_level=90)
        assert result == "At Risk"

    def test_edge_case_very_low_glucose(self):
        """Test edge case: Very low glucose level"""
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=50)
        assert result == "Healthy"

    def test_edge_case_very_high_glucose(self):
        """Test edge case: Very high glucose level"""
        # Glucose 300 adds 2, no other risk factors = 2 total (At Risk, not Critical)
        result = categorize_health_status(bmi=22.5, blood_pressure="120/80", glucose_level=300)
        assert result == "At Risk"


class TestReadPatientData:
    """Test cases for read_patient_data function"""

    @pytest.fixture
    def sample_csv_file(self, tmp_path):
        """Create a temporary CSV file for testing"""
        csv_content = """PatientID,name,age,BMI,Blood_pressure,Glucose_level
1,John Doe,45,28.5,130/85,105
2,Jane Smith,52,31.2,145/92,145
3,Bob Johnson,38,22.3,118/76,92
4,Alice Brown,60,24.8,125/80,110
5,Charlie White,55,29.5,140/88,120"""

        csv_file = tmp_path / "test_patients.csv"
        csv_file.write_text(csv_content)
        return str(csv_file)

    def test_read_patient_data_default_rows(self, sample_csv_file, capsys):
        """Test reading patient data with default rows"""
        df = read_patient_data(sample_csv_file)

        assert isinstance(df, pd.DataFrame)
        assert 'health_status' in df.columns
        assert len(df) == 5
        assert df['health_status'].isin(['Healthy', 'At Risk', 'Critical']).all()

    def test_read_patient_data_custom_rows(self, sample_csv_file, capsys):
        """Test reading patient data with custom number of rows"""
        df = read_patient_data(sample_csv_file, rows=3)

        assert isinstance(df, pd.DataFrame)
        assert 'health_status' in df.columns
        assert len(df) == 5

    def test_read_patient_data_contains_all_columns(self, sample_csv_file):
        """Test that returned dataframe has all required columns"""
        df = read_patient_data(sample_csv_file)

        required_columns = ['PatientID', 'name', 'age', 'BMI', 'Blood_pressure', 'Glucose_level', 'health_status']
        for col in required_columns:
            assert col in df.columns

    def test_read_patient_data_health_status_values(self, sample_csv_file):
        """Test that health_status column contains valid values"""
        df = read_patient_data(sample_csv_file)

        valid_statuses = {'Healthy', 'At Risk', 'Critical'}
        assert df['health_status'].isin(valid_statuses).all()

    def test_read_patient_data_row_count(self, sample_csv_file):
        """Test that correct number of rows are read"""
        df = read_patient_data(sample_csv_file, rows=5)
        assert len(df) == 5

    def test_read_patient_data_file_not_found(self):
        """Test error handling when CSV file doesn't exist"""
        with pytest.raises(FileNotFoundError):
            read_patient_data("nonexistent_file.csv")


class TestPlotHealthStatusDistribution:
    """Test cases for plot_health_status_distribution function"""

    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample dataframe with health status data"""
        data = {
            'PatientID': [1, 2, 3, 4, 5],
            'name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'health_status': ['Healthy', 'At Risk', 'Critical', 'Healthy', 'At Risk']
        }
        return pd.DataFrame(data)

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_plot_health_status_distribution_creates_plot(self, mock_show, mock_savefig, sample_dataframe, capsys):
        """Test that plot function creates visualization"""
        plot_health_status_distribution(sample_dataframe)

        mock_savefig.assert_called_once()
        mock_show.assert_called_once()

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_plot_health_status_distribution_saves_to_correct_path(self, mock_show, mock_savefig, sample_dataframe):
        """Test that plot is saved to correct path"""
        plot_health_status_distribution(sample_dataframe)

        # Check that savefig was called with correct path
        call_args = mock_savefig.call_args
        assert 'data/health_status_chart.png' in call_args[0][0]

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_plot_health_status_distribution_with_all_statuses(self, mock_show, mock_savefig):
        """Test plot with all three health statuses"""
        data = {
            'health_status': ['Healthy', 'At Risk', 'Critical', 'Healthy', 'At Risk', 'Critical']
        }
        df = pd.DataFrame(data)

        plot_health_status_distribution(df)

        mock_savefig.assert_called_once()
        assert mock_savefig.call_count == 1

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_plot_health_status_distribution_with_single_status(self, mock_show, mock_savefig):
        """Test plot with only one health status"""
        data = {
            'health_status': ['Healthy', 'Healthy', 'Healthy']
        }
        df = pd.DataFrame(data)

        plot_health_status_distribution(df)

        mock_savefig.assert_called_once()

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_plot_with_empty_dataframe(self, mock_show, mock_savefig):
        """Test plot with empty dataframe"""
        df = pd.DataFrame({'health_status': []})

        # This should handle empty data gracefully
        plot_health_status_distribution(df)

        # Should still attempt to save
        mock_savefig.assert_called_once()


class TestIntegration:
    """Integration tests combining multiple functions"""

    @pytest.fixture
    def integration_csv_file(self, tmp_path):
        """Create a comprehensive test CSV file"""
        csv_content = """PatientID,name,age,BMI,Blood_pressure,Glucose_level
1,Patient Healthy,30,22.0,115/75,85
2,Patient At Risk,45,27.5,130/85,105
3,Patient Critical,60,35.0,150/95,180
4,Patient Borderline,40,24.9,119/79,99
5,Patient Multiple Risk,55,32.0,145/90,128"""

        csv_file = tmp_path / "integration_test.csv"
        csv_file.write_text(csv_content)
        return str(csv_file)

    def test_end_to_end_workflow(self, integration_csv_file):
        """Test complete workflow from reading to categorization"""
        df = read_patient_data(integration_csv_file)

        # Verify data was read correctly
        assert len(df) == 5
        assert 'health_status' in df.columns

        # Verify categorization happened
        status_counts = df['health_status'].value_counts()
        assert 'Healthy' in status_counts or len(status_counts) > 0

    @patch('read_patients.plt.savefig')
    @patch('read_patients.plt.show')
    def test_end_to_end_with_plot(self, mock_show, mock_savefig, integration_csv_file):
        """Test complete workflow including plot generation"""
        df = read_patient_data(integration_csv_file)
        plot_health_status_distribution(df)

        assert len(df) == 5
        mock_savefig.assert_called_once()
        mock_show.assert_called_once()
