from fastapi import FastAPI,APIRouter ,Depends,UploadFile ,status,Request
from fastapi.responses import JSONResponse
from helper.config import get_settings,Settings
from controllers import DataController,ProjectController,ProcessController
import os , aiofiles ,logging
from models import ResponseEnums,AssetType
from .schemes import ProcessRequest
from models.ProjectModel import ProjectModel
from models.db_schemes import DataChunk,Asset
from models.AssetModel import AssetModel
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
                
    except Exception as e:
        #remove the file if the upload fails then store logger error
        logger.error(f"Error uploading file: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.FILE_UPLOAD_FAILED.value
            }
        )
    
    asset_model = await AssetModel.create_instance(db_client=request.app.database_name)
    
    new_asset = await asset_model.create_asset(
        Asset(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value,
            asset_name=file_id,
            asset_size=os.path.getsize(file_path)
        ))
    
    return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message":ResponseEnums.FILE_UPLOAD_SUCCESS.value,
                "file_id": str(new_asset.id),
            }
    )
@data_router.post("/process/{project_id}")
async def process_data(request:Request,project_id:str,data:ProcessRequest):
    
    file_id=data.file_id
    chunk_size=data.chunk_size
    overlap_size=data.overlap_size
    do_reset=data.do_reset
    
    #get project 
    project_model = await ProjectModel.create_instance(db_client=request.app.database_name)
    
    project = await project_model.get_or_create_project(project_id=project_id)
    asset_model = await AssetModel.create_instance(db_client=request.app.database_name)

    project_files_ids ={}
    if file_id:
        #check that file_id belongs to this project
        asset = await asset_model.check_asset_belongs_to_project(asset_name=file_id,project_id=project.id)
        if asset is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "message":ResponseEnums.FILE_NOT_FOUND.value
                }
            )
        project_files_ids[asset.id] = asset.asset_name
    else:
        projects_files = await asset_model.get_all_project_assets(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value
        )
        
        if projects_files is None or len(projects_files) == 0:
            return JSONResponse(
                status_code = status.HTTP_404_NOT_FOUND,
                content={
                    "message":ResponseEnums.NO_FILES_FOUND.value
                }
            )
        
        project_files_ids = {
            record.id: record.asset_name
            for record in projects_files
        }
        

    process_controller = ProcessController(project_id=project_id)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.database_name)
    
    total_files_processed = 0
    new_inserted_chunks = []
    for asset_id,file_id in project_files_ids.items():
        file_content = process_controller.get_file_documents(file_id=file_id)
        #if file not found, skip the file
        if file_content is None :
            logger.error(f"File {file_id} not found")
            continue
        
        file_chunks = process_controller.get_file_chunks(file_content=file_content,file_id=file_id,chunk_size=chunk_size,overlap_size=overlap_size)
        
        if file_chunks is None or len(file_chunks) == 0:
            logger.error(f"No chunks found for file {file_id}")
            continue
    
        chunk_records = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=index+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for index,chunk in enumerate(file_chunks)
        ]
    
        new_inserted_chunks.extend(chunk_records)
        total_files_processed += 1  
    
    if total_files_processed == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message": ResponseEnums.NO_FILES_TO_PROCESS.value
            }
        )
        
    if do_reset:
        _ = await chunk_model.delete_chunks_by_project_id(project_id=project.id)
        
    result = await chunk_model.insert_chunks(chunks=new_inserted_chunks)
    if not result["success"]:
        logger.error(f"Error inserting chunks: {result['error']}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "message":ResponseEnums.PROCESS_FILE_FAILED.value
            }
        )
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message":ResponseEnums.PROCESS_FILE_SUCCESS.value,
            "inserted_chunks":result["inserted_count"],
            "files_processed":total_files_processed
        }
    )