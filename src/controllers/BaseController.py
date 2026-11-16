from helper.config import get_settings
from pathlib import Path 
import random , string
import os
class BaseController:
    
    def __init__(self):
        self.settings = get_settings()
        self.file_path = str(Path(__file__).resolve().parent.parent / "assets" / "files")
        # database directory
        self.database_dir = str(Path(__file__).resolve().parent.parent / "assets" / "database")
    
    def generate_random_string(self,length:int=12):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    def get_database_dir(self,db_name:str):
        db_path = os.path.join(self.database_dir, db_name)
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        return db_path