import tkinter as tk
from tkinter import messagebox, ttk
import requests

def mypage_ui(root, user_id):
    # 다른 페이지 함수 import (화면 전환용)
    from login.login_ui import clear_widgets
    from login.login_ui import login_page
    from mainpage.mainpage_ui import mainpage_ui

    # 기존 위젯 지우기 (페이지 전환)
    clear_widgets(root)
    root.title("마이페이지")
    root.geometry("1000x500")

    # FastAPI 서버 주소
    BASE_URL = "http://127.0.0.1:8000/mypage"

    # ========== 대출 리스트 조회 ==========
    def get_rental_list():
        
        #사용자(user_id)의 대출 기록을 FastAPI 서버에서 조회
        # GET /rental_list 요청 (쿼리 파라미터로 user_id 전달)
        # 대출 정보(책 제목, 반납예정일, 위치 등)를 테이블(treeview)에 표시
        
        try:
            response = requests.get(f"{BASE_URL}/rental_list", params={"user_id": user_id})
            if response.status_code == 200:
                loans = response.json()
                treeview.delete(*treeview.get_children())  # 테이블 초기화

                if not loans:
                    messagebox.showinfo("대출 리스트", "대출한 책이 없습니다.")
                    return

                # 각 대출 기록 표시
                for loan in loans:
                    service_id = loan["service_id"]
                    book_title = loan["book_title"]
                    due_date = loan["due_date"]
                    location = loan["library_location"]

                    # 반납 상태 표시 (returned_at 값 유무로 판별)
                    if loan.get("returned_at") is not None:
                        status = "반납"
                        returned_display = loan["returned_at"].split("T")[0]
                    else:
                        status = "대출 중"
                        returned_display = "-"

                    # service_id는 사용자에게 표시하지 않고 tags로 저장 (연장 기능에서 사용)
                    treeview.insert("", "end", values=(book_title, due_date, location, status, returned_display), tags=(str(service_id),))
            else:
                messagebox.showwarning("경고", response.json().get("detail", "에러 발생"))
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # ========== 대출 연장 기능 ==========
    def extend_selected_book():
        """
        선택한 책의 대출 기간을 7일 연장
        - POST /extend_rental/{service_id} 요청
        - 쿼리 파라미터로 user_id, extension_days(7) 전달
        - 성공 시 새 반납일 안내 후 대출 리스트 새로고침
        """
        selected = treeview.selection()
        if not selected:
            messagebox.showwarning("선택 오류", "연장할 책을 선택하세요.")
            return

        # 선택한 대출 건의 service_id (tags에 저장된 값)
        service_id = treeview.item(selected[0])["tags"][0]

        try:
            response = requests.post(
                f"{BASE_URL}/extend_rental/{service_id}",
                params={
                    "extension_days": 7,  # 연장 일수 고정
                    "user_id": user_id
                }
            )
            if response.status_code == 200:
                messagebox.showinfo("연장 완료", response.json()["message"])
                get_rental_list()  # 연장 후 대출 리스트 새로고침
            else:
                messagebox.showwarning("연장 실패", response.json().get("detail", "에러"))
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # ========== UI 구성 ==========
    tk.Label(root, text="📘 마이페이지", font=("Arial", 16)).pack(pady=10)

    # 대출 리스트 테이블
    columns = ("책 제목", "반납예정일", "위치", "상태", "반납일")
    treeview = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for col in columns:
        treeview.heading(col, text=col)
    treeview.pack(padx=10, pady=10)

    # 버튼 구성
    tk.Button(root, text="⏳ 선택한 책 대출 연장", command=extend_selected_book).pack(pady=5)
    tk.Button(root, text="🏠 메인 페이지로", command=lambda: mainpage_ui(root, user_id)).pack(pady=5)
    tk.Button(root, text="🔓 로그아웃", command=lambda: login_page(root)).pack(pady=5)

    # 시작 시 대출 리스트 자동 조회
    get_rental_list()
