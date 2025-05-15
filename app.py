from fastapi import FastAPI
from models import Base, User 
from database import engine, SessionLocal
from register.register import router as register_router
from login.login import router as login_router
from mainpage.mainpage import router as mainpage_router
from mypage.mypage import router as mypage_router
from manager.manager_r import router as manager_router

import uvicorn

app = FastAPI()

# 테이블이 없으면 생성
Base.metadata.create_all(bind=engine)

# 초기 책 데이터만 추가
@app.on_event("startup")
def init_books():
    from models import Book
    from database import SessionLocal

    db = SessionLocal()

       # 모든 도서를 '대여 가능' 상태로 초기화
    db.query(Book).update({Book.rental_status: True})

    initial_books = [
        {"book_title": "파이썬 프로그래밍", "author": "홍길동", "year": 2020, "library_location": "A1", "rental_status": True},
        {"book_title": "데이터베이스 기초", "author": "김철수", "year": 2018, "library_location": "B2", "rental_status": True},
        {"book_title": "알고리즘 개론", "author": "이영희", "year": 2021, "library_location": "C3", "rental_status": False}
    ]
    for book in initial_books:
        exists = db.query(Book).filter_by(book_title=book["book_title"], author=book["author"]).first()
        if not exists:
            db.add(Book(**book))
            print(f" 초기 도서 '{book['book_title']}' 추가됨")
    db.commit()
    db.close()


# 라우터 연결
app.include_router(register_router, tags=["회원가입"])
app.include_router(login_router, tags=["로그인"])
app.include_router(mainpage_router, tags=["메인"])
app.include_router(mypage_router, tags=["마이페이지"])
app.include_router(manager_router, prefix="/admin", tags=["관리자"])

# 서버 실행 (uvicorn으로 실행할 때만 작동)
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
