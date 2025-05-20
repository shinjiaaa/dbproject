from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models import Book, Service
from database import get_db
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta, timezone

router = APIRouter()

# --- Pydantic Models ---
class BookSearch(BaseModel):
    book_id: int
    book_title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    library_location: Optional[str] = None
    rental_status: Optional[bool] = None  # True = 대여 가능, False = 대출 중

    class Config:
        orm_mode = True

class RentalRequest(BaseModel):
    user_id: int

# --- 도서 리스트 조회 ---
@router.get("/books_list", response_model=List[BookSearch])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).filter(or_(Book.is_deleted == False, Book.is_deleted == None)).all()
    return [
        {
            "book_id": book.book_id,
            "book_title": book.book_title,
            "author": book.author,
            "year": book.year,
            "library_location": book.library_location,
            "rental_status": book.rental_status
        }
        for book in books
    ]

# --- 도서 검색 ---
@router.get("/search_books", response_model=List[BookSearch])
def search_books(
    book_title: Optional[str] = None,
    author: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Book).filter(or_(Book.is_deleted == False, Book.is_deleted == None))
    if book_title:
        query = query.filter(Book.book_title.ilike(f"%{book_title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    books = query.all()

    return [
        {
            "book_id": book.book_id,
            "book_title": book.book_title,
            "author": book.author,
            "year": book.year,
            "library_location": book.library_location,
            "rental_status": book.rental_status
        }
        for book in books
    ]

# --- 도서 상세 정보 ---
@router.get("/book/{book_id}", response_model=BookSearch)
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(
        Book.book_id == book_id,
        or_(Book.is_deleted == False, Book.is_deleted == None)
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return {
        "book_id": book.book_id,
        "book_title": book.book_title,
        "author": book.author,
        "year": book.year,
        "library_location": book.library_location,
        "rental_status": book.rental_status
    }

# --- 도서 대여 ---
@router.post("/rental_book/{book_id}")
def rental_book(book_id: int, req: RentalRequest, db: Session = Depends(get_db)):
    book = db.query(Book).filter(
        Book.book_id == book_id,
        or_(Book.is_deleted == False, Book.is_deleted == None)
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="존재하지 않는 도서입니다.")

    if book.rental_status is False:  # ✅ False만 막고 None은 허용
        raise HTTPException(status_code=400, detail="이미 대여된 책입니다.")

    book.rental_status = False  # 대출 중으로 상태 변경

    now = datetime.now(timezone.utc)  # SQLite 호환 (naive datetime)
    new_service = Service(
        user_id=req.user_id,
        book_id=book_id,
        rented_at=now,
        due_date=now + timedelta(days=14),
        extension_count=0
    )
    db.add(new_service)
    db.add(book)  # 대출 상태 변경된 book 객체도 추가
    db.commit()

    return {"message": "대여 완료"}
