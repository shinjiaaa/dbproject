from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import User
from database import get_db
from datetime import timedelta
from passlib.context import CryptContext


router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # 비밀번호 해싱


# 로그인 데이터 모델
class LoginData(BaseModel):
    login_id: str
    password: str


# 비밀번호 해싱 함수
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)  # 비밀번호 검증


# 로그인 라우터
@router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = (
        db.query(User).filter(User.login_id == data.login_id).first()
    )  # 로그인 ID로 사용자 조회

    # 사용자 존재 여부 및 비밀번호 확인
    if user and verify_password(data.password, user.password):
        return {
            "message": "로그인 성공",
            "user_id": user.user_id,
            "is_admin": user.admin,
        }
    # 로그인 실패 시 예외 처리
    else:
        raise HTTPException(
            status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다."
        )
