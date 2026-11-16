from enum import Enum

class LLMType(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    
class OpenaiEnums(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class CohereEnums(Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
    DOCUMENT = "search_document"
    QUERY = "search_query"

class DocumentTypeEnum(Enum):
    DOCUMENT = "document"
    QUERY = "query"
    
    