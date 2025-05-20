# 빈 __init__.py 파일을 mypage 폴더에 생성
init_file_path = "/mnt/data/mypage/__init__.py"

# 먼저 폴더가 없다면 생성
import os
os.makedirs("/mnt/data/mypage", exist_ok=True)

# 빈 __init__.py 생성
with open(init_file_path, "w", encoding="utf-8") as f:
    f.write("")

init_file_path
