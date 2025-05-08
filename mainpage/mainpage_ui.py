import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

root = tk.Tk()
root.title("도서 검색 및 대여")
root.geometry("500x400")

book_listbox = None

# 도서 목록 업데이트
def update_book_list(books):
    book_listbox.delete(0, tk.END)
    for book in books:
        book_listbox.insert(tk.END, f"{book['book_title']} / {book['author']} (ID: {book['book_id']})")

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
    selected = book_listbox.curselection()
    if not selected:
        messagebox.showwarning("선택 오류", "대여할 책을 선택하세요.")
        return

    book_info = book_listbox.get(selected[0])
    book_id = int(book_info.split("ID: ")[1].replace(")", ""))

    try:
        res = requests.post(f"http://localhost:8000/rantal_book/{book_id}")
        if res.status_code == 200:
            messagebox.showinfo("대여 성공", res.json()["message"])
            fetch_all_books()
        else:
            messagebox.showerror("대여 실패", res.json()["detail"])
    except:
        messagebox.showerror("서버 오류", "대여 요청 실패")

# --- UI 구성 ---
tk.Label(root, text="도서 검색", font=("Arial", 14)).pack(pady=5)

tk.Label(root, text="제목").pack()
title_entry = tk.Entry(root)
title_entry.pack()

tk.Label(root, text="작가").pack()
author_entry = tk.Entry(root)
author_entry.pack()

tk.Button(root, text="검색", command=search_books).pack(pady=5)

book_listbox = tk.Listbox(root, width=70, height=10)
book_listbox.pack(pady=10)

tk.Button(root, text="도서 전체 보기", command=fetch_all_books).pack()
tk.Button(root, text="도서 대여", command=rent_book).pack(pady=5)

# 실행 시 전체 도서 불러오기
fetch_all_books()

root.mainloop()
