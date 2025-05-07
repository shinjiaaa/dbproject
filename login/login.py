from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from app import get_db
from pydantic import BaseModel

router = APIRouter()

# login
class LoginData(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    
    if user and user.password == data.password:
        return {"message": "로그인 성공", "status": "success"}
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")
