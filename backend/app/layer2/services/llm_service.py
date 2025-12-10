import logging
from typing import Optional, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from app.core.config import settings
from app.core.llm_config import llm_settings

logger = logging.getLogger(__name__)

class LLMService:
    """
    Singleton service to manage LLM interactions.
    Currently maps to Groq (Llama 3.1) via LangChain.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.llm = None
        if llm_settings.GROQ_API_KEY:
            try:
                self.llm = ChatGroq(
                    temperature=llm_settings.LLM_TEMPERATURE,
                    model_name=llm_settings.LLM_MODEL,
                    groq_api_key=llm_settings.GROQ_API_KEY
                )
                logger.info(f"LLM Service initialized with provider: {llm_settings.LLM_PROVIDER}, model: {llm_settings.LLM_MODEL}")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
        else:
            logger.warning("GROQ_API_KEY not set. LLM features will be disabled or fall back to basic logic.")

    def is_available(self) -> bool:
        """Check if LLM is properly initialized and ready."""
        return self.llm is not None

    async def generate_response(self, system_prompt: str, user_content: str) -> Optional[str]:
        """
        Generate a simple text response from the LLM.
        """
        if not self.is_available():
            return None
            
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_content)
            ]
            response = await self.llm.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return None
