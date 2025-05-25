from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from database import get_db
from pydantic import BaseModel
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 비밀번호 해싱


# 회원가입 요청 모델
class RegisterData(BaseModel):
    name: str
    phone: str
    login_id: str
    password: str


# 일반 사용자 회원가입
@router.post("/register")
async def register(data: RegisterData, db: Session = Depends(get_db)):
    # login_id 중복 확인
    if db.query(User).filter(User.login_id == data.login_id).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 로그인 ID입니다.")

    # 비밀번호 해시 처리
    hashed_password = pwd_context.hash(data.password)

    # 사용자 등록 (admin=False)
    new_user = User(
        name=data.name,
        login_id=data.login_id,
        password=hashed_password,
        phone=data.phone,
        admin=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입 성공", "status": "success"}


# 관리자 계정 생성
@router.post("/admin_signup")
def create_admin_user(
    name: str, login_id: str, password: str, db: Session = Depends(get_db)
):
    # login_id 중복 확인
    if db.query(User).filter(User.login_id == login_id).first():
        raise HTTPException(
            status_code=400, detail="Login ID already exists"
        )  # 중복된 로그인 ID 예외 처리

    # 비밀번호 해시 처리
    hashed_password = pwd_context.hash(password)

    # 관리자 계정 생성
    new_user = User(
        name=name,
        login_id=login_id,
        password=hashed_password,
        admin=True,  # 관리자이므로 True
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Admin user created successfully", "login_id": new_user.login_id}
