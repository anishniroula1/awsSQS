from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)

    def __repr__(self):
        return f"<User(username='{self.username}')>"
    

def get_or_create_user(session, username):
    # Check if the user exists
    user = session.query(User).filter_by(username=username).first()

    # If user exists, return the existing user's ID
    if user:
        return user.id

    # If user does not exist, create a new one
    new_user = User(username=username)
    session.add(new_user)
    session.commit()

    return new_user.id
