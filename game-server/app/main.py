import os
import logging
# 개발/운영 환경별 로그 레벨 분기
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='[%(levelname)s] %(asctime)s %(name)s: %(message)s')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from app.routers import game_router
from app.websocket.game.endpoints import router as ws_router
from app.websocket.game.lobby_manager import lobby_manager

#from api.ranking import router as ranking_router

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
#app.include_router(game_router)
app.include_router(ws_router)

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행되는 이벤트 핸들러"""
    logging.info("Starting server...")
    await lobby_manager.start()

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행되는 이벤트 핸들러"""
    logging.info("Shutting down server...")
    await lobby_manager.stop()