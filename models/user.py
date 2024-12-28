from sqlalchemy import Column, Integer, String, DateTime
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String)
    last_name = Column(String)
    id_telegram = Column(String, unique=True)
    stage = Column(String, default='Start')
    updated_at = Column(DateTime, default=datetime.now())

    @staticmethod
    def check_user(session, id_telegram):
        return session.query(User).filter(User.id_telegram == id_telegram).first()
