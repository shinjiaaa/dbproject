import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from manager import add_book_ui
from manager import delete_book_ui
from manager import return_book_ui

def show_manager_ui(root):
    for widget in root.winfo_children():
        widget.destroy()

    root.title("관리자 모드")
    root.geometry("350x300")  # 창 크기 유지

    tk.Label(root, text="관리자 모드", font=("Arial", 16)).pack(pady=10)

    # 이등분된 container
    container = tk.Frame(root)
    container.pack(fill="both", expand=True, padx=10, pady=5)

    # 왼쪽 영역: 도서 관리
    frame_left = tk.Frame(container)
    frame_left.pack(side="left", fill="both", expand=True)

    tk.Label(frame_left, text="도서 관리", font=("Arial", 13)).pack(pady=(20, 10))
    tk.Button(frame_left, text="도서 추가", width=13,command=lambda: add_book_ui.show_add_book_ui(root)).pack(pady=2)
    tk.Button(frame_left, text="도서 삭제", width=13,command=lambda: delete_book_ui.show_delete_book_ui(root)).pack(pady=2)
    tk.Button(frame_left, text="반납", width=13,command=lambda: return_book_ui.show_return_book_ui(root)).pack(pady=2)

    # 오른쪽 영역: 블랙리스트 관리
    frame_right = tk.Frame(container)
    frame_right.pack(side="right", fill="both", expand=True)

    tk.Label(frame_right, text="블랙리스트 관리", font=("Arial", 13)).pack(pady=(20, 10))
    tk.Button(frame_right, text="블랙리스트 관리", width=13).pack(pady=2)

# 단독 실행
if __name__ == "__main__":
    root = tk.Tk()
    show_manager_ui(root)
    root.mainloop()
