import tkinter as tk
from tkinter import ttk, messagebox
import requests

root = tk.Tk()
root.title("도서 검색 및 대여")
root.geometry("600x400")

# 도서 목록 업데이트
def update_book_list(books):
    for row in treeview.get_children():
        treeview.delete(row)
    
    for book in books:
        treeview.insert("", "end", values=(book['book_title'], book['author'], book['year'], book['library_location'], book['rental_status']))

# 도서 전체 조회
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
    book_id = int(book_info[0])  # 책 ID가 첫 번째 컬럼에 있다고 가정

    try:
        res = requests.post(f"http://localhost:8000/rantal_book/{book_id}")
        if res.status_code == 200:
            messagebox.showinfo("대여 성공", res.json()["message"])
            fetch_all_books()
        else:
            messagebox.showerror("대여 실패", res.json()["detail"])
    except:
        messagebox.showerror("서버 오류", "대여 요청 실패")

# 마이페이지 버튼
def mypage():
    try:
        user_id = 1  # 예시로 user_id를 1로 설정
        response = requests.get(f"http://localhost:8000/mypage/{user_id}")
        if response.status_code == 200:
            user_info = response.json()
            # 마이페이지 정보 출력
            messagebox.showinfo("마이페이지", f"ID: {user_info['user_id']}\n이름: {user_info['name']}\n전화번호: {user_info['phone']}")
        else:
            messagebox.showerror("오류", "마이페이지 정보를 불러올 수 없습니다.")
    except:
        messagebox.showerror("서버 오류", "서버에 연결할 수 없습니다.")

# --- UI 구성 ---
tk.Label(root, text="도서 검색", font=("Arial", 14)).pack(pady=5)

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

tk.Button(root, text="도서 전체 보기", command=fetch_all_books).pack()
tk.Button(root, text="도서 대여", command=rent_book).pack(pady=5)

tk.Button(root, text="마이페이지", command=mypage).place(x=500, y=10)  # 마이페이지 버튼은 여전히 오른쪽 상단에 배치

# 실행 시 전체 도서 불러오기
fetch_all_books()

root.mainloop()
