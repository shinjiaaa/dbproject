from fastapi import FastAPI
from models import Base
from database import engine
from register.register import router as register_router
from login.login import router as login_router
from mainpage.mainpage import router as mainpage_router
from mypage.mypage import router as mypage_router
from manager.manager import router as manager_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(register_router, tags=["회원가입"])
app.include_router(login_router, tags=["로그인"])
app.include_router(mainpage_router, tags=["메인"])
app.include_router(mypage_router, tags=["마이페이지"])
app.include_router(manager_router, prefix="/admin" , tags=["관리자"])

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
