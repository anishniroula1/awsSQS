# test_dbconnection.py
import pytest
from sql_connection import DBConnection, Base  # Import your DBConnection class and Base
from your_model_module import YourModel  # Import your SQLAlchemy model classes

# Constants
TEST_DATABASE_URL = "postgresql+psycopg2://user:password@localhost/test_db"

@pytest.fixture(scope='module')
def db_connection():
    """Fixture to create a database connection and tear it down after tests."""
    db = DBConnection(TEST_DATABASE_URL)
    Base.metadata.create_all(db.engine)  # Create tables for testing
    yield db
    Base.metadata.drop_all(db.engine)  # Drop tables after tests
    db.close()

def test_insert_single_record(db_connection):
    """Test inserting a single record."""
    test_record = {'column1': 'value1', 'column2': 'value2'}
    db_connection.insert_single_record(test_record, YourModel)
    # Query and assert to check if the record was inserted
    result = db_connection.session.query(YourModel).filter_by(column1='value1').first()
    assert result is not None
    assert result.column1 == 'value1'
    assert result.column2 == 'value2'

def test_bulk_insert_records(db_connection):
    """Test bulk inserting records."""
    test_records = [
        {'column1': 'value1', 'column2': 'value2'},
        {'column1': 'value3', 'column2': 'value4'}
    ]
    db_connection.bulk_insert_records(test_records, YourModel)
    # Query and assert to check if the records were inserted
    results = db_connection.session.query(YourModel).all()
    assert len(results) == 2

# Additional tests for bulk_update_records, update_columns_record, etc.

def test_close(db_connection):
    """Test closing the connection."""
    db_connection.close()
    with pytest.raises(Exception):
        # Attempting to execute a query after closing should raise an exception
        db_connection.session.query(YourModel).all()
