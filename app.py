from fastapi import FastAPI
from register import router as register_router
from login import router as login_router
from main import router as main_router

app = FastAPI()

# 라우터 등록
app.include_router(register_router, prefix="/api")
app.include_router(login_router, prefix="/api")
app.include_router(main_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
