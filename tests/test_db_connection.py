import pytest
import sys
import os
from unittest.mock import patch, MagicMock, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from db_connection import MySQLConnection, get_db_connection


class TestMySQLConnection:
    """Test cases for MySQLConnection class"""

    @pytest.fixture
    def mock_connector(self):
        """Mock mysql.connector module"""
        with patch('db_connection.mysql.connector') as mock:
            yield mock

    def test_initialization_with_defaults(self):
        """Test MySQLConnection initialization with default values"""
        with patch.dict(os.environ, {}, clear=True):
            conn = MySQLConnection()
            assert conn.host == 'localhost'
            assert conn.user == 'root'
            assert conn.password == ''
            assert conn.database == 'patient_health_db'
            assert conn.port == 3306

    def test_initialization_with_custom_values(self):
        """Test MySQLConnection initialization with custom values"""
        conn = MySQLConnection(
            host='192.168.1.1',
            user='admin',
            password='secret',
            database='health_db',
            port=3307
        )
        assert conn.host == '192.168.1.1'
        assert conn.user == 'admin'
        assert conn.password == 'secret'
        assert conn.database == 'health_db'
        assert conn.port == 3307

    def test_initialization_with_env_variables(self):
        """Test MySQLConnection initialization with environment variables"""
        env_vars = {
            'DB_HOST': '192.168.1.100',
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_NAME': 'test_db'
        }
        with patch.dict(os.environ, env_vars):
            with patch('db_connection.load_dotenv'):
                conn = MySQLConnection()
                assert conn.host == '192.168.1.100'
                assert conn.user == 'testuser'
                assert conn.password == 'testpass'
                assert conn.database == 'test_db'

    @patch('db_connection.mysql.connector.connect')
    def test_connect_success(self, mock_connect, capsys):
        """Test successful MySQL connection"""
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connection.get_server_info.return_value = '8.0.28'
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        result = conn.connect()

        assert result is True
        assert conn.connection is not None
        mock_connect.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_connect_failure(self, mock_connect, capsys):
        """Test failed MySQL connection"""
        from mysql.connector import Error
        mock_connect.side_effect = Error("Connection refused")

        conn = MySQLConnection()
        result = conn.connect()

        assert result is False
        captured = capsys.readouterr()
        assert "Error while connecting to MySQL" in captured.out

    @patch('db_connection.mysql.connector.connect')
    def test_disconnect(self, mock_connect):
        """Test MySQL disconnection"""
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        conn.disconnect()

        mock_connection.close.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_disconnect_when_not_connected(self, mock_connect, capsys):
        """Test disconnect when not connected"""
        conn = MySQLConnection()
        conn.disconnect()

        captured = capsys.readouterr()
        assert "MySQL connection closed" not in captured.out

    @patch('db_connection.mysql.connector.connect')
    def test_execute_query_success(self, mock_connect):
        """Test successful query execution"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.execute_query("INSERT INTO patients (name) VALUES ('John')")

        assert result is True
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_execute_query_with_params(self, mock_connect):
        """Test query execution with parameters"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        conn.execute_query("INSERT INTO patients (name, age) VALUES (%s, %s)", ("John", 30))

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO patients (name, age) VALUES (%s, %s)",
            ("John", 30)
        )

    def test_execute_query_no_connection(self):
        """Test query execution when not connected"""
        conn = MySQLConnection()
        result = conn.execute_query("SELECT * FROM patients")
        assert result is False

    @patch('db_connection.mysql.connector.connect')
    def test_execute_query_error(self, mock_connect, capsys):
        """Test query execution with error"""
        from mysql.connector import Error
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Error("Syntax error")

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.execute_query("INVALID QUERY")

        assert result is False

    @patch('db_connection.mysql.connector.connect')
    def test_fetch_all_success(self, mock_connect):
        """Test fetching all results"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_results = [(1, 'John', 30), (2, 'Jane', 28)]
        mock_cursor.fetchall.return_value = mock_results

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        results = conn.fetch_all("SELECT * FROM patients")

        assert results == mock_results
        mock_cursor.execute.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_fetch_one_success(self, mock_connect):
        """Test fetching single result"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_result = (1, 'John', 30)
        mock_cursor.fetchone.return_value = mock_result

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.fetch_one("SELECT * FROM patients WHERE PatientID = %s", (1,))

        assert result == mock_result

    def test_fetch_all_no_connection(self):
        """Test fetch_all when not connected"""
        conn = MySQLConnection()
        result = conn.fetch_all("SELECT * FROM patients")
        assert result is None

    def test_fetch_one_no_connection(self):
        """Test fetch_one when not connected"""
        conn = MySQLConnection()
        result = conn.fetch_one("SELECT * FROM patients WHERE PatientID = 1")
        assert result is None

    @patch('db_connection.mysql.connector.connect')
    def test_create_patients_table(self, mock_connect):
        """Test creating patients table"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.create_patients_table()

        assert result is True
        mock_cursor.execute.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_insert_patient(self, mock_connect):
        """Test inserting a patient record"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.insert_patient('John Doe', 45, 28.5, '130/85', 105, 'At Risk')

        assert result is True
        mock_cursor.execute.assert_called_once()

    @patch('db_connection.mysql.connector.connect')
    def test_get_all_patients(self, mock_connect):
        """Test retrieving all patients"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_patients = [(1, 'John', 45, 28.5), (2, 'Jane', 52, 31.2)]
        mock_cursor.fetchall.return_value = mock_patients

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        results = conn.get_all_patients()

        assert results == mock_patients

    @patch('db_connection.mysql.connector.connect')
    def test_get_patient_by_id(self, mock_connect):
        """Test retrieving patient by ID"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_patient = (1, 'John', 45, 28.5)
        mock_cursor.fetchone.return_value = mock_patient

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.get_patient_by_id(1)

        assert result == mock_patient

    @patch('db_connection.mysql.connector.connect')
    def test_update_patient_health_status(self, mock_connect):
        """Test updating patient health status"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.update_patient_health_status(1, 'Critical')

        assert result is True

    @patch('db_connection.mysql.connector.connect')
    def test_delete_patient(self, mock_connect):
        """Test deleting a patient record"""
        mock_connection = MagicMock()
        mock_cursor = MagicMock()

        mock_connection.is_connected.return_value = True
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        conn = MySQLConnection()
        conn.connect()
        result = conn.delete_patient(1)

        assert result is True


class TestGetDbConnection:
    """Test cases for get_db_connection function"""

    def test_get_db_connection_default(self):
        """Test getting default database connection"""
        db = get_db_connection()
        assert isinstance(db, MySQLConnection)
        assert db.host == 'localhost'

    def test_get_db_connection_custom(self):
        """Test getting database connection with custom parameters"""
        db = get_db_connection(
            host='remote.server.com',
            user='admin',
            password='secret',
            database='remote_db',
            port=3307
        )
        assert db.host == 'remote.server.com'
        assert db.user == 'admin'
        assert db.password == 'secret'
        assert db.database == 'remote_db'
        assert db.port == 3307
