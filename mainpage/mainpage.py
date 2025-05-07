# book/book.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Book
from database import get_db
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

class BookSearch(BaseModel):
    book_title: Optional[str] = None
    author: Optional[str] = None

# 도서 리스트
@router.get("/books_list", response_model=List[BookSearch])
def get_books(db: Session = Depends(get_db)):
    books = db.query(Book).all()
    return books

# 도서 검색
@router.get("/search_books", response_model=List[BookSearch])
def search_books(search: BookSearch, db: Session = Depends(get_db)):
    query = db.query(Book)
    if search.book_title:
        query = query.filter(Book.book_title.ilike(f"%{search.book_title}%"))
    if search.author:
        query = query.filter(Book.author.ilike(f"%{search.author}%"))
    return query.all()

# 도서 상세 정보 
@router.get("/book/{book_id}", response_model=BookSearch)
def get_book_detail(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# 도서 대여 기능
@router.post("/rantal_book/{book_id}")
def rantal_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="존재하지 않는 도서입니다.")
    
    if not book.rental_status:
        raise HTTPException(status_code=400, detail="이미 대여된 책입니다.")
    
    book.rental_status = False  # 대여 상태로 변경
    db.commit()
    return {"message": "대여 완료"}
