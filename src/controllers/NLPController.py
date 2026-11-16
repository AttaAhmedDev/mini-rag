from .BaseController import BaseController
from models.db_schemes import Project,DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List

class NLPController(BaseController):
    def __init__(self,vectordb_client,generation_client,embeddings_client,template_parser):
        super().__init__()
        
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embeddings_client = embeddings_client
        self.template_parser = template_parser
        
    # get collection name from project id
    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()
    
    # reset vectordb collection
    def reset_vectordb_collection(self,project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    # get vectordb collection info
    def get_vectordb_collection_info(self,project:Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
        #model_dump() is used to convert the collection info to a dictionary
        return collection_info.model_dump() if collection_info else None
    
    
    def index_into_vectordb(self,project:Project,chunks:List[DataChunk],do_reset:bool=False):
        
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        texts =[chunk.chunk_text for chunk in chunks]
        metadata =[chunk.chunk_metadata for chunk in chunks]
        vectors = [
            self.embeddings_client.embed_text(text=text,document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]
        
        _ = self.vectordb_client.create_collection(collection_name=collection_name,embedding_size=self.embeddings_client.embedding_size,do_reset=do_reset)
        
        return self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            vectors=vectors,
            metadata=metadata,
        )
        
    def search_vectordb_collection(self,project:Project,query:str,limit:int=10):
        
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        vector = self.embeddings_client.embed_text(text=query,document_type=DocumentTypeEnum.QUERY.value)
        
        if not vector or len(vector) == 0:
            return False
        
        results = self.vectordb_client.search_by_vector(collection_name=collection_name,vector=vector,limit=limit)
        
        return [result.model_dump() for result in results] if results else False
    
    def answer_rag_question(self,project:Project,query:str,limit:int=10):
        
        retrieved_documents = self.search_vectordb_collection(project=project,query=query,limit=limit)
        
        if not retrieved_documents:
            return None
        
        system_prompt = self.template_parser.get_template(group="rag",key="system_prompt")
        
        documents_prompts = "\n".join([
            self.template_parser.get_template(group="rag",key="document_prompt",vars={"doc_number":idx+1,"doc_content":document["text"]})
            for idx,document in enumerate(retrieved_documents)
        ] )
        
        footer_prompt = self.template_parser.get_template(group="rag",key="footer_prompt",vars={"question":query})
        
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role = self.generation_client.enums.SYSTEM.value
            )
        ]
        
        full_prompt = "\n\n".join([documents_prompts,footer_prompt])
        
        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history
        )
        
        return answer ,full_prompt,chat_history