from sqlalchemy import Column, String
from app import Base

class User(Base):
    __tablename__ = "users"
    
    username = Column(String, primary_key=True, index=True)
    password = Column(String)
