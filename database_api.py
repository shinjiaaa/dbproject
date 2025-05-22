from fastapi import APIRouter
import sqlite3
from fastapi import APIRouter
from database import SessionLocal
from models import Book

router = APIRouter()

@router.post("/admin/set_available/{book_id}")
def set_book_available(book_id: int):
    db = SessionLocal()
    book = db.query(Book).filter(Book.book_id == book_id).first()
    if not book:
        db.close()
        return {"error": "Book not found"}

    book.rental_status = 0  # 대출 가능 상태로 변경
    db.commit()
    db.close()
    return {"message": f"Book ID {book_id} is now available."}


@router.get("/get_books")
def get_books():
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("""
    SELECT book_id, book_title, author, year, library_location, rental_status
    FROM books
    WHERE is_deleted = 0
""")

    rows = cursor.fetchall()
    conn.close()

    books = []
    for row in rows:
        books.append({
            "book_id": row[0],
            "title": row[1],
            "author": row[2],
            "year": row[3],
            "location": row[4],
            "rental_status": row[5]
        })

    return {"books": books}
