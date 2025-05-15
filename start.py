# start.py

import tkinter as tk
from login import login_ui

root = tk.Tk()
root.title("DB 도서관리 및 대여시스템")
root.geometry("350x300")

login_ui.login_page(root)

root.mainloop()
