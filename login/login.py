from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User
from database import get_db
from datetime import timedelta

from mypage.mypage import create_access_token

router = APIRouter()

class LoginData(BaseModel):
    name: str
    password: str

# 로그인 시 JWT 발급
@router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login_id == data.name).first()
    if user and user.password == data.password:
        # 사용자 정보로 JWT 발급
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(data={"sub": user.user_id}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")
