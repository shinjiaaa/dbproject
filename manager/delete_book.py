# dbproject/manager/delete_book.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

router = APIRouter()

class DeleteBookRequest(BaseModel):
    book_id: int

@router.post("/delete_book")
def delete_book(data: DeleteBookRequest):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()

    cursor.execute("SELECT rental_status FROM books WHERE book_id = ? AND is_deleted = 0", (data.book_id,))
    result = cursor.fetchone()

    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="해당 책을 찾을 수 없거나 이미 삭제되었습니다.")

    rental_status = result[0]
    if rental_status:
        raise HTTPException(status_code=400, detail="대출 중인 도서는 삭제할 수 없습니다.")

    cursor.execute("UPDATE books SET is_deleted = 1 WHERE book_id = ?", (data.book_id,))
    conn.commit()
    conn.close()
    return {"message": "도서가 성공적으로 삭제되었습니다."}
