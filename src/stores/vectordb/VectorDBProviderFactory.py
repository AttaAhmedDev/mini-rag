from .providers import QdrantDB
from helper import Settings
from .VectorDBEnums import VectorDBType
from controllers import BaseController
class VectorDBProviderFactory:
    def __init__(self, config:Settings):
        self.config = config
        self.base_controller = BaseController()
        
    def create_provider(self, provider:str):
        if provider == VectorDBType.QDRANT.value:
            return QdrantDB(
                db_path=self.base_controller.get_database_dir(db_name=self.config.QDRANT_DB_PATH),
                distance_method=self.config.QDRANT_DISTANCE_METHOD
            )
        return None