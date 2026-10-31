from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnums import DataBaseEnums

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection =self.db_client[
            DataBaseEnums.Collection_PROJECT_NAME.value
        ]
    #this method is used to initialize the collection and create the indexes
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnums.Collection_PROJECT_NAME.value not in all_collections:
            self.collection =self.db_client[DataBaseEnums.Collection_PROJECT_NAME.value]
            indexes = Project.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    unique=index["unique"],
                    name=index["name"],
                )
    #this method is used to create an instance of the ProjectModel class
    @classmethod
    async def create_instance(cls,db_client:object):
        instance = cls(db_client=db_client)
        await instance.init_collection()
        return instance
        
    async def create_project(self,project:Project):
        # Dump by alias so `id` is stored as Mongo `_id`, and omit it when unset
        # so MongoDB generates the ObjectId instead of saving `id: null`.
        project_dict = project.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(project_dict)
        project.id = result.inserted_id
        return project
    
    async def get_or_create_project(self,project_id:str):
        get_project = await self.collection.find_one({"project_id":project_id})
        
        if get_project is None :
            new_project = Project(project_id=project_id)
            new_project = await self.create_project(project=new_project)
            return new_project
        # if project exists, return the project as a Project object not a dictionary``
        return Project(**get_project)
    
    async def get_all_projects(self,page:int =1,page_size:int =10):
        total_documents = await self.collection.count_documents({})
        #for the last page, we need to add 1 to the total pages to avoid odd number of documents
        total_pages = (total_documents + page_size - 1) // page_size
        
        cursor = (self.collection.find()
                    .skip((page-1) * page_size)
                    .limit(page_size)
                    )
        #to_list is a method that converts the cursor to a list of documents (deal with async opearation in motor driver)
        documents = await cursor.to_list(length=page_size)
        projects = [Project(**document) for document in documents]
        return projects,total_pages
    
        # another way for that code is: projects = []
        # async for document in cursor:
        #     projects.append(Project(**document))
        # return projects,total_pages