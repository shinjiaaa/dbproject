import tkinter as tk
from tkinter import ttk, messagebox
import requests
from mypage.mypage_ui import mypage_ui  # 마이페이지 import

def mainpage_ui(root, user_id):
    from login.login_ui import clear_widgets
    clear_widgets(root)

    root.title("도서 검색 및 대여")
    root.geometry("1000x500")

    # ===== 내부 함수 정의 =====
    def update_book_list(books):
        treeview.delete(*treeview.get_children())
        for book in books:
            book_id = book.get("book_id", 0)
            book_title = book.get("book_title", "")
            author = book.get("author", "")
            year = book.get("year", "")
            location = book.get("library_location", "")

            # ✅ rental_status: True면 대여 가능, False면 대여 중
            rental_status = "대여 가능" if book.get("rental_status", True) else "대여 중"

            # book_id는 사용자에겐 안 보이지만 tags로 저장
            treeview.insert("", "end", values=(book_title, author, year, location, rental_status), tags=(str(book_id),))

    def fetch_all_books():
        try:
            res = requests.get("http://localhost:8000/books_list")
            if res.status_code == 200:
                update_book_list(res.json())
            else:
                messagebox.showerror("오류", "도서 목록을 불러오지 못했습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"서버에 연결할 수 없습니다.\n{str(e)}")

    def search_books():
        title = title_entry.get()
        author = author_entry.get()
        params = {"book_title": title, "author": author}
        try:
            res = requests.get("http://localhost:8000/search_books", params=params)
            if res.status_code == 200:
                update_book_list(res.json())
            else:
                messagebox.showerror("오류", "검색 실패")
        except Exception as e:
            messagebox.showerror("서버 오류", f"서버에 연결할 수 없습니다.\n{str(e)}")

    def rent_book():
        selected = treeview.selection()
        if not selected:
            messagebox.showwarning("선택 오류", "대여할 책을 선택하세요.")
            return

        book_id = int(treeview.item(selected[0])["tags"][0])  # 숨겨진 book_id 추출

        try:
            res = requests.post(f"http://localhost:8000/rental_book/{book_id}", json={"user_id": user_id})
            if res.status_code == 200:
                fetch_all_books()
                messagebox.showinfo("대여 성공", res.json()["message"])
            else:
                messagebox.showerror("대여 실패", res.json()["detail"])
        except Exception as e:
            messagebox.showerror("서버 오류", f"대여 요청 실패\n{str(e)}")

    # ===== UI 구성 =====
    tk.Label(root, text="도서 검색", font=("Arial", 14)).pack(pady=5)

    tk.Label(root, text="제목").pack()
    title_entry = tk.Entry(root)
    title_entry.pack()

    tk.Label(root, text="작가").pack()
    author_entry = tk.Entry(root)
    author_entry.pack()

    tk.Button(root, text="검색", command=search_books).pack(pady=5)

    columns = ("책 제목", "저자", "출판년도", "도서관 위치", "대출 상태")
    treeview = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for col in columns:
        treeview.heading(col, text=col)
    treeview.pack(pady=10)

    tk.Button(root, text="도서 대여", command=rent_book).pack(pady=5)
    tk.Button(root, text="마이페이지", command=lambda: mypage_ui(root, user_id)).place(relx=1.0, x=-20, y=10, anchor="ne")

    # ===== 초기 실행 =====
    fetch_all_books()
