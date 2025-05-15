from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User
from database import get_db
from datetime import timedelta
from passlib.context import CryptContext

from mypage.mypage import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginData(BaseModel):
    login_id: str
    password: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.login_id == data.login_id).first()

    # 여기서 암호화된 비밀번호 비교
    if user and verify_password(data.password, user.password):
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.login_id},
            expires_delta=access_token_expires
        )
        return {
            "message": "로그인 성공",
            "is_admin": user.admin,
            "access_token": access_token,
            "token_type": "bearer"
        }
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")
    
    
#회원가입
class RegisterData(BaseModel):
    name: str
    phone: str
    login_id: str
    password: str

@router.post("/register")
async def register_user(data: RegisterData, db: Session = Depends(get_db)):
    if db.query(User).filter(User.login_id == data.login_id).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 아이디입니다.")

    user = User(
        name=data.name,
        phone=data.phone,
        login_id=data.login_id,
        password=pwd_context.hash(data.password),  # 해시 처리
        admin=False  # 일반 사용자로 등록
    )
    db.add(user)
    db.commit()

    return {"message": "회원가입 성공"}
