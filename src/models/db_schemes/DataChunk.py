from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Optional

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(...,min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(...,gt=0)
    chunk_project_id: ObjectId
    
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    @staticmethod # this is a static method because we are not dealing with any instance or class data
    def get_indexes():
        return [
            {
                "key":[("chunk_project_id", 1)],
                "name":"chunk_project_id_index",
                "unique":False,
            }
        ]