from openai import OpenAI
from ...LLMInterface import LLMInterface
from ...LLMEnums import LLMRole
import logging

#temprature is degree of creativity of model
class OpenaiProvider(LLMInterface):
    def __init__(self,api_key:str,api_url:str=None,      default_input_max:int=1000,default_generation_max:int=1000,default_temperature:float=0.1):
        
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max = default_input_max
        self.default_generation_max = default_generation_max
        self.default_temperature = default_temperature
        
        self.generation_model_id = None
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = OpenAI(api_key=self.api_key,api_url=self.api_url)
        
        self.logger = logging.getLogger(__name__)
        
    def set_generation_model(self,model_id:str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self,model_id:str,embedding_size:int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
       
    #process text to fit the model input requirements
    def process_text(self,text:str):
        return text[:self.default_input_max].strip()
        
    def generate_text(self,prompt:str,chat_history:list[dict],max_tokens:int=None,temperature:float= None):
        
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None
        
        if not self.generation_model_id:
            self.logger.error("Generation model not initialized")
            return None
        
        max_output_tokens = max_tokens if max_tokens else self.default_generation_max
        
        temperature = temperature if temperature else self.default_temperature
        
        chat_history.append(
            self.construct_prompt(prompt=prompt,role=LLMRole.USER.value)
        )
        
        response = self.client.chat.completions.create(
            model=self.generation_model_id,
            messages=chat_history,
            max_tokens=max_output_tokens,
            temperature=temperature,
        )
        
        if not response or not response.choices or not len(response.choices)==0 or not response.choices[0].message.content:
            self.logger.error("Error while generating text with OpenAI")
            return None
            
        return response.choices[0].message.content
    
    def embed_text(self,text:str,document_type:str=None):
        
        if not self.client:
            self.logger.error("OpenAI client not initialized")
            return None
        
        if not self.embedding_model_id:
            self.logger.error("Embedding model not initialized")
            return None
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
        )
        
        if not response or not response.data or not len(response.data)==0 or not response.data[0].embedding:
            self.logger.error("Error while embedding text with OpenAI")
            
        return response.data[0].embedding
    
    def construct_prompt(self,prompt:str,role:str):
        return {
            "role":role,
            "content":self.process_text(prompt),
        }