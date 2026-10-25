from fastapi import UploadFile
from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ResponseEnums
import re, os
class DataController(BaseController):
    def __init__(self):
        super().__init__()
        self.scale_size = 1024*1024    
    def validate_file(self,file:UploadFile):
        if file.content_type not in self.settings.FILE_TYPES:
            return ResponseEnums.FILE_TYPE_NOT_SUPPORTED.value
        if file.size > self.settings.FILE_MAX_SIZE*self.scale_size:
            return ResponseEnums.FILE_SIZE_TOO_LARGE.value
        return True
    
    
    def get_clean_file_name(self, original_file_name: str) -> str:
        file_name = os.path.basename(original_file_name).strip()
        return re.sub(r"[^\w.-]", "_", file_name)
    
    def generate_unique_file_path(self, original_file_name: str, project_id: str) -> str:
        project_path = ProjectController().get_path_project(project_id=project_id)
        clean_file_name = self.get_clean_file_name(original_file_name)
        stem, extension = os.path.splitext(clean_file_name)
        while True:
            random_string = self.generate_random_string()
            unique_file_name = f"{random_string}_{stem}{extension}"
            new_file_path = os.path.join(project_path, unique_file_name)
            if not os.path.exists(new_file_path):
                return new_file_path , unique_file_name