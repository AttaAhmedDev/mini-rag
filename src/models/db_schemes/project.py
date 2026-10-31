from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from bson import ObjectId


class Project(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)
    
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    #for validation of project_id 
    @field_validator("project_id")
    @classmethod # this is a class method because we are validating the project_id for the entire class
    def validate_project_id(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return v
    
    @staticmethod # this is a static method because we are not dealing with any instance or class data
    def get_indexes():
        return [
            {
                "key":[("project_id", 1)],#1 is the index type, 1 is ascending, -1 is descending
                "unique":True,
                "name":"project_id_index",
            }
        ]