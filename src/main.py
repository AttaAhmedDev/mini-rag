from contextlib import asynccontextmanager
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from routes import base, data
from helper.config import get_settings
from stores.llm import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.database_name = app.mongodb_client[settings.MONGO_DB_NAME]
    
    llm_provider_factory = LLMProviderFactory(settings)
    #create generation provider
    app.generation_provider = llm_provider_factory.create_provider(provider=settings.GENERATION_BACKEND)
    app.generation_provider.set_generation_model(model_id=settings.GENERATION_MODEL_ID)
    #create embedding provider
    app.embedding_provider = llm_provider_factory.create_provider(provider=settings.EMBEDDING_BACKEND)
    app.embedding_provider.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,embedding_size=settings.EMBEDDING_MODEL_SIZE)
    
    try:
        yield
    finally:
        app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.include_router(base.base_router)
app.include_router(data.data_router)
