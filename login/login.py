from fastapi import FastAPI, APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import User

app = FastAPI()
router = APIRouter()

class LoginData(BaseModel):
    name: str
    password: str

@router.post("/login")
async def login(data: LoginData, db: Session = Depends(get_db)):
    user = db.query(User).filter(user.login_id == data.name).first()
    if user and user.password == data.password:
        return {"message": "로그인 성공", "status": "success"}
    else:
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")

app.include_router(router)
