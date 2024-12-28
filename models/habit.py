from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database import Base

class Habit(Base):
    __tablename__ = 'habits'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_telegram_user = Column(Integer, ForeignKey('users.id_telegram'))
    name = Column(String)
    description = Column(String)
    total_streak = Column(Integer, default=0)
    last_streak = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now())

    @staticmethod
    def create_habit(session, id_telegram_user, name):
        habit = Habit(id_telegram_user=id_telegram_user, name=name)
        session.add(habit)
        session.commit()
        return habit

    @staticmethod
    def get_habit(session, id_telegram_user, habit_id=None, offset=0):
        try:
            query = session.query(Habit).filter(
                Habit.id_telegram_user == id_telegram_user)
            if habit_id:
                query = query.filter(Habit.id == habit_id)
            else:
                query = query.limit(5).offset(offset)
            return query.all()
        except Exception as e:
            print(e)
            return None
        
    @staticmethod
    def delete_habit(session, id_telegram_user, habit_id):
        habit = session.query(Habit).filter(Habit.id_telegram_user == id_telegram_user, Habit.id == habit_id).first()
        if habit:
            session.delete(habit)
            session.commit()
            return True
        return False
    
    @staticmethod
    def update_habit(session, id_telegram_user, habit_id, name, description):
        habit = session.query(Habit).filter(Habit.id_telegram_user == id_telegram_user, Habit.id == habit_id).first()
        if habit:
            habit.name = name
            habit.description = description
            session.commit()
            return True
        return False
    
    @staticmethod
    def count_habit(session, id_telegram_user):
        return session.query(Habit).filter(Habit.id_telegram_user == id_telegram_user).count()