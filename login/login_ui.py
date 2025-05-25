import tkinter as tk
from tkinter import messagebox
import requests

from mainpage.mainpage_ui import mainpage_ui
from mypage.mypage_ui import mypage_ui


# ===== 로그인 화면 =====
def login_page(root):
    clear_widgets(root)  # 위젯 초기화

    tk.Label(root, text="로그인", font=("Arial", 16)).pack(pady=10)  # UI 제목

    tk.Label(root, text="아이디").pack()  # UI 아이디 입력
    login_id_entry = tk.Entry(root)
    login_id_entry.pack()

    tk.Label(root, text="비밀번호").pack()  # UI 비밀번호 입력
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    # 로그인 동작 함수
    def login_action():
        login_id = login_id_entry.get()  # 아이디 입력
        password = password_entry.get()  # 비밀번호 입력

        data = {"login_id": login_id, "password": password}  # 로그인 정보 딕셔너리
        # 서버에 로그인 요청
        try:
            response = requests.post("http://localhost:8000/login", json=data)
            if response.status_code == 200:
                res_json = response.json()
                messagebox.showinfo("성공", res_json["message"])

                if res_json.get("is_admin"):  # 관리자일 경우
                    from manager import manager_ui

                    manager_ui.show_manager_ui(root)  # 관리자 UI로 이동
                else:
                    user_id = res_json["user_id"]  # 여기서 user_id 추출
                    main_menu_page(root, user_id)  # 메인 메뉴로 이동
            else:
                messagebox.showerror("오류", response.json()["detail"])  # 로그인 실패
        except Exception as e:
            messagebox.showerror("서버 오류", f"연결 실패: {e}")  # 서버 연결 실패

    tk.Button(root, text="로그인", command=login_action).pack(pady=5)
    tk.Button(root, text="회원가입", command=lambda: register_page(root)).pack(pady=2)


# ===== 회원가입 화면 =====
def register_page(root):
    clear_widgets(root)

    tk.Label(root, text="회원가입", font=("Arial", 16)).pack(pady=10)  # UI 제목

    tk.Label(root, text="이름").pack()  # UI 이름 입력
    name_entry = tk.Entry(root)
    name_entry.pack()

    tk.Label(root, text="전화번호").pack()  # UI 전화번호 입력
    phone_entry = tk.Entry(root)
    phone_entry.pack()

    tk.Label(root, text="아이디").pack()  # UI 아이디 입력
    login_id_entry = tk.Entry(root)
    login_id_entry.pack()

    tk.Label(root, text="비밀번호").pack()  # UI 비밀번호 입력
    pw_entry = tk.Entry(root, show="*")
    pw_entry.pack()

    # 회원가입 완료 동작 함수
    def complete_register():
        name = name_entry.get()  # 이름 입력
        phone = phone_entry.get()  # 전화번호 입력
        login_id = login_id_entry.get()  # 아이디 입력
        password = pw_entry.get()  # 비밀번호 입력

        # 입력 값 검증
        data = {
            "name": name,
            "phone": phone,
            "login_id": login_id,
            "password": password,
        }

        # 서버에 회원가입 요청
        try:
            response = requests.post("http://localhost:8000/register", json=data)
            if response.status_code == 200:
                messagebox.showinfo("회원가입", "회원가입이 완료되었습니다.")
                login_page(root)
            else:
                messagebox.showerror(
                    "회원가입 실패", response.json().get("detail", "에러 발생")
                )
        except Exception as e:
            messagebox.showerror("서버 오류", f"연결 실패: {e}")

    tk.Button(root, text="완료", command=complete_register).pack(pady=5)


# ===== 메인 메뉴 =====
def main_menu_page(root, user_id):
    clear_widgets(root)
    tk.Label(root, text="메인 메뉴", font=("Arial", 16)).pack(pady=10)
    tk.Button(
        root, text="도서 검색", width=20, command=lambda: mainpage_ui(root, user_id)
    ).pack(pady=3)
    tk.Button(
        root, text="마이페이지", width=20, command=lambda: mypage_ui(root, user_id)
    ).pack(pady=3)
    tk.Button(root, text="로그아웃", width=20, command=lambda: login_page(root)).pack(
        pady=3
    )


# ===== 위젯 클리어 =====
def clear_widgets(root):
    for widget in root.winfo_children():
        widget.destroy()
