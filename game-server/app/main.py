import os
import logging
# 개발/운영 환경별 로그 레벨 분기
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='[%(levelname)s] %(asctime)s %(name)s: %(message)s')

from fastapi import FastAPI
from app.websocket.endpoints import router as ws_router
#from api.ranking import router as ranking_router

app = FastAPI()
app.include_router(ws_router)
#app.include_router(ranking_router)