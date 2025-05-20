import tkinter as tk
from tkinter import messagebox
import requests

# 서버 URL 설정
BASE_URL = "http://127.0.0.1:8000/mypage"


# 이 함수만 외부에서 호출되며, window는 Toplevel로 전달됨
def mypage_ui(window, user_id):
    window.title("도서 대여 관리 시스템")
    window.geometry("350x300")

    # 사용자 ID 라벨 (readonly로 보여주기)
    tk.Label(window, text=f"사용자 ID: {user_id}").pack()

    # 대출 리스트 조회
    def get_rental_list():
        try:
            response = requests.get(
                f"{BASE_URL}/rental_list", params={"user_id": user_id}
            )
            if response.status_code == 200:
                loans = response.json()
                result = ""
                for loan in loans:
                    result += f"책 제목: {loan['book_title']}, 반납일: {loan['due_date']}, 위치: {loan['library_location']}, 상태: {loan['rental_status']}\n"
                messagebox.showinfo("대출 리스트", result)
            else:
                messagebox.showwarning("경고", response.json()["detail"])
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # 대출 연장
    def extend_rental():
        service_id = entry_service_id.get()
        extension_days = entry_extension.get()
        try:
            response = requests.post(
                f"{BASE_URL}/extend_rantal/{service_id}",
                json={"extension_days": int(extension_days)},
            )
            if response.status_code == 200:
                messagebox.showinfo("대출 연장", response.json()["message"])
            else:
                messagebox.showwarning("경고", response.json()["detail"])
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # 책 반납
    def return_book():
        service_id = entry_service_id.get()
        try:
            response = requests.post(f"{BASE_URL}/return_book/{service_id}")
            if response.status_code == 200:
                messagebox.showinfo("반납 완료", response.json()["message"])
            else:
                messagebox.showwarning("경고", response.json()["detail"])
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # 위젯 구성
    tk.Button(window, text="대출 리스트 조회", command=get_rental_list).pack(pady=5)

    tk.Label(window, text="서비스 ID:").pack()
    entry_service_id = tk.Entry(window)
    entry_service_id.pack()

    tk.Label(window, text="연장 일수:").pack()
    entry_extension = tk.Entry(window)
    entry_extension.pack()

    tk.Button(window, text="대출 연장", command=extend_rental).pack(pady=5)
    tk.Button(window, text="책 반납", command=return_book).pack(pady=5)
