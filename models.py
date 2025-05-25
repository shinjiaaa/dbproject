from sqlalchemy import Column, String, Integer, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import DateTime
from datetime import datetime
from datetime import timezone


# user 모델
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)  # 사용자 ID

    name = Column(String)  # 사용자 이름
    login_id = Column(String, unique=True, index=True)  # 로그인 ID (고유)
    password = Column(String)  # 비밀번호 (해싱된 값)
    phone = Column(String, nullable=True)  # 전화번호
    admin = Column(Boolean, default=False)  # 관리자 여부
    overdue_count = Column(Integer, default=0)  # 연체 횟수
    blacklist = Column(Boolean, default=False)  # 블랙리스트 여부
    blacklist_date = Column(Date, nullable=True)  # 블랙리스트 등록 날짜

    # 관계 (User -> Service -> Book)
    services = relationship("Service", back_populates="user")


# book 모델
class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)  # 도서 ID

    book_title = Column(String, index=True)  # 도서 제목
    author = Column(String)  # 저자
    year = Column(Integer)  # 출판 연도
    rental_status = Column(Boolean)  # 대여 가능 여부
    library_location = Column(String)  # 도서관 위치
    is_deleted = Column(Boolean, default=False)  # 삭제 여부

    # 관계 (Book -> Service -> User)
    services = relationship("Service", back_populates="book")


# service 모델 (관계 모델)
class Service(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, index=True)  # 서비스 ID

    book_id = Column(Integer, ForeignKey("books.book_id"))  # 도서 ID
    user_id = Column(Integer, ForeignKey("users.user_id"))  # 사용자 ID

    rented_at = Column(DateTime, default=datetime.now(timezone.utc))  # 대여 날짜
    due_date = Column(Date)  # 반납 예정일
    returned_at = Column(Date, nullable=True)  # 반납 날짜 (반납하지 않은 경우 None)
    extension_count = Column(Integer, default=0)  # 대출 연장 횟수

    # 관계 (Service -> User, Book)
    book = relationship("Book", back_populates="services")
    user = relationship("User", back_populates="services")
