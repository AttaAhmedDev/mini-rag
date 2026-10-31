from fastapi import FastAPI,APIRouter ,Depends,UploadFile ,status,Request
from fastapi.responses import JSONResponse
from helper.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
import os , aiofiles ,logging
from models import ResponseEnums
from .schemes import ProcessRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import DataChunk
from models.ChunkModel import ChunkModel

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

logger = logging.getLogger('uvicorn.error')

@data_router.post("/upload/{project_id}")
async def upload_data(request:Request,project_id:str,file:UploadFile,settings:Settings=Depends(get_settings)):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database_name)
    project = await project_model.get_or_create_project(project_id=project_id)
    
    data_controller = DataController()
    
    is_valid = data_controller.validate_file(file)
    
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.FILE_UPLOAD_FAILED.value
            }
        )
        
    project_dir_path = ProjectController().get_path_project(project_id=project_id)
    
    file_path , file_id = data_controller.generate_unique_file_path(file.filename,project_id)
    
    try:
        async with aiofiles.open(file_path,mode="wb") as f:
            while content := await file.read(settings.FILE_CHUNK_SIZE):
                await f.write(content)
                
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message":ResponseEnums.FILE_UPLOAD_SUCCESS.value,
                "file id":file_id,
                "project_id":str(project.id) #convert the ObjectId to a string
            }
        )
    except Exception as e:
        #remove the file if the upload fails then store logger error
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.FILE_UPLOAD_FAILED.value
            }
        )
        
@data_router.post("/process/{project_id}")
async def process_data(request:Request,project_id:str,data:ProcessRequest):
    
    file=data.file_id
    chunk_size=data.chunk_size
    overlap_size=data.overlap_size
    do_reset=data.do_reset
    
    project_model = await ProjectModel.create_instance(db_client=request.app.database_name)
    
    project = await project_model.get_or_create_project(project_id=project_id)

    process_controller = ProcessController(project_id=project_id)
    file_content= process_controller.get_file_documents(file_id=file)
    
    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "message":ResponseEnums.FILE_NOT_FOUND.value
                }
        )
    
    file_chunks= process_controller.get_file_chunks(file_content=file_content,file_id=file,chunk_size=chunk_size,overlap_size=overlap_size)
    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.PROCESS_FILE_FAILED.value
                }
        )
    
    chunk_records = [
        DataChunk(
            chunk_text=chunk.page_content,
            chunk_metadata=chunk.metadata,
            chunk_order=index+1,
            chunk_project_id=project.id
        )
        for index,chunk in enumerate(file_chunks)
    ]
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.database_name)
    # put delete here as we want first prepare data that chunking process then insert the new data , do for prevent lose old data 
    if do_reset:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
    
    result = await chunk_model.insert_chunks(chunks=chunk_records)
    # JSONResponse is a response object that returns a JSON response,HTTPException is a response object that returns a HTTP exception, i used JSONResponse for control the response status code and content
    if not result["success"]:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.PROCESS_FILE_FAILED.value,
                "error":result["error"],
                "inserted_count":result["inserted_count"]
            })
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":ResponseEnums.PROCESS_FILE_SUCCESS.value,
            "inserted_count":result["inserted_count"]
        }
    )