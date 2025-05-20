import tkinter as tk
from tkinter import messagebox
import requests

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

        data = {"name": user_id, "password": password}
        try:
            response = requests.post("http://localhost:8000/login", json=data)
            if response.status_code == 200:
                res_json = response.json()
                messagebox.showinfo("성공", res_json["message"])
            
                if res_json.get("is_admin"):  #관리자일 경우
                    import manager.manager_ui as manager_ui
                    manager_ui.show_manager_ui(root)
                else:
                    main_menu_page()
            else:
                messagebox.showerror("오류", response.json()["detail"])
        except Exception as e:
            messagebox.showerror("서버 오류", f"연결 실패: {e}")


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
        messagebox.showinfo("회원가입", "회원가입이 완료되었습니다.")  # 추후 서버 연동 가능
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
