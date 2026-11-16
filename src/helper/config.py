from pydantic_settings import BaseSettings , SettingsConfigDict

class Settings(BaseSettings):
    
    APP_NAME: str
    APP_VERSION: str
    
    FILE_TYPES:list
    FILE_MAX_SIZE:int
    FILE_CHUNK_SIZE:int
    
    MONGO_URI:str
    MONGO_DB_NAME:str
    
    GENERATION_BACKEND:str
    EMBEDDING_BACKEND:str
    OPENAI_API_KEY:str
    COHERE_API_KEY:str
    OPENAI_API_URL:str = None
    GENERATION_MODEL_ID:str
    EMBEDDING_MODEL_ID:str
    EMBEDDING_MODEL_SIZE:int 
    DEFAULT_INPUT_MAX:int
    DEFAULT_GENERATION_MAX:int 
    DEFAULT_TEMPERATURE:float 
    
    #================= VECTOR DB CONFIGURATION =================
    VECTOR_DB_TYPE:str
    QDRANT_DB_PATH:str
    QDRANT_DISTANCE_METHOD:str
    
    
    #================= TEMPLATE CONFIGURATION =================
    DEFAULT_LANGUAGE:str
    PRIMARY_LANGUAGE:str
    class Config:
        env_file = ".env"
        
def get_settings()->Settings:
    return Settings()