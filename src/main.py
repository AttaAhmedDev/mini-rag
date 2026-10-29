from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helper.config import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.database_name = app.mongodb_client[settings.MONGO_DB_NAME]
    
    try:
        yield
    finally:
        app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
