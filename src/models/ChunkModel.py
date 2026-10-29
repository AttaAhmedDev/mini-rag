from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnums import DataBaseEnums
from bson import ObjectId
from pymongo import InsertOne
from pymongo.errors import BulkWriteError

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[
            DataBaseEnums.Collection_DATA_CHUNK_NAME.value
        ]
        
    async def create_chunk(self,chunk: DataChunk):
        # model_dump by alias so `id` is stored as Mongo `_id`, and omit it when unset
        #exclude_none=True to omit None values from the dictionary
        result = await self.collection.insert_one(chunk.model_dump(by_alias=True, exclude_none=True))
        chunk.id = result.inserted_id
        return chunk 
    
    async def get_chunk(self,chunk_id:str):
        result = await self.collection.find_one(
            {"_id":ObjectId(chunk_id)})
        if result is None:
            return None
        return DataChunk(**result)
    
    async def insert_chunks(self,chunks:list,batch_size:int=100):
        if batch_size <= 0 :
            raise ValueError("Batch size must be greater than 0")
        
        inserted_count = 0
        
        for i in range(0,len(chunks),batch_size):
            batch = chunks[i:i+batch_size]
            
            #create a list of InsertOne operations for the batch
            operations = [
                InsertOne(chunk.model_dump(by_alias=True, exclude_none=True)) 
                for chunk in batch 
            ]
            try:
                
                result = await self.collection.bulk_write(operations)
                inserted_count += result.inserted_count
            except BulkWriteError as WriteError:
                #if details is empty use empty dictionary to can use get method without error
                details = WriteError.details or {}
                #get the number of inserted documents from the details
                inserted_count += details.get("nInserted",0)
                return {
                    "success": False,
                    "inserted_count": inserted_count,
                    "error": details.get("writeErrors", [])
                }
        return {
        "success": True,
        "inserted_count": inserted_count,
        "error": None
    }