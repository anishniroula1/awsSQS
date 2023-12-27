import pytest

from db_connection import DBConnection
from users import User, get_or_create_user

# Assuming you have a setup for test database URL
TEST_DATABASE_URL = "postgresql://user:password@localhost/test_db"

@pytest.fixture(scope="module")
def db_session():
    connection = DBConnection(TEST_DATABASE_URL)
    yield connection.session
    connection.session.close()

def test_create_new_user(db_session):
    username = "new_test_user"
    user_id = get_or_create_user(db_session, username)
    assert user_id is not None
    # Further checks can be added to ensure the user is properly created

def test_get_existing_user(db_session):
    username = "existing_test_user"
    # Create a user first
    existing_user = User(username=username)
    db_session.add(existing_user)
    db_session.commit()

    user_id = get_or_create_user(db_session, existing_user.username)
    assert user_id == existing_user.id
    # Further checks can be added to ensure the correct user ID is returned
