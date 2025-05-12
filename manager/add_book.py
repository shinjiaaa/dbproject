from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Book
from pydantic import BaseModel

router = APIRouter()

class BookCreate(BaseModel):
    book_id: int
    book_title: str
    author: str
    year: int
    library_location: str

@router.post("/add_book")
def add_book(data: BookCreate, db: Session = Depends(get_db)):
    try:
        new_book = Book(
            book_id=data.book_id,
            book_title=data.book_title,
            author=data.author,
            year=data.year,
            library_location=data.library_location,
            rental_status=True,
            is_deleted=False
        )
        db.add(new_book)
        db.commit()
        return {"message": "도서 등록 완료"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
