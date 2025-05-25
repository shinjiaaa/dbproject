from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models import User, Book, Service
from database import get_db
from datetime import timedelta, datetime

router = APIRouter()


# 1. 대출 리스트 조회
@router.get("/rental_list")
def get_my_loans(
    user_id: int = Query(...), db: Session = Depends(get_db)  # 쿼리 파라미터 명시
):
    services = (
        db.query(Service).filter(Service.user_id == user_id).all()
    )  # 사용자 ID로 대출 기록 조회

    if not services:
        raise HTTPException(
            status_code=404, detail="대출 리스트가 존재하지 않습니다."
        )  # 대출 기록이 없을 경우 예외 처리

    # 대출된 책들 가져오기
    book_ids = [service.book_id for service in services]
    books = db.query(Book).filter(Book.book_id.in_(book_ids)).all()

    # 응답 데이터 구성
    loan_details = []
    for service in services:
        for book in books:
            if book.book_id == service.book_id:
                loan_details.append(
                    {
                        "service_id": service.service_id,
                        "book_title": book.book_title,
                        "due_date": service.due_date,
                        "library_location": book.library_location,
                        "returned_at": service.returned_at,
                    }
                )
    return loan_details


# 2. 대출 연장
@router.post("/extend_rental/{service_id}")
def extend_loan(  # 쿼리 파라미터로 받는 부분
    service_id: int,
    extension_days: int = Query(...),
    user_id: int = Query(...),
    db: Session = Depends(get_db),
):
    service = (  # 서비스 ID와 사용자 ID로 대출 기록 조회
        db.query(Service)
        .filter(Service.service_id == service_id, Service.user_id == user_id)
        .first()
    )

    if not service:
        raise HTTPException(
            status_code=404, detail="대출 기록을 찾을 수 없습니다."
        )  # 대출 기록이 없으면 404

    # 이미 반납된 책은 연장 불가
    if service.returned_at is not None:
        raise HTTPException(
            status_code=400, detail="이미 반납된 책은 연장할 수 없습니다."
        )

    # 대출 연장
    service.due_date += timedelta(days=extension_days)  # 연장 일수만큼 반납일 연장
    db.commit()

    return {
        "message": f"대출이 {extension_days}일 연장되었습니다. 새로운 반납일: {service.due_date}"
    }
