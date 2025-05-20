from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Book, Service, User
from database import get_db
from datetime import timedelta, datetime
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Book 응답 모델 확장
class BookSearch(BaseModel):
    book_title: Optional[str] = None
    author: Optional[str] = None
    year: Optional[int] = None
    library_location: Optional[str] = None
    rental_status: Optional[bool] = None
    book_id: Optional[int] = None

# 전체 도서 목록
@router.get("/books_list", response_model=List[BookSearch])
def get_books(db: Session = Depends(get_db)):
    try:
        books = db.query(Book).all()
        return [{
            "book_title": book.book_title,
            "author": book.author,
            "year": book.year,
            "library_location": book.library_location,
            "rental_status": book.rental_status,
            "book_id": book.book_id
        } for book in books]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# 도서 검색
@router.get("/search_books", response_model=List[BookSearch])
def search_books(book_title: Optional[str] = None, author: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Book)
    if book_title:
        query = query.filter(Book.book_title.ilike(f"%{book_title}%"))
    if author:
        query = query.filter(Book.author.ilike(f"%{author}%"))
    books = query.all()
    return [{
        "book_title": book.book_title,
        "author": book.author,
        "year": book.year,
        "library_location": book.library_location,
        "rental_status": book.rental_status,
        "book_id": book.book_id
    } for book in books]

# 도서 상세 정보
@router.get("/book/{book_id}", response_model=BookSearch)
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return {
        "book_title": book.book_title,
        "author": book.author,
        "year": book.year,
        "library_location": book.library_location,
        "rental_status": book.rental_status,
        "book_id": book.book_id
    }

# 도서 대여 (오타 수정 optional)
@router.post("/rental_book/{book_id}")
def rental_book(book_id: int, db: Session = Depends(get_db)):
    
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="존재하지 않는 도서입니다.")
    if not book.rental_status:
        raise HTTPException(status_code=400, detail="이미 대여된 책입니다.")
    book.rental_status = False
    db.commit()
    return {"message": "대여 완료"}
