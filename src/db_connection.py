import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()


class MySQLConnection:
    """MySQL Database Connection Handler"""

    def __init__(self, host=None, user=None, password=None, database=None, port=3306):
        """
        Initialize MySQL connection parameters.

        Args:
            host (str): MySQL server host (default from .env or 'localhost')
            user (str): MySQL user (default from .env or 'root')
            password (str): MySQL password (default from .env or '')
            database (str): Database name (default from .env)
            port (int): MySQL port (default: 3306)
        """
        self.host = host or os.getenv('DB_HOST', 'localhost')
        self.user = user or os.getenv('DB_USER', 'root')
        self.password = password or os.getenv('DB_PASSWORD', '')
        self.database = database or os.getenv('DB_NAME', 'patient_health_db')
        self.port = port
        self.connection = None

    def connect(self):
        """
        Establish connection to MySQL server.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            if self.connection.is_connected():
                db_info = self.connection.get_server_info()
                print(f"Successfully connected to MySQL Server version {db_info}")
                print(f"Connected to database: {self.database}")
                return True
        except Error as e:
            print(f"Error while connecting to MySQL: {e}")
            return False

    def disconnect(self):
        """Close MySQL connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

    def execute_query(self, query, params=None):
        """
        Execute a SQL query.

        Args:
            query (str): SQL query to execute
            params (tuple): Query parameters for parameterized queries

        Returns:
            bool: True if execution successful, False otherwise
        """
        if not self.connection or not self.connection.is_connected():
            print("Connection not established. Please connect first.")
            return False

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            print(f"Query executed successfully. Rows affected: {cursor.rowcount}")
            cursor.close()
            return True
        except Error as e:
            print(f"Error executing query: {e}")
            return False

    def fetch_all(self, query, params=None):
        """
        Fetch all results from a SELECT query.

        Args:
            query (str): SQL SELECT query
            params (tuple): Query parameters for parameterized queries

        Returns:
            list: List of tuples containing query results, or None if error
        """
        if not self.connection or not self.connection.is_connected():
            print("Connection not established. Please connect first.")
            return None

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def fetch_one(self, query, params=None):
        """
        Fetch single result from a SELECT query.

        Args:
            query (str): SQL SELECT query
            params (tuple): Query parameters for parameterized queries

        Returns:
            tuple: Single row result, or None if no result or error
        """
        if not self.connection or not self.connection.is_connected():
            print("Connection not established. Please connect first.")
            return None

        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            print(f"Error fetching data: {e}")
            return None

    def create_patients_table(self):
        """Create patients table if it doesn't exist"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS patients (
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
        """
        return self.execute_query(create_table_query)

    def insert_patient(self, name, age, bmi, blood_pressure, glucose_level, health_status):
        """
        Insert a patient record into database.

        Args:
            name (str): Patient name
            age (int): Patient age
            bmi (float): Body Mass Index
            blood_pressure (str): Blood pressure in format "systolic/diastolic"
            glucose_level (int): Glucose level in mg/dL
            health_status (str): Health status category

        Returns:
            bool: True if insertion successful, False otherwise
        """
        insert_query = """
        INSERT INTO patients (name, age, BMI, Blood_pressure, Glucose_level, health_status)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, age, bmi, blood_pressure, glucose_level, health_status)
        return self.execute_query(insert_query, params)

    def get_all_patients(self):
        """
        Retrieve all patients from database.

        Returns:
            list: List of patient records, or None if error
        """
        query = "SELECT * FROM patients"
        return self.fetch_all(query)

    def get_patient_by_id(self, patient_id):
        """
        Retrieve a patient by ID.

        Args:
            patient_id (int): Patient ID

        Returns:
            tuple: Patient record, or None if not found or error
        """
        query = "SELECT * FROM patients WHERE PatientID = %s"
        return self.fetch_one(query, (patient_id,))

    def update_patient_health_status(self, patient_id, health_status):
        """
        Update patient health status.

        Args:
            patient_id (int): Patient ID
            health_status (str): New health status

        Returns:
            bool: True if update successful, False otherwise
        """
        update_query = """
        UPDATE patients SET health_status = %s WHERE PatientID = %s
        """
        return self.execute_query(update_query, (health_status, patient_id))

    def delete_patient(self, patient_id):
        """
        Delete a patient record.

        Args:
            patient_id (int): Patient ID to delete

        Returns:
            bool: True if deletion successful, False otherwise
        """
        delete_query = "DELETE FROM patients WHERE PatientID = %s"
        return self.execute_query(delete_query, (patient_id,))


def get_db_connection(host=None, user=None, password=None, database=None, port=3306):
    """
    Create and return a MySQLConnection instance.

    Args:
        host (str): MySQL server host
        user (str): MySQL user
        password (str): MySQL password
        database (str): Database name
        port (int): MySQL port

    Returns:
        MySQLConnection: Database connection instance
    """
    return MySQLConnection(host, user, password, database, port)


if __name__ == "__main__":
    db = MySQLConnection()
    if db.connect():
        db.create_patients_table()
        print("Database setup complete!")
        db.disconnect()
    else:
        print("Failed to connect to database")
