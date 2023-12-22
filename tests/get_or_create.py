import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from your_model_module import Base, User  # Import the Base and User model

# Constants for test database (use a test database URL)
TEST_DATABASE_URL = "sqlite:///./test_database.db"

@pytest.fixture(scope="module")
def engine():
    return create_engine(TEST_DATABASE_URL)

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    """Create a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

def test_get_or_create_user_existing(session):
    # Setup - add a user to the test database
    existing_user = User(username="existing_user")
    session.add(existing_user)
    session.commit()

    # Test - try to get the existing user
    user_id = get_or_create_user(session, "existing_user")
    assert user_id == existing_user.id

def test_get_or_create_user_new(session):
    # Test - try to get or create a new user
    user_id = get_or_create_user(session, "new_user")
    new_user = session.query(User).get(user_id)
    
    assert new_user is not None
    assert new_user.username == "new_user"
