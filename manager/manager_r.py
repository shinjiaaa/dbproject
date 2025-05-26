from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Service, User, Book
from database import get_db
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

# Pydantic 모델 정의
class BookData(BaseModel):
    book_title: str
    author: str
    year: int
    rental_status: bool = True
    library_location: str
    is_deleted: bool = False


class BlacklistData(BaseModel):
    user_id: int
    blacklist_date: int


# ✅ 도서 등록
@router.post("/book")
async def add_book(data: BookData, db: Session = Depends(get_db)):
    try:
        new_book = Book(
            book_title=data.book_title,
            author=data.author,
            year=data.year,
            library_location=data.library_location,
            rental_status=data.rental_status,
            is_deleted=data.is_deleted,
        )
        db.add(new_book)
        db.commit()
        return {"message": "도서 등록 완료"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ 도서 삭제
@router.delete("/book/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")
    db.delete(book)
    db.commit()
    return {"message": "도서 삭제 완료"}


# ✅ 도서 반납 (블랙리스트 자동 등록 포함)
@router.post("/return_book/{book_id}")
def return_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(
        Book.book_id == book_id,
        or_(Book.is_deleted == False, Book.is_deleted == None)
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")

    if book.rental_status:
        raise HTTPException(status_code=400, detail="이미 반납된 도서입니다.")

    service = db.query(Service).filter(
        Service.book_id == book_id, Service.returned_at == None
    ).order_by(Service.rented_at.desc()).first()

    if not service:
        raise HTTPException(status_code=404, detail="대출 기록을 찾을 수 없습니다.")

    # 반납 처리
    book.rental_status = True
    today = datetime.utcnow().date()
    service.returned_at = today

    # 연체 확인 및 블랙리스트 처리
    due_date = service.due_date
    if due_date is None:
        raise HTTPException(status_code=400, detail="반납 기한 정보가 없습니다.")

    if isinstance(due_date, datetime):
        due_date = due_date.date()

    user = db.query(User).filter(User.user_id == service.user_id).first()
    if user:
        if today > due_date:
            user.overdue_count += 1
            if user.overdue_count >= 3:
                user.blacklist = True
                user.blacklist_date = today  # 블랙리스트 등록일 기록

    db.commit()
    return {"message": "도서가 성공적으로 반납되었습니다."}


# ✅ 도서 목록 조회
@router.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).filter(Book.is_deleted == False).all()
    return books


# ✅ 사용자 목록 조회
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


# ✅ 블랙리스트 조회
@router.get("/blacklist")
async def get_blacklist(db: Session = Depends(get_db)):
    blacklist = db.query(User).filter(User.blacklist == True).all()
    return blacklist


# ✅ 블랙리스트 해지
@router.post("/blacklist/remove/{user_id}")
async def remove_blacklist(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user.blacklist:
        raise HTTPException(status_code=400, detail="이미 블랙리스트에 등록되어 있지 않습니다.")

    user.blacklist = False
    user.blacklist_date = None  # 해지 시 날짜 초기화
    db.commit()
    return {"message": "블랙리스트 해지 완료"}
