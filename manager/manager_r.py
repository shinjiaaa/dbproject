from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Service, User, Book
from database import get_db
from pydantic import BaseModel
from sqlalchemy import func
from datetime import date


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
@router.post("/return_book/{book_id}")
def return_book(book_id: int, db: Session = Depends(get_db)):
    # 도서 존재 여부 + 삭제 여부 확인
    book = db.query(Book).filter(
        Book.book_id == book_id,
        Book.is_deleted == False
    ).first()

    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")

    # 이미 반납된 상태인지 확인
    if book.rental_status:
        raise HTTPException(status_code=400, detail="이미 반납된 도서입니다.")

    # 반납 처리
    book.rental_status = True
    db.commit()

    return {"message": "도서가 성공적으로 반납되었습니다."}





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
# @router.post("/blacklist")
# async def add_blacklist(data: BlacklistData, db: Session = Depends(get_db)):
#    user = db.query(User).filter(User.user_id == data.user_id).first()
#    if not user:
#        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
#    user.blacklist = True
#    db.commit()
#    return {"message": "블랙리스트 추가 완료"}

# 블랙리스트 해지
@router.post("/blacklist/remove/{user_id}")
async def remove_blacklist(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    if not user.blacklist:
        raise HTTPException(status_code=400, detail="이미 블랙리스트에 등록되어 있지 않습니다.")
    user.blacklist = False
    db.commit()
    return {"message": "블랙리스트 해지 완료"}

# 블랙리스트 등록
@router.post("/blacklist/auto")
def auto_blacklist(db: Session = Depends(get_db)):
    late_users = db.query(Service.user_id)\
        .filter(Service.return_date > Service.due_date)\
        .group_by(Service.user_id)\
        .having(func.count() >= 2)\
        .all()

     # 각 사용자에 대해 블랙리스트 처리
    updated_users = []
    for user in late_users:
        user_id = user.user_id if hasattr(user, "user_id") else user[0]  # 튜플일 경우 대비
        u = db.query(User).filter(User.user_id == user_id).first()
        if u and not u.blacklist:
            u.blacklist = True
            updated_users.append(user_id)

    db.commit()
    return {"message": f"자동 블랙리스트 등록 완료: {len(updated_users)}명", "등록된 사용자": updated_users}