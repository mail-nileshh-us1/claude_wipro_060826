# Claude Code Configuration

## Project Overview
Patient Health Analyzer - A healthcare application for analyzing patient health metrics and categorizing health status.

## Database Configuration

### MCP MySQL Server
This project uses Model Context Protocol (MCP) for Claude to interact with MySQL databases.

**Configuration Files:**
- `.claude/settings.json` - Project-level MCP server configuration
- `.claude/mcp.json` - MySQL MCP server details
- `.env.example` - Environment variable template

### Environment Setup
Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=patient_health_db
DB_PORT=3306
```

### Python Database Module
For direct Python connections, use `src/db_connection.py`:
```python
from src.db_connection import MySQLConnection

db = MySQLConnection()
if db.connect():
    db.create_patients_table()
    db.insert_patient('John Doe', 45, 28.5, '130/85', 105, 'At Risk')
```

## Testing

### Run All Tests
```bash
source venv/bin/activate
pytest -v
```

### Run Specific Test Suites
```bash
# Health functions tests
pytest tests/test_health_functions.py -v

# Database connection tests
pytest tests/test_db_connection.py -v
```

## Project Structure
```
Patient_health_analyser/
├── src/
│   ├── read_patients.py          # Health status categorization
│   ├── db_connection.py           # MySQL connection module
│   └── __init__.py
├── tests/
│   ├── test_health_functions.py   # 41 health function tests
│   ├── test_db_connection.py      # 23 database tests
│   └── __init__.py
├── data/
│   ├── sample_patients.csv        # Sample patient data
│   └── health_status_chart.png    # Health distribution chart
├── .claude/
│   ├── settings.json              # Project MCP configuration
│   └── mcp.json                   # MySQL MCP server config
├── .env.example                   # Environment template
├── requirements.txt               # Python dependencies
├── CLAUDE.md                      # This file
└── README.md
```

## Key Functions

### Health Status Categorization
- `categorize_health_status(bmi, blood_pressure, glucose_level)` - Categorizes patient health
- Risk factors: BMI (25-29.9: +1, ≥30: +2), Blood Pressure (120-139/80-89: +1, ≥140/90: +2), Glucose (100-125: +1, ≥126: +2)
- Status: Healthy (0-1), At Risk (2-4), Critical (≥5)

### Database Operations
- `MySQLConnection.create_patients_table()` - Initialize database schema
- `MySQLConnection.insert_patient()` - Add new patient
- `MySQLConnection.get_all_patients()` - Retrieve all patients
- `MySQLConnection.get_patient_by_id()` - Get specific patient
- `MySQLConnection.update_patient_health_status()` - Update health status
- `MySQLConnection.delete_patient()` - Remove patient record

## Git Workflow

### Branches
- `main` - Production-ready code with test suite
- `feature` - Development branch with database integration

### Commit History
1. Initial commit - Project setup with sample data
2. Add comprehensive pytest test cases for health functions (41 tests)
3. Add MySQL database connection module (23 tests)

## MCP Server Tools Available
When MCP MySQL is configured, the following tools are available in Claude Code:
- **query** - Execute SELECT queries
- **execute** - Execute INSERT/UPDATE/DELETE queries
- **list_tables** - Show all tables in database
- **describe_table** - Show table schema
- **insert_record** - Insert new records
- **update_record** - Update existing records
- **delete_record** - Delete records

## Dependencies
- Python 3.12+
- MySQL 8.0+
- pandas, numpy, matplotlib, scikit-learn
- pytest for testing
- mysql-connector-python for database connection
- python-dotenv for environment configuration

## Notes
- All database queries use parameterized statements to prevent SQL injection
- Connection handling is automatic with context manager support
- Tests use mocking to avoid requiring a live database during testing
- Health status categorization is based on WHO/medical guidelines

## Future Enhancements
- Add Flask API for REST endpoints
- Implement data visualization dashboard
- Add user authentication system
- Create scheduled data analysis reports
