from completed.users import Base, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DBConnection:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        # Ensure the tables are created
        Base.metadata.create_all(self.engine)

    def get_or_create_user(self, username):
        # Check if user exists
        user = self.session.query(User).filter_by(username=username).first()

        # If user exists, return the user ID
        if user:
            return user.id

        # If user does not exist, create a new user
        new_user = User(username=username)
        self.session.add(new_user)
        self.session.commit()

        return new_user.id

    def close(self):
        self.session.close()
