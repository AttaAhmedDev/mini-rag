from fastapi import FastAPI,APIRouter ,Depends,UploadFile ,status
from fastapi.responses import JSONResponse
from helper.config import get_settings,Settings
from controllers import DataController,ProjectController
import os , aiofiles ,logging
from models import ResponseEnums
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1","data"]
)

logger = logging.getLogger('uvicorn.error')

@data_router.post("/upload/{project_id}")
async def upload_data(project_id:str,file:UploadFile,settings:Settings=Depends(get_settings)):
    
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
                "file id":file_id
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