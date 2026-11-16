import os 
from string import Template

class TemplateParser:
    def __init__(self,language:str=None ,default_language:str = "en"):
        self.language = language or default_language
        self.default_language = default_language
        self.current_path = os.path.dirname(os.path.abspath(__file__))

    def set_language(self, language:str) -> None:
        if not language:
            self.language = self.default_language
        
        language_path = os.path.join(self.current_path, "locales", language)
        if os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get_template(self,group:str,key:str,vars:dict={}):
        if not group or not key:
            return None
        
        #there is as language value is None and Join can not deal with it``
        # print("current_path:", self.current_path)
        # print("language:", self.language)
        # print("group:", group)
        
        group_path = os.path.join(self.current_path, "locales", self.language,f"{group}.py")
        target_language = self.language
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, "locales", self.default_language, f"{group}.py")
            target_language = self.default_language
        # if the default language is not found, return None
        if not os.path.exists(group_path):
            return None
        module = __import__(f"stores.llm.templates.locales.{target_language}.{group}", fromlist=[group])
        
        if not hasattr(module, key):
            return None
        template = getattr(module, key)
        
        
        #as there is str and Template class in rag.py so str dont have substitute method so we need to check if the template is a Template class
        if isinstance(template,Template):
            return template.substitute(vars)
        
        return template