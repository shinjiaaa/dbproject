# delete_book.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

router = APIRouter()

# 삭제 요청용 모델
class DeleteBookRequest(BaseModel):
    book_id: int

# 도서 삭제 API
@router.post("/delete_book")
def delete_book(data: DeleteBookRequest):
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # 삭제되지 않은 책 정보 가져오기
    cursor.execute("""
        SELECT rental_status FROM BOOK
        WHERE book_id = ? AND is_deleted = 0
    """, (data.book_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 책을 찾을 수 없거나 이미 삭제되었습니다.")

    rental_status = result[0]  # True:대출 중 False:대출 가능

    # 대출 중이면 삭제 불가
    if rental_status == False:
        conn.close()
        raise HTTPException(status_code=400, detail="대출 중인 도서는 삭제할 수 없습니다.")

    # 삭제 처리
    cursor.execute("UPDATE BOOK SET is_deleted = 1 WHERE book_id = ?", (data.book_id,))
    conn.commit()
    conn.close()

    return {"message": f"book_id {data.book_id} 삭제 완료"}


# 삭제되지 않은 책 목록 반환 API
@router.get("/get_books")
def get_books():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT book_id, book_title, author, year, library_location
        FROM BOOK
        WHERE is_deleted = 0
    """)
    rows = cursor.fetchall()
    conn.close()

    books = [
        {
            "book_id": row[0],
            "book_title": row[1],
            "author": row[2],
            "year": row[3],
            "library_location": row[4]
        }
        for row in rows
    ]

    return {"books": books}
