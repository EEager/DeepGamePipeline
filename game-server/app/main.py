from fastapi import FastAPI
from app.websocket.endpoints import router as ws_router
#from api.ranking import router as ranking_router

app = FastAPI()
app.include_router(ws_router)
#app.include_router(ranking_router)