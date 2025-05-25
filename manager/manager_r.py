from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Service, User, Book
from database import get_db
from pydantic import BaseModel
from sqlalchemy import func
from datetime import date


router = APIRouter()


# Pydantic 모델 정의
class BookData(BaseModel):
    book_title: str
    author: str
    year: int
    rental_status: bool = True
    library_location: str
    is_deleted: bool = False


# 블랙리스트 데이터 모델 정의
class BlacklistData(BaseModel):
    user_id: int
    blacklist_date: int


# 도서 추가
@router.post("/book")
async def add_book(data: BookData, db: Session = Depends(get_db)):
    # 도서 제목 중복 확인
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
    # 예외 처리
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# 도서 삭제
@router.delete("/book/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.book_id == book_id).first()  # book_id로 조회
    if not book:
        raise HTTPException(
            status_code=404, detail="도서를 찾을 수 없습니다."
        )  # 도서 존재 여부 확인
    db.delete(book)
    db.commit()
    return {"message": "도서 삭제 완료"}


# 도서 대출
@router.post("/return_book/{book_id}")
def return_book(book_id: int, db: Session = Depends(get_db)):
    from sqlalchemy import or_
    from datetime import datetime

    # 도서 확인
    book = (
        db.query(Book)  # 삭제되지 않은 도서만 조회 (필터링)
        .filter(
            Book.book_id == book_id,
            or_(Book.is_deleted == False, Book.is_deleted == None),
        )
        .first()
    )
    if not book:
        raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")

    if book.rental_status:
        raise HTTPException(status_code=400, detail="이미 반납된 도서입니다.")

    # 대출 기록 조회
    service = (
        db.query(Service)
        .filter(Service.book_id == book_id, Service.returned_at == None)
        .order_by(Service.rented_at.desc())
        .first()
    )  # 가장 최근 대출 기록 조회
    if not service:
        raise HTTPException(
            status_code=404, detail="대출 기록을 찾을 수 없습니다."
        )  # 대출 기록이 없으면 404

    # 반납 처리
    book.rental_status = True
    today = datetime.utcnow().date()  # ✅ 날짜만 저장
    service.returned_at = today

    # 연체 확인 및 처리
    if today > service.due_date.date():  # due_date가 datetime이면 .date()로 비교
        user = (
            db.query(User).filter(User.user_id == service.user_id).first()
        )  # 사용자 조회
        if user:
            user.overdue_count += 1  # 연체 횟수 증가

    db.commit()
    return {"message": "도서가 성공적으로 반납되었습니다."}


# 도서 목록 전체 조회
@router.get("/books")
def get_books(db: Session = Depends(get_db)):
    books = (
        db.query(Book).filter(Book.is_deleted == False).all()
    )  # 삭제되지 않은 도서만 조회
    return books


# 고객 정보 조회
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()  # 모든 사용자 조회
    return users


# 블랙리스트 조회
@router.get("/blacklist")
async def get_blacklist(db: Session = Depends(get_db)):
    blacklist = (
        db.query(User).filter(User.blacklist == True).all()
    )  # 블랙리스트 사용자 조회
    return blacklist


# 블랙리스트 해지
@router.post("/blacklist/remove/{user_id}")
async def remove_blacklist(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()  # user_id로 조회
    if not user:
        raise HTTPException(
            status_code=404, detail="사용자를 찾을 수 없습니다."
        )  # 사용자 존재 여부 확인
    if not user.blacklist:
        raise HTTPException(
            status_code=400, detail="이미 블랙리스트에 등록되어 있지 않습니다."
        )  # 블랙리스트 여부 확인
    user.blacklist = False  # 블랙리스트 해지
    db.commit()
    return {"message": "블랙리스트 해지 완료"}


# 자동 블랙리스트 등록
@router.post("/blacklist/auto")
def auto_blacklist(db: Session = Depends(get_db)):
    # 1. 연체 기록이 2회 이상인 사용자들 조회
    late_users = (
        db.query(Service.user_id, func.count().label("overdue_count"))
        .filter(Service.returned_at > Service.due_date)  # 연체 반납
        .group_by(Service.user_id)
        .having(func.count() >= 2)
        .all()
    )

    updated_users = []

    # 2. 각 사용자에 대해 블랙리스트 처리 및 overdue_count 갱신
    for user in late_users:
        user_id = user.user_id if hasattr(user, "user_id") else user[0]  # user_id 추출
        overdue_count = (
            user.overdue_count
            if hasattr(user, "overdue_count")
            else user[1]  # 연체 횟수 추출
        )

        u = db.query(User).filter(User.user_id == user_id).first()  #  user_id로 조회

        # 사용자 존재 여부 확인
        if u:
            u.overdue_count = overdue_count  # 연체 횟수 반영
            if not u.blacklist:
                u.blacklist = True
            updated_users.append(user_id)

    db.commit()
    # 3. 블랙리스트에 등록된 사용자 목록 반환
    return {
        "message": f"{len(updated_users)}명의 사용자가 블랙리스트에 등록되었습니다.",
        "user_ids": updated_users,
    }
