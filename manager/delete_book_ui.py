import tkinter as tk
from tkinter import ttk, messagebox
import requests

def fetch_books(query=None):
    """서버에서 삭제되지 않은 책 목록 가져오기 (검색어가 있으면 필터링)"""
    try:
        url = "http://localhost:8000/books_list"
        params = {}
        if query:
            params["query"] = query  # 서버 API에 따라 쿼리 파라미터 이름은 조정 필요
        response = requests.get(url, params=params)
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
        url = f"http://localhost:8000/admin/book/{book_id}"  # URL에 book_id 넣기
        response = requests.delete(url)  # DELETE 메서드로 요청
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
    window.geometry("700x450")

    tk.Label(window, text="📚 도서 검색").pack(pady=5)

    # 검색창 & 버튼 프레임
    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=40)
    search_entry.pack(side=tk.LEFT, padx=(0, 5))

    columns = ("도서 ID", "제목", "저자", "출판연도", "위치", "대출상태")

    tree = ttk.Treeview(window, columns=columns, show="headings", height=15)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)
    tree.pack(pady=10)

    def load_books(query=None):
        # 기존 목록 클리어
        for row in tree.get_children():
            tree.delete(row)
        # 책 목록 불러오기
        books = fetch_books(query)
        for book in books:
            rental_value = book.get("rental_status", False)
            status = "대출 가능" if rental_value else "대출 중"
            tree.insert("", "end", values=(
                book.get("book_id", ""),
                book.get("book_title", ""),
                book.get("author", ""),
                book.get("year", ""),
                book.get("library_location", ""),
                status
            ))

    def on_search():
        query = search_var.get().strip()
        load_books(query if query else None)

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

    search_btn = tk.Button(search_frame, text="검색", command=on_search)
    search_btn.pack(side=tk.LEFT)

    delete_btn = tk.Button(window, text="선택한 책 삭제", command=delete_selected)
    delete_btn.pack(pady=5)

    # 처음에 전체 도서 목록 로드
    load_books()

    window.mainloop()
