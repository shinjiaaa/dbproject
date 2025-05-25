from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 데이터베이스 연결결
SQLALCHEMY_DATABASE_URL = "sqlite:///./mydatabase.db"

# SQLALCHEMY 엔진 생성
engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# 세션 로컬 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 모델 정의
Base = declarative_base()


# 데이터베이스 세션
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
