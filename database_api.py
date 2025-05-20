from fastapi import APIRouter
import sqlite3

router = APIRouter()

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
