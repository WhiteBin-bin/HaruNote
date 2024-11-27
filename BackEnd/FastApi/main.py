from fastapi import FastAPI
from routes.users import user_router
from contextlib import asynccontextmanager
from database.connection import conn
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn()  # 데이터베이스 연결 초기화
    yield


# FastAPI 애플리케이션 생성
app = FastAPI(lifespan=lifespan)

# 사용자 라우터 등록
app.include_router(user_router, prefix="/user")

# CORS 설정: 로컬 프론트엔드와 연동 가능하도록 허용
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 등 프론트엔드 도메인 허용
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)