from helper.config import get_settings
from pathlib import Path 
import random , string
class BaseController:
    
    def __init__(self):
        self.settings = get_settings()
        self.file_path = str(Path(__file__).resolve().parent.parent / "assets" / "files")
    
    def generate_random_string(self,length:int=12):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))