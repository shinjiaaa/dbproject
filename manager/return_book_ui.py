import tkinter as tk
from tkinter import ttk, messagebox
import requests


# 도서 반납 UI 함수
def show_return_book_ui(root):
    window = tk.Toplevel(root)
    window.title("도서 반납")
    window.geometry("800x500")

    tk.Label(window, text="📚 도서 반납", font=("Arial", 16)).pack(pady=10)

    # 검색창
    search_frame = tk.Frame(window)
    search_frame.pack(pady=5)

    tk.Label(search_frame, text="도서 검색").pack(side="left", padx=5)
    search_entry = tk.Entry(search_frame, width=40)
    search_entry.pack(side="left", padx=5)

    # book_id 컬럼도 포함된 Treeview 컬럼 정의
    columns = ("책 ID", "책 제목", "저자", "출판년도", "도서관 위치", "대출 상태")
    tree = ttk.Treeview(
        window, columns=columns, show="headings", height=12
    )  # 트리뷰 생성
    for col in columns:  # 트리뷰 컬럼 정의
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")
    tree.pack(pady=10)

    # 책 불러오기 함수
    def fetch_books(keyword=None):
        try:
            res = requests.get("http://localhost:8000/books_list")  # 책 목록 API 호출
            if res.status_code == 200:
                books = res.json()
                tree.delete(*tree.get_children())

                for book in books:
                    if book["rental_status"] is False:  # 대출 중인 책만
                        if (
                            keyword
                            and keyword.lower()
                            not in book["book_title"].lower()  # 검색어 필터링
                        ):
                            continue
                        tree.insert(  # 트리뷰에 책 정보 삽입
                            "",
                            "end",
                            iid=book["book_id"],  # 정수형으로 설정
                            values=(
                                book["book_id"],
                                book["book_title"],
                                book["author"],
                                book.get("year", ""),
                                book.get("library_location", ""),
                                "대출 중",
                            ),
                        )

        except Exception as e:
            messagebox.showerror("서버 오류", str(e))

    # 검색 버튼 동작
    def search_books():
        keyword = search_entry.get().strip()  # 검색어 가져오기
        fetch_books(keyword)  # 검색어로 책 목록 필터링

    tk.Button(search_frame, text="검색", command=search_books).pack(side="left", padx=5)

    # 책 목록 불러오기
    def return_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning(
                "선택 없음", "반납할 책을 선택하세요."
            )  # 선택된 책이 없을 때 경고 메시지 출력
            return

        # 선택된 책의 ID 가져오기
        book_id = int(selected[0])
        url = f"http://localhost:8000/admin/return_book/{book_id}"  # 반납 API URL
        print(f"요청 URL: {url}")  # 디버깅용 출력
        try:
            res = requests.post(url)
            print(f"응답 상태: {res.status_code}, 내용: {res.text}")  # 디버깅용 출력

            if res.status_code == 200:
                messagebox.showinfo("성공", res.json()["message"])  # 반납 성공 메시지
                fetch_books()
            else:
                # 에러 메시지를 문자열로 안전하게 변환
                detail_msg = res.json().get("detail", "반납 실패")  # 반납 실패 메시지
                if not isinstance(detail_msg, str):
                    detail_msg = str(detail_msg)
                messagebox.showerror("실패", detail_msg)
        except Exception as e:
            messagebox.showerror("서버 오류", str(e))  # 서버 연결 실패 메시지

    tk.Button(
        window, text="반납", width=10, command=return_selected
    ).pack()  # 반납 버튼

    fetch_books()
