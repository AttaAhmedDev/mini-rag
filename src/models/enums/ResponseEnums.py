from enum import Enum

class ResponseEnums(Enum):
    FILE_SIZE_TOO_LARGE = "File size is too large"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_UPLOAD_SUCCESS = "File uploaded successfully"
    FILE_UPLOAD_FAILED = "File upload failed"
    PROCESS_FILE_SUCCESS = "File processed successfully"
    PROCESS_FILE_FAILED = "File processing failed"
    DELETE_CHUNKS_SUCCESS = "Chunks deleted successfully"
    DELETE_CHUNKS_FAILED = "Chunks deletion failed"
    FILE_NOT_FOUND = "File not found"