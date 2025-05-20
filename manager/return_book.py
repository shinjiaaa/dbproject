# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from database import get_db
# from models import Book

# router = APIRouter()

# @router.post("/return_book/{book_id}")
# def return_book(book_id: int, db: Session = Depends(get_db)):
#     # 도서 존재 여부 + 삭제 여부 확인
#     book = db.query(Book).filter(
#         Book.book_id == book_id,
#         Book.is_deleted == False
#     ).first()

#     if not book:
#         raise HTTPException(status_code=404, detail="도서를 찾을 수 없습니다.")

#     # 이미 반납된 상태인지 확인
#     if book.rental_status:
#         raise HTTPException(status_code=400, detail="이미 반납된 도서입니다.")

#     # 반납 처리
#     book.rental_status = True
#     db.commit()

#     return {"message": "도서가 성공적으로 반납되었습니다."}
