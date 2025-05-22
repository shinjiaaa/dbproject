import tkinter as tk
from tkinter import ttk, messagebox
import requests

def fetch_books():
    """서버에서 삭제되지 않은 책 목록 가져오기"""
    try:
        response = requests.get("http://localhost:8000/books_list")  # 수정된 API 경로
        if response.status_code == 200:
            return response.json()
        else:
            messagebox.showerror("오류", "도서 목록을 불러오는 데 실패했습니다.")
            return []
    except Exception as e:
        messagebox.showerror("서버 연결 오류", str(e))
        return []

def delete_book(book_id):
    """서버에 삭제 요청"""
    try:
        # DELETE 메서드와 RESTful 경로 권장
        response = requests.delete(f"http://localhost:8000/admin/book/{book_id}")
        if response.status_code == 200:
            messagebox.showinfo("성공", response.json()["message"])
            return True
        else:
            messagebox.showerror("실패", response.json().get("detail", "삭제 실패"))
            return False
    except Exception as e:
        messagebox.showerror("오류", str(e))
        return False

def show_delete_book_ui(root):
    window = tk.Toplevel(root)
    window.title("🗑 도서 삭제")
    window.geometry("700x400")

    tk.Label(window, text="📚 도서 목록 ").pack(pady=10)

    columns = ("도서 ID", "제목", "저자", "출판연도", "위치", "대출상태")

    tree = ttk.Treeview(window, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack()

    # 책 목록 불러오기
    books = fetch_books()
    for book in books:
        rental_value = book.get("rental_status", False)
        status = "대출 중" if rental_value else "대출 가능"

        tree.insert("", "end", values=(
            book.get("book_id", ""),
            book.get("book_title", ""),
            book.get("author", ""),
            book.get("year", ""),
            book.get("library_location", ""),
            status
        ))

    def delete_selected():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("경고", "삭제할 책을 선택해주세요.")
            return

        book_values = tree.item(selected_item)["values"]
        book_id = book_values[0]
        rental_status = book_values[5]

        if rental_status == "대출 중":
            messagebox.showerror("실패", "대출 중인 도서는 삭제할 수 없습니다.")
            return

        if delete_book(book_id):
            tree.delete(selected_item)

    delete_btn = tk.Button(window, text="선택한 책 삭제", command=delete_selected)
    delete_btn.pack(pady=10)

    window.mainloop()
