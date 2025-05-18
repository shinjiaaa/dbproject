import tkinter as tk
from tkinter import messagebox
import requests

BACKEND_URL = "http://127.0.0.1:8000"  

def fetch_blacklist():
    try:
        response = requests.get(f"{BACKEND_URL}/blacklist")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("블랙리스트 불러오기 실패:", e)
        return []

def remove_from_blacklist(user_id, refresh_callback):
    try:
        response = requests.post(f"{BACKEND_URL}/blacklist/remove/{user_id}")
        response.raise_for_status()
        messagebox.showinfo("알림", "블랙리스트가 해지되었습니다.")
        refresh_callback()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("에러", f"해지 실패: {e}")

def show_blacklist_ui(root, go_back_callback=None):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("블랙리스트 관리")

    # 타이틀
    tk.Label(root, text="블랙리스트 관리", font=("Arial", 18)).pack(pady=10)

    # 테이블 프레임
    table_frame = tk.Frame(root)
    table_frame.pack(padx=10, pady=10)

    headers = ["사용자 ID", "이름", "전화번호", "블랙리스트 등록일자", "해지"]
    for i, h in enumerate(headers):
        tk.Label(table_frame, text=h, font=("Arial", 11, "bold"), width=18).grid(row=0, column=i, padx=5, pady=5)

    def refresh_table():
        # 기존 테이블 내용 삭제 (첫 번째 row 제외)
        for widget in table_frame.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()

        blacklist = fetch_blacklist()

        for row_idx, user in enumerate(blacklist, start=1):
            tk.Label(table_frame, text=user.get("user_id", "-")).grid(row=row_idx, column=0, padx=5, pady=5)
            tk.Label(table_frame, text=user.get("name", "-")).grid(row=row_idx, column=1, padx=5, pady=5)
            tk.Label(table_frame, text=user.get("phone", "-")).grid(row=row_idx, column=2, padx=5, pady=5)
            tk.Label(table_frame, text=user.get("blacklisted_by", "-")).grid(row=row_idx, column=3, padx=5, pady=5)

            tk.Button(
                table_frame,
                text="해지",
                command=lambda uid=user["user_id"]: remove_from_blacklist(uid, refresh_table)
            ).grid(row=row_idx, column=4, padx=5, pady=5)

    refresh_table()

    # 뒤로 가기 버튼
    tk.Button(root, text="뒤로 가기", width=12, command=lambda: go_back_callback() if go_back_callback else root.destroy()).pack(pady=15)
