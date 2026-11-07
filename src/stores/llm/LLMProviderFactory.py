from .providers import OpenaiProvider, CohereProvider
from .LLMEnums import LLMType
from helper import Settings

class LLMProviderFactory:
    def __init__(self, config:Settings):
        self.config = config
        
    def create_provider(self,provider:str):
        if provider == LLMType.OPENAI.value:
            return OpenaiProvider(
                api_key=self.config.OPENAI_API_KEY,
                api_url=self.config.OPENAI_API_URL,
                default_input_max=self.config.DEFAULT_INPUT_MAX,
                default_generation_max=self.config.DEFAULT_GENERATION_MAX,
                default_temperature=self.config.DEFAULT_TEMPERATURE,
            )
        
        if provider == LLMType.COHERE.value:
            return CohereProvider(
                api_key=self.config.COHERE_API_KEY,
                default_input_max=self.config.DEFAULT_INPUT_MAX,
                default_generation_max=self.config.DEFAULT_GENERATION_MAX,
                default_temperature=self.config.DEFAULT_TEMPERATURE,
            )
        
        return None