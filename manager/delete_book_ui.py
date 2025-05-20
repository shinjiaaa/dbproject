import tkinter as tk
from tkinter import ttk, messagebox
import requests

def fetch_books():
    """서버에서 삭제되지 않은 책 목록 가져오기"""
    try:
        response = requests.get("http://localhost:8000/get_books")
        if response.status_code == 200:
            return response.json()["books"]
        else:
            messagebox.showerror("오류", "도서 목록을 불러오는 데 실패했습니다.")
            return []
    except Exception as e:
        messagebox.showerror("서버 연결 오류", str(e))
        return []

def delete_book(book_id):
    """서버에 삭제 요청"""
    response = requests.post("http://localhost:8000/delete_book", json={"book_id": book_id})
    if response.status_code == 200:
        messagebox.showinfo("성공", response.json()["message"])
    else:
        messagebox.showerror("실패", response.json()["detail"])

def show_delete_book_ui(root):
    window = tk.Toplevel(root)
    window.title("🗑 도서 삭제")
    window.geometry("700x400")

    tk.Label(window, text="📚 도서 목록 ").pack(pady=10)

    columns = ("도서 ID", "제목", "저자", "출판연도", "위치", "대출상태")  # ← 여기 추가

    tree = ttk.Treeview(window, columns=columns, show="headings", height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack()

    # 책 목록 불러오기
    books = fetch_books()
    for book in books:
        status = "대출 중" if book["rental_status"] else "대출 가능"
        tree.insert("", "end", values=(
            book["book_id"],
            book["title"],
            book["author"],
            book["year"],
            book["location"],
            book["rental_status"] 
        ))
    def delete_selected():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("경고", "삭제할 책을 선택해주세요.")
            return
        book_id = tree.item(selected_item)["values"][0]
        delete_book(book_id)
        tree.delete(selected_item)  # UI에서도 삭제

    delete_btn = tk.Button(window, text="선택한 책 삭제", command=delete_selected)
    delete_btn.pack(pady=10)

    window.mainloop()
