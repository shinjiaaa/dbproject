import tkinter as tk
from login import login_ui

# GUI 초기화
root = tk.Tk()
root.title("DB 도서관리 및 대여시스템")
root.geometry("350x300")

login_ui.login_page(root)  # 로그인 페이지 표시

root.mainloop()  # 메인 루프 시작
