import tkinter as tk
from tkinter import messagebox, ttk
import requests


# 마이페이지 UI 함수
def mypage_ui(root, user_id):
    from login.login_ui import clear_widgets
    from login.login_ui import login_page
    from mainpage.mainpage_ui import mainpage_ui

    clear_widgets(root)
    root.title("마이페이지")
    root.geometry("1000x500")

    BASE_URL = "http://127.0.0.1:8000/mypage"

    # ========== 대출 리스트 조회 ==========
    def get_rental_list():
        # 사용자 ID가 없으면 경고 메시지
        try:
            response = requests.get(
                f"{BASE_URL}/rental_list",
                params={"user_id": user_id},  # 대출 리스트 API 호출
            )
            # 서버에서 대출 리스트를 가져옴
            if response.status_code == 200:
                loans = response.json()
                treeview.delete(*treeview.get_children())

                # 대출 리스트가 비어 있을 시 messagebox 표시
                if not loans:
                    messagebox.showinfo("대출 리스트", "대출한 책이 없습니다.")
                    return

                # 대출 리스트가 있을 경우 트리뷰에 추가
                for loan in loans:
                    service_id = loan["service_id"]
                    book_title = loan["book_title"]
                    due_date = loan["due_date"]
                    location = loan["library_location"]

                    # 대출 상태 결정
                    if loan.get("returned_at") is not None:
                        status = "반납"  # 반납된 경우
                        returned_display = loan["returned_at"].split("T")[
                            0
                        ]  # 반납일 표시
                    else:
                        status = "대출 중"  # 대출 중인 경우
                        returned_display = "-"  # 반납일이 없으므로 표시하지 않음

                    # service_id는 사용자에게 안 보이게 tags로만 저장
                    treeview.insert(
                        "",
                        "end",
                        values=(
                            book_title,
                            due_date,
                            location,
                            status,
                            returned_display,
                        ),
                        tags=(str(service_id),),
                    )
            else:  # 에러 발생 시
                messagebox.showwarning(
                    "경고", response.json().get("detail", "에러 발생")
                )
        except Exception as e:  # 서버 연결 실패 시
            messagebox.showerror("오류", str(e))

    # ========== 대출 연장 ==========
    def extend_selected_book():  # 선택한 책 연장
        selected = treeview.selection()
        # 선택된 책이 없으면 경고 메시지
        if not selected:
            messagebox.showwarning(
                "선택 오류", "연장할 책을 선택하세요."
            )  # 선택된 책이 없을 때 경고 메시지
            return

        # 선택된 책의 service_id 가져오기
        service_id = treeview.item(selected[0])["tags"][0]

        try:
            #  쿼리 파라미터로 user_id, extension_days 전달
            response = requests.post(
                f"{BASE_URL}/extend_rental/{service_id}",  # 연장 API 호출
                params={
                    "extension_days": 7,
                    "user_id": user_id,
                },  # 연장 일수 7일로 설정
            )
            if response.status_code == 200:
                messagebox.showinfo(
                    "연장 완료", response.json()["message"]
                )  # 연장 성공 메시지
                get_rental_list()  # 다시 새로고침
            else:
                messagebox.showwarning(
                    "연장 실패",
                    response.json().get("detail", "에러"),  # 연장 실패 메시지
                )
        except Exception as e:
            messagebox.showerror("오류", str(e))  # 서버 연결 실패 메시지

    # ========== UI 구성 ==========
    tk.Label(root, text="📘 마이페이지", font=("Arial", 16)).pack(pady=10)

    columns = ("책 제목", "반납예정일", "위치", "상태", "반납일")
    treeview = ttk.Treeview(root, columns=columns, show="headings", height=10)

    # 트리뷰 컬럼 정의
    for col in columns:
        treeview.heading(col, text=col)
    treeview.pack(padx=10, pady=10)

    tk.Button(root, text="⏳ 선택한 책 대출 연장", command=extend_selected_book).pack(
        pady=5
    )
    tk.Button(
        root, text="🏠 메인 페이지로", command=lambda: mainpage_ui(root, user_id)
    ).pack(pady=5)
    tk.Button(root, text="🔓 로그아웃", command=lambda: login_page(root)).pack(pady=5)

    # 시작하자마자 대출 리스트 출력
    get_rental_list()
