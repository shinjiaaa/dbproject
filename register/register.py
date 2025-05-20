from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from database import get_db
from pydantic import BaseModel
from passlib.context import CryptContext

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

# 패스워드 암호화
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/admin_signup")
def create_admin_user(name: str, login_id: str, password: str, db: Session = Depends(get_db)):
    # 로그인 아이디가 이미 존재하는지 확인
    db_user = db.query(User).filter(User.login_id == login_id).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Login ID already exists")
    
    # 패스워드 암호화
    hashed_password = pwd_context.hash(password)
    
    # 어드민 생성
    new_user = User(
        name=name,
        login_id=login_id,
        password=hashed_password,
        admin=True  # 어드민 필드 설정
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Admin user created successfully", "user_id": new_user.user_id}

