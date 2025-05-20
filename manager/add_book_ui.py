import tkinter as tk
from tkinter import messagebox
import requests
from manager import manager_ui

def show_add_book_ui(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("도서 추가")
    root.geometry("400x500") 

    tk.Label(root, text="📚 도서 추가", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="도서 제목").pack()
    title_entry = tk.Entry(root)
    title_entry.pack()

    tk.Label(root, text="저자").pack()
    author_entry = tk.Entry(root)
    author_entry.pack()

    tk.Label(root, text="출판년도").pack()
    year_entry = tk.Entry(root)
    year_entry.pack()

    tk.Label(root, text="도서관 위치").pack()
    location_entry = tk.Entry(root)
    location_entry.pack()

    def register_book():
        data = {
            "book_title": title_entry.get(),  
            "author": author_entry.get(),
            "year": int(year_entry.get()),
            "library_location": location_entry.get(),
            "rental_status": True,         
            "is_deleted": False 
        }

        try:
            response = requests.post("http://localhost:8000/admin/book", json=data)
            if response.status_code == 200:
                messagebox.showinfo("성공", "도서가 등록되었습니다.")
                manager_ui.show_manager_ui(root)
            else:
                messagebox.showerror("오류", response.json().get("detail", "등록 실패"))
        except Exception as e:
            messagebox.showerror("서버 오류", f"연결 실패: {e}")

    tk.Button(root, text="등록", command=register_book).pack(pady=10)
    tk.Button(root, text="뒤로가기", command=lambda: manager_ui.show_manager_ui(root)).pack()
