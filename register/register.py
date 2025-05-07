from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from app import get_db
from pydantic import BaseModel

router = APIRouter()

# register
class RegisterData(BaseModel):
    username: str
    password: str

@router.post("/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    # user 정보가 존재하는지 확인
    user = db.query(User).filter(User.username == data.username).first()
    
    if user:
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")
    
    new_user = User(username=data.username, password=data.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입 성공", "status": "success"}
