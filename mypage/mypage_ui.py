import tkinter as tk
from tkinter import messagebox
import requests

# 서버 URL 설정
BASE_URL = "http://127.0.0.1:8000/mypage"

# GUI 메인 윈도우 설정
root = tk.Tk()
root.title("도서 대여 관리 시스템")
root.geometry("350x300")

# 대출 리스트 조회
def get_rental_list():
    user_id = entry_user_id.get()
    try:
        response = requests.get(f"{BASE_URL}/rental_list", params={"user_id": user_id})
        if response.status_code == 200:
            loans = response.json()
            result = ""
            for loan in loans:
                result += f"책 제목: {loan['book_title']}, 반납일: {loan['due_date']}, 위치: {loan['library_location']}, 상태: {loan['rental_status']}\n"
            messagebox.showinfo("대출 리스트", result)
        else:
            messagebox.showwarning("경고", response.json()['detail'])
    except Exception as e:
        messagebox.showerror("오류", str(e))

# 대출 연장
def extend_rental():
    service_id = entry_service_id.get()
    extension_days = entry_extension.get()
    try:
        response = requests.post(f"{BASE_URL}/extend_rantal/{service_id}", json={"extension_days": int(extension_days)})
        if response.status_code == 200:
            messagebox.showinfo("대출 연장", response.json()['message'])
        else:
            messagebox.showwarning("경고", response.json()['detail'])
    except Exception as e:
        messagebox.showerror("오류", str(e))

# 책 반납
def return_book():
    service_id = entry_service_id.get()
    try:
        response = requests.post(f"{BASE_URL}/return_book/{service_id}")
        if response.status_code == 200:
            messagebox.showinfo("반납 완료", response.json()['message'])
        else:
            messagebox.showwarning("경고", response.json()['detail'])
    except Exception as e:
        messagebox.showerror("오류", str(e))

# 사용자 ID 입력
tk.Label(root, text="사용자 ID:").pack()
entry_user_id = tk.Entry(root)
entry_user_id.pack()
tk.Button(root, text="대출 리스트 조회", command=get_rental_list).pack()

# 서비스 ID 및 연장 입력
tk.Label(root, text="서비스 ID:").pack()
entry_service_id = tk.Entry(root)
entry_service_id.pack()
tk.Label(root, text="연장 일수:").pack()
entry_extension = tk.Entry(root)
entry_extension.pack()
tk.Button(root, text="대출 연장", command=extend_rental).pack()

# 반납 버튼
tk.Button(root, text="책 반납", command=return_book).pack()

root.mainloop()
