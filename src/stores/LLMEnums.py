from enum import Enum

class LLMType(Enum):
    OPENAI = "OPENAI"
    COHERE = "COHERE"
    ANTHROPIC = "ANTHROPIC"
    
class LLMRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
