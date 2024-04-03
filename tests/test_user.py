import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from completed.users import Base, User


@pytest.fixture(scope="session")
def engine(postgresql_proc, request):
    # Connect to the PostgreSQL database provided by pytest-postgresql
    engine = create_engine(postgresql_proc.dsn)
    Base.metadata.create_all(bind=engine)
    return engine


@pytest.fixture(scope="function")
def session(engine):
    # Create a new session for each test
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Rollback and close session after each test
    session.close()
    transaction.rollback()
    connection.close()


def test_user_creation(session):
    # Test creating a User with an ARRAY data type
    user = User(embedding_list=[1.0, 2.0, 3.0])
    session.add(user)
    session.commit()

    # Retrieve and assert
    db_user = session.query(User).first()
    assert db_user is not None
    assert db_user.embedding_list == [1.0, 2.0, 3.0]


# Additional tests can be added here
