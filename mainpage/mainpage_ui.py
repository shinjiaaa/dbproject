#로그인에 필요
import sys
user_id = int(sys.argv[1]) if len(sys.argv) > 1 else None

#마이페이지에 필요
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import ttk, messagebox
import requests


root = tk.Tk()
root.title("도서 검색 및 대여")
root.geometry("600x400")

# 로그인 후 user_id 설정 (예시로 user_id 값을 설정해 줍니다)
user_id = 1  # 로그인 후 이 값을 동적으로 설정

# 도서 목록 업데이트
def update_book_list(books):
    for row in treeview.get_children():  # 기존에 있는 데이터 삭제
        treeview.delete(row)

    for book in books:
        book_title = book.get("book_title", "")
        author = book.get("author", "")
        year = book.get("year", "")
        location = book.get("library_location", "")
        rental_status = "대여 가능" if book.get("rental_status", False) else "대여 중"
        book_id = book.get("book_id", 0)

        treeview.insert("", "end", values=(
            book_title, author, year, location, rental_status, book_id
        ))


# 도서 전체
def fetch_all_books():
    try:
        res = requests.get("http://localhost:8000/books_list")
        
        if res.status_code == 200:
            update_book_list(res.json())
        else:
            messagebox.showerror("오류", "도서 목록을 불러오지 못했습니다.")
    except:
        messagebox.showerror("오류", "서버에 연결할 수 없습니다.")

# 도서 검색
def search_books():
    title = title_entry.get()
    author = author_entry.get()
    print(f"Title: {title}, Author: {author}")  # Debug: 확인을 위해 출력
    params = {"book_title": title, "author": author}
    try:
        res = requests.get("http://localhost:8000/search_books", params=params)
        if res.status_code == 200:
            update_book_list(res.json())
        else:
            messagebox.showerror("오류", "검색 실패")
    except:
        messagebox.showerror("서버 오류", "서버에 연결할 수 없습니다.")


        

# 도서 대여
def rent_book():
    selected = treeview.selection()
    if not selected:
        messagebox.showwarning("선택 오류", "대여할 책을 선택하세요.")
        return

    book_info = treeview.item(selected[0])['values']
    book_id = int(book_info[5])  # 책 ID가 마지막 컬럼에 있다고 가정

    try:
        res = requests.post(f"http://localhost:8000/rental_book/{book_id}")
        if res.status_code == 200:
            fetch_all_books()  # ✅ 먼저 새로고침
            messagebox.showinfo("대여 성공", res.json()["message"])
        else:
            messagebox.showerror("대여 실패", res.json()["detail"])
    except:
        messagebox.showerror("서버 오류", "대여 요청 실패")




# 마이페이지 버튼
def mypage():
    global user_id
    if user_id is None:  # 로그인되지 않으면
        messagebox.showerror("오류", "로그인 후 마이페이지를 이용해주세요.")
        return
    # 마이페이지 UI 열기
    mypage_window = tk.Toplevel()  # Create a new top-level window
    from mypage import mypage_ui  # This assumes 'mypage_ui.py' is inside the 'mypage' folder
    mypage_ui.mypage_ui(mypage_window, user_id)  # Pass user_id to the mypage_ui function


# --- UI 구성 ---
tk.Label(root, text="도서 검색", font=("Arial", 14)).pack(pady=5)
root.geometry("1000x500") 

tk.Label(root, text="제목").pack()
title_entry = tk.Entry(root)
title_entry.pack()

tk.Label(root, text="작가").pack()
author_entry = tk.Entry(root)
author_entry.pack()

tk.Button(root, text="검색", command=search_books).pack(pady=5)

# 테이블 레이아웃
columns = ("책 제목", "저자", "출판년도", "도서관 위치", "대출 상태")
treeview = ttk.Treeview(root, columns=columns, show="headings", height=10)
for col in columns:
    treeview.heading(col, text=col)
treeview.pack(pady=10)

tk.Button(root, text="도서 대여", command=rent_book).pack(pady=5)
tk.Button(root, text="마이페이지", command=mypage).place(x=900, y=10)  # 마이페이지 버튼은 여전히 오른쪽 상단에 배치

# 실행 시 전체 도서 불러오기
fetch_all_books()

root.mainloop()
