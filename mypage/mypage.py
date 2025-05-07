from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import Service, Book
from database import get_db
from datetime import timedelta

router = APIRouter()

# 대출 리스트
@router.get("/rental_list")
def get_my_loans(user_id: int, db: Session = Depends(get_db)):
    services = db.query(Service).filter(Service.user_id == user_id).all()
    if not services:
        raise HTTPException(status_code=404, detail="해당 사용자에 대한 대출 리스트가 존재하지 않습니다.")
    
    loan_details = []
    for service in services:
        book = db.query(Book).filter(Book.book_id == service.book_id).first()
        loan_details.append({
            "book_title": book.book_title,
            "due_date": service.due_date,
            "library_location": book.library_location,
            "rental_status": book.rental_status
        })
    
    return loan_details

# 대출 연장
@router.post("/extend_rantal/{service_id}")
def extend_loan(service_id: int, extension_days: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    # 연장 날짜 게산
    book = db.query(Book).filter(Book.book_id == service.book_id).first()
    new_end_date = service.due_date + timedelta(days=extension_days)
    service.due_date = new_end_date
    book.rental_status = "Extended"  # 대여 상태 갱신
    db.commit()

    return {"message": f"대출 연장 기간: {new_end_date}"}

# 책 반납
@router.post("/return_book/{service_id}")
def return_book(service_id: int, db: Session = Depends(get_db)):
    service = db.query(Service).filter(Service.service_id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    book = db.query(Book).filter(Book.book_id == service.book_id).first()
    book.rental_status = True  # 대여 가능 상태로 변경
    book.rental_status = "Returned"  # 대여 상태 갱신
    db.commit()

    return {"message": "반납 완료"}
