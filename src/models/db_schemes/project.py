from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
from bson import ObjectId


class Project(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)
    
    model_config = ConfigDict(arbitrary_types_allowed=True, populate_by_name=True)
    
    @field_validator("project_id")
    @classmethod # this is a class method because we are validating the project_id for the entire class
    def validate_project_id(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Project ID must be alphanumeric")
        return v