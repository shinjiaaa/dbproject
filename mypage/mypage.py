from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Book, Service, User
from database import get_db
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "6db98f1da03cce9a40f27ea20199b542e6ad88d56807830f47bf5497f8405c77eec2e3b2fde0e1dfb44160dc02281f47afaae916aab2206a633f6418a3a24087"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# JWT 생성
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 사용자 인증
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: user_id not found")
        
        user = db.query(User).filter(User.user_id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# 대출 리스트 조회
@router.get("/rental_list")
def get_my_loans(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.user_id == current_user.user_id).all()
    if not services:
        raise HTTPException(status_code=404, detail="대출 리스트가 존재하지 않습니다.")
    
    book_ids = [service.book_id for service in services]
    books = db.query(Book).filter(Book.book_id.in_(book_ids)).all()

    loan_details = [{
        "book_title": book.book_title,
        "due_date": service.due_date,
        "library_location": book.library_location,
        "rental_status": True if book.rental_status == "True" else False  # 문자열로 되어 있을 경우 처리
    } for service in services for book in books if book.book_id == service.book_id]

    return loan_details


# 대출 연장
@router.post("/extend_rental/{service_id}")
def extend_loan(service_id: int, extension_days: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id, Service.user_id == current_user.user_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    service.due_date += timedelta(days=extension_days)
    db.commit()
    return {"message": f"대출 연장 기간: {service.due_date}"}


