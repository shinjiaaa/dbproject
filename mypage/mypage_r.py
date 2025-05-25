from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from models import User, Book, Service
from database import get_db
from datetime import timedelta, datetime

router = APIRouter()

# 1. 대출 리스트 조회 API
@router.get("/rental_list")
def get_my_loans(
    user_id: int = Query(...),  # 사용자 ID를 쿼리 파라미터로 받음
    db: Session = Depends(get_db)  # DB 세션 주입 (의존성 주입 방식)
):
    # 해당 사용자의 대출 기록 (service 테이블) 조회
    services = db.query(Service).filter(Service.user_id == user_id).all()

    # 대출 기록이 없으면 404 에러 반환
    if not services:
        raise HTTPException(status_code=404, detail="대출 리스트가 존재하지 않습니다.")

    # 대출 기록에 포함된 책(book_id) 정보 가져오기
    book_ids = [service.book_id for service in services]
    books = db.query(Book).filter(Book.book_id.in_(book_ids)).all()

    # 대출 정보 + 도서 정보 합쳐서 응답 데이터 구성
    loan_details = []
    for service in services:
        for book in books:
            if book.book_id == service.book_id:
                loan_details.append({
                    "service_id": service.service_id,  # 대출 고유 ID
                    "book_title": book.book_title,    # 도서 제목
                    "due_date": service.due_date,     # 반납 예정일
                    "library_location": book.library_location,  # 도서관 위치
                    "returned_at": service.returned_at  # 실제 반납일 (없으면 아직 반납 안 한 상태)
                })
    return loan_details


# 2. 대출 연장 API
@router.post("/extend_rental/{service_id}")
def extend_loan(
    service_id: int,  # 연장할 대출 건의 ID (path parameter)
    extension_days: int = Query(...),  # 연장할 일수 (쿼리 파라미터)
    user_id: int = Query(...),         # 사용자 ID (쿼리 파라미터)
    db: Session = Depends(get_db)
):
    # 사용자와 대출 ID로 대출 기록 찾기
    service = db.query(Service).filter(Service.service_id == service_id, Service.user_id == user_id).first()

    # 대출 기록이 없으면 404 에러
    if not service:
        raise HTTPException(status_code=404, detail="대출 기록을 찾을 수 없습니다.")

    # 이미 반납된 책은 연장 불가
    if service.returned_at is not None:
        raise HTTPException(status_code=400, detail="이미 반납된 책은 연장할 수 없습니다.")

    # 대출 기간 연장: 기존 due_date에 연장 일수 더하기
    service.due_date += timedelta(days=extension_days)
    db.commit()

    # 성공 메시지 반환
    return {
        "message": f"대출이 {extension_days}일 연장되었습니다. 새로운 반납일: {service.due_date}"
    }
