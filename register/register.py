from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from database import get_db
from pydantic import BaseModel

router = APIRouter()

class RegisterData(BaseModel):
    login_id: str
    username: str
    password: str

@router.post("/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    # login_id 중복 확인
    user = db.query(User).filter(User.login_id == data.login_id).first()
    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 로그인 ID입니다.")

    # username 중복 확인
    user = db.query(User).filter(User.name == data.username).first()
    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    # 새로운 사용자 추가
    new_user = User(login_id=data.login_id, name=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입 성공", "status": "success"}
