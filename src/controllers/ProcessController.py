from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from models import ProcessEnums
import uuid

class ProcessController(BaseController):
    def __init__(self,project_id:str):
        super().__init__()
        self.project_id = project_id
        self.project_path=ProjectController().get_path_project(project_id=project_id)
        
    def get_file_extension(self,file_id:str):
        return os.path.splitext(file_id)[-1]
    
    #in this method we will load the file and return the documents (loader and file)
    def get_file_documents(self,file_id:str):
        file_ext = self.get_file_extension(file_id=file_id)
        file_path = os.path.join(self.project_path,file_id)
        if file_ext == ProcessEnums.PDF.value:
            return PyMuPDFLoader(file_path,encoding="utf-8").load()
        if file_ext == ProcessEnums.TEXT.value:
            return TextLoader(file_path,encoding="utf-8").load()
        return None
    
    def get_file_chunks(self,file_content:list,file_id:str,chunk_size:int=100,overlap_size:int=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=overlap_size,
            length_function=len)
        
        file_content_texts =[
            rec.page_content
            for rec in file_content
        ]
        
        file_content_metadata =[
            rec.metadata
            for rec in file_content
        ]
        
        chunks = text_splitter.create_documents(file_content_texts,metadatas=file_content_metadata)
        
        
        # [
        #     {
        #         "id":str(uuid.uuid4()),
        #         "chunk":chunk.page_content,
        #         "metadata":chunk.metadata
        #     }
        #     for chunk in chunks
        # ]
        
        return chunks