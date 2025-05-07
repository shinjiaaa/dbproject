import tkinter as tk
from tkinter import messagebox

# 메인 윈도우 설정
root = tk.Tk()
root.title("DB 도서관리 및 대여시스템")
root.geometry("350x300")

# ===== 로그인 화면 =====
def login_page():
    clear_widgets()

    tk.Label(root, text="로그인", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="아이디").pack()
    login_id_entry = tk.Entry(root)
    login_id_entry.pack()

    tk.Label(root, text="비밀번호").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    def login_action():
        user_id = login_id_entry.get()
        password = password_entry.get()
        # 여기에 실제 로그인 요청 넣을 수 있음
        if user_id == "admin" and password == "1234":
            messagebox.showinfo("성공", "로그인 성공")
            main_menu_page()
        else:
            messagebox.showerror("오류", "아이디 또는 비밀번호가 틀렸습니다.")

    tk.Button(root, text="로그인", command=login_action).pack(pady=5)
    tk.Button(root, text="회원가입", command=register_page).pack(pady=2)

# ===== 회원가입 화면 =====
def register_page():
    clear_widgets()

    tk.Label(root, text="회원가입", font=("Arial", 16)).pack(pady=10)

    tk.Label(root, text="이름").pack()
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="전화번호").pack()
    phone_entry = tk.Entry(root)
    phone_entry.pack()

    tk.Label(root, text="아이디").pack()
    user_id_entry = tk.Entry(root)
    user_id_entry.pack()

    tk.Label(root, text="비밀번호").pack()
    pw_entry = tk.Entry(root, show="*")
    pw_entry.pack()

    def complete_register():
        # 실제 서버 전송 로직 대신 UI 팝업만 사용
        messagebox.showinfo("회원가입", "회원가입이 완료되었습니다.")
        login_page()

    tk.Button(root, text="완료", command=complete_register).pack(pady=5)

# ===== 메인 메뉴 (로그인 성공 후 진입) =====
def main_menu_page():
    clear_widgets()
    tk.Label(root, text="메인 메뉴", font=("Arial", 16)).pack(pady=10)
    tk.Button(root, text="도서 검색", width=20).pack(pady=3)
    tk.Button(root, text="마이페이지", width=20).pack(pady=3)
    tk.Button(root, text="관리자 모드", width=20).pack(pady=3)
    tk.Button(root, text="로그아웃", width=20, command=login_page).pack(pady=3)

# ===== 유틸: 현재 화면 위젯 모두 제거 =====
def clear_widgets():
    for widget in root.winfo_children():
        widget.destroy()

# 프로그램 시작 시 로그인 화면부터
login_page()

root.mainloop()
