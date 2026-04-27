# db_models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base
from datetime import date
from typing import Optional, List

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    applications: Mapped[List['Application']] = relationship('Application', back_populates='user') # SQLAlchemy relationship to link User to their Applications 
    
class Application(Base):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, nullable=False) # primary key (auto increment & must be unique) indexed for faster queries
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    position: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default = 'Applied')
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    salary: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    date_applied: Mapped[date] = mapped_column(Date, default = date.today, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False) # foreign key to link application to a user (must exist in users table)
    user: Mapped['User'] = relationship('User', back_populates='applications') # SQLAlchemy relationship to link Application back to its User (bidirectional relationship)

    def __repr__(self):
        return f"<Application(id={self.id}, company='{self.company}', position='{self.position}', status='{self.status}', notes='{self.notes}', salary={self.salary}, date_applied={self.date_applied})>"
    
