import tkinter as tk
from tkinter import ttk, messagebox
import requests


def show_return_book_ui(root):
    window = tk.Toplevel(root)
    window.title("도서 반납")
    window.geometry("800x500")

    tk.Label(window, text="📚 도서 반납", font=("Arial", 16)).pack(pady=10)

    # 검색창
    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="도서 검색").pack(side="left", padx=5)
    search_entry = tk.Entry(search_frame, width=40)
    search_entry.pack(side="left", padx=5)

    # book_id 컬럼도 포함된 Treeview 컬럼 정의
    columns = ("ID", "책 제목", "저자", "출판년도", "도서관 위치", "대출 상태")
    tree = ttk.Treeview(window, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    tree.pack(pady=10)

    # 책 불러오기 함수
    def fetch_books(keyword=None):
        try:
            res = requests.get("http://localhost:8000/books_list")
            if res.status_code == 200:
                books = res.json()
                tree.delete(*tree.get_children())

                for book in books:
                    if book["rental_status"] is False:  # 대출 중인 책만
                        if keyword and keyword.lower() not in book["book_title"].lower():
                            continue
                        tree.insert(
                            "",
                            "end",
                            iid=book["book_id"],
                            values=(
                                book["book_id"],  # 첫 번째 칼럼으로 book_id 보여줌
                                book["book_title"],
                                book["author"],
                                book.get("year", ""),
                                book.get("library_location", ""),
                                "대출 중"
                            )
                        )
        except Exception as e:
            messagebox.showerror("서버 오류", str(e))

    def search_books():
        keyword = search_entry.get().strip()
        fetch_books(keyword)

    tk.Button(search_frame, text="검색", command=search_books).pack(side="left", padx=5)

    def return_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("선택 없음", "반납할 책을 선택하세요.")
            return

        book_id = int(selected[0])  # Treeview의 iid로 book_id 저장했으므로 그대로 사용
        try:
            res = requests.post(f"http://localhost:8000/return_book/{book_id}")
            if res.status_code == 200:
                messagebox.showinfo("성공", res.json()["message"])
                fetch_books()
            else:
                messagebox.showerror("실패", res.json().get("detail", "반납 실패"))
        except Exception as e:
            messagebox.showerror("서버 오류", str(e))

    tk.Button(window, text="반납", width=10, command=return_selected).pack()

    fetch_books()
