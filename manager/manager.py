from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Service, User, Book
from database import get_db
from pydantic import BaseModel

from mypage.mypage import get_current_user

router = APIRouter()

class BookData(BaseModel):
    book_title: str
    author: str
    year: int
    rental_status: bool
    library_location: str

class BlacklistData(BaseModel):
    user_id: int
    blacklist_date: int

# 도서 추가
@router.post("/book")
async def add_book(data: BookData, db: Session = Depends(get_db)):
    new_book = Book(
        book_title=data.book_title,
        author=data.author,
        year=data.year,
        rental_status=data.rental_status,
        library_location=data.library_location
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return {"message": "도서 추가 완료"}

# 도서 삭제
@router.delete("/book/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")
    db.delete(book)
    db.commit()
    return {"message": "도서 삭제 완료"}

# 도서 반납
@router.post("/return_book/{service_id}")
def return_book(service_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id, Service.user_id == current_user.user_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    book = db.query(Book).filter(Book.book_id == service.book_id).first()
    book.rental_status = True
    db.commit()
    return {"message": "반납 완료"}

# 고객 정보 조회
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

# 블랙리스트 조회
@router.get("/blacklist")
async def get_blacklist(db: Session = Depends(get_db)):
    blacklist = db.query(User).filter(User.blacklist == True).all()
    return blacklist

# 블랙리스트 추가
@router.post("/blacklist")
async def add_blacklist(data: BlacklistData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    user.blacklist = True
    db.commit()
    return {"message": "블랙리스트 추가 완료"}
