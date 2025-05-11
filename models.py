from sqlalchemy import Column, String, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    login_id = Column(String, unique=True, index=True)
    password = Column(String)
    phone = Column(String, nullable=True)
    admin = Column(Boolean, default=False)
    overdue_count = Column(Integer, default=0)
    blacklist = Column(Boolean, default=False)
    blacklist_date = Column(Date, nullable=True)

    # 관계 (User -> Service -> Book)
    services = relationship("Service", back_populates="user")

class Book(Base):
    __tablename__ = "books"
    
    book_id = Column(Integer, primary_key=True, index=True)

    book_title = Column(String, index=True)
    author = Column(String)
    year = Column(Integer)
    rental_status = Column(Boolean)
    library_location = Column(String)

    # 관계 (Book -> Service -> User)
    services = relationship("Service", back_populates="book")

class Service(Base):
    __tablename__ = 'services'
    
    service_id = Column(Integer, primary_key=True, index=True)

    book_id = Column(Integer, ForeignKey('books.book_id')) 
    user_id = Column(Integer, ForeignKey('users.user_id')) 

    due_date = Column(Date)
    returned_at = Column(Date, nullable=True)
    extension_count = Column(Integer, default=0)

    # 관계 (Service -> User, Book)
    book = relationship("Book", back_populates="services")
    user = relationship("User", back_populates="services")
