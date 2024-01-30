import pytest
from unittest.mock import MagicMock, create_autospec
from sqlalchemy.orm import Session

from db_connection import DBConnection
from completed.users import User

@pytest.fixture
def mock_session():
    # Create a mock session object
    session = create_autospec(Session, instance=True)
    session.query.return_value.filter_by.return_value.first.return_value = None
    return session

@pytest.fixture
def db_connection(mock_session):
    # Create an instance of DBConnection with a mocked session
    db_conn = DBConnection('postgresql://user:pass@localhost/dbname')
    db_conn.session = mock_session
    return db_conn

def test_get_or_create_user_new_user(db_connection, mock_session):
    # Test the creation of a new user
    username = 'new_user'
    db_connection.get_or_create_user(username)

    # Check if a new User object was added to the session
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()

def test_get_or_create_user_existing_user(db_connection, mock_session):
    # Test the retrieval of an existing user
    username = 'existing_user'
    existing_user = User(username=username)
    mock_session.query.return_value.filter_by.return_value.first.return_value = existing_user

    user_id = db_connection.get_or_create_user(username)

    # Check if the correct user ID is returned without adding a new user
    assert user_id == existing_user.id
    mock_session.add.assert_not_called()
