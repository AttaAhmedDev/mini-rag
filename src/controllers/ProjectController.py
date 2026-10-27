from fastapi import UploadFile
from .BaseController import BaseController
from models import ResponseEnums
import os



class ProjectController(BaseController):
    def __init__(self):
        super().__init__()
    
    def get_path_project(self,project_id:str):
        project_dir = os.path.join(self.file_path,project_id)
        
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir