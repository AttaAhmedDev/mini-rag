from fastapi import APIRouter,Request,FastAPI,status
from fastapi.responses import JSONResponse
import logging
from routes.schemes import PushRequest,SearchRequest
from models.ProjectModel import ProjectModel
from controllers import NLPController
from models.enums.ResponseEnums import ResponseEnums
from models.ChunkModel import ChunkModel

logger = logging.getLogger("uvicorn.error")

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1","nlp"]
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request:Request,project_id:str,push_request:PushRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client = request.app.database_name
    )

    chunk_model = await ChunkModel.create_instance(
        db_client = request.app.database_name
    )
    
    project = await project_model.get_or_create_project(project_id=project_id)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_provider,
        embeddings_client=request.app.embedding_provider,
        template_parser=request.app.template_parser
    )
    
    has_more_records = True
    page_no = 1
    inserted_items_count = 0
    while has_more_records:
        chunks = await chunk_model.get_chunks_by_project_id(project_id=project.id,page_no=page_no)
        
        if len(chunks):
            page_no +=1
        
        if not chunks:
            if inserted_items_count == 0:
                return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,content={"message":ResponseEnums.NO_CHUNKS_TO_INDEX.value})
            has_more_records = False
            break
        
        is_success = nlp_controller.index_into_vectordb(project=project,chunks=chunks,do_reset=push_request.do_reset and inserted_items_count == 0)
        if not is_success:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,content={"message":ResponseEnums.FAILED_TO_INDEX_INTO_VECTORDB.value})
        inserted_items_count += len(chunks)
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message":ResponseEnums.INDEX_PROJECT_SUCCESS.value,
                "inserted_items_count":inserted_items_count
                })
    
@nlp_router.get("/index/status/{project_id}")
async def get_project_index_status(request:Request,project_id:str):
    
    
    project_model = await ProjectModel.create_instance(
        db_client = request.app.database_name
    )
    project = await project_model.get_or_create_project(project_id=project_id)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_provider,
        embeddings_client=request.app.embedding_provider,
        template_parser=request.app.template_parser
    )
    
    collection_info = nlp_controller.get_vectordb_collection_info(project=project)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message":ResponseEnums.PROJECT_INDEX_STATUS_SUCCESS.value,
                "collection_info":collection_info
                })
    
@nlp_router.post("/index/search/{project_id}")
async def search_index(request:Request,project_id:str,search_request:SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client = request.app.database_name
    )
    
    project = await project_model.get_or_create_project(project_id=project_id)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_provider,
        embeddings_client=request.app.embedding_provider,
        template_parser=request.app.template_parser
    )
    
    search_results = nlp_controller.search_vectordb_collection(project=project,query=search_request.query,limit=search_request.limit)
    
    if not search_results:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":ResponseEnums.FAILED_TO_SEARCH_INDEX.value})
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":ResponseEnums.SEARCH_INDEX_SUCCESS.value,
            "results":search_results})
    
@nlp_router.post("/index/answer/{project_id}")
async def search_index(request:Request,project_id:str,search_request:SearchRequest):
    project_model = await ProjectModel.create_instance(
        db_client = request.app.database_name
    )
    
    project = await project_model.get_or_create_project(project_id=project_id)
    
    nlp_controller = NLPController(
        vectordb_client=request.app.vectordb_client,
        generation_client=request.app.generation_provider,
        embeddings_client=request.app.embedding_provider,
        template_parser=request.app.template_parser
    )
    
    answer,full_prompt,chat_history = nlp_controller.answer_rag_question(project=project,query=search_request.query,limit=search_request.limit)
    
    if not answer:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,content={"message":ResponseEnums.FAILED_TO_ANSWER_RAG_QUESTION.value})
    
    return JSONResponse(status_code=status.HTTP_200_OK,content={"message":ResponseEnums.ANSWER_RAG_QUESTION_SUCCESS.value,
            "answer":answer,
            "full_prompt":full_prompt,
            "chat_history":chat_history})