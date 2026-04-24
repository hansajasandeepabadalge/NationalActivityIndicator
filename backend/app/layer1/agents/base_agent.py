"""
Base Agent Class

Abstract base class for all AI agents in the system.
Provides common functionality for LLM interaction, logging, and error handling.
"""

import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Dict, Any, List

from app.agents.config import get_agent_config, TaskComplexity
from app.agents.llm_manager import get_llm_manager, LLMProvider
from app.agents.tools.database_tools import log_agent_decision

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Abstract base class for AI agents.
    
    All agents inherit from this class and implement the execute() method.
    Provides common functionality for:
    - LLM access with automatic fallback
    - Decision logging
    - Error handling
    - Performance tracking
    """
    
    # Class-level configuration
    agent_name: str = "base_agent"
    agent_description: str = "Base agent class"
    task_complexity: TaskComplexity = TaskComplexity.MEDIUM
    
    def __init__(self):
        """Initialize the agent with configuration and LLM."""
        self.config = get_agent_config()
        self.llm_manager = get_llm_manager()
        self._tools: List[Any] = []
        
        logger.info(f"Initialized {self.agent_name} agent")
    
    @property
    def llm(self):
        """Get the appropriate LLM for this agent."""
        return self.llm_manager.get_llm_for_agent(self.agent_name)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Returns:
            System prompt string that defines agent behavior
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """
        Get the tools available to this agent.
        
        Returns:
            List of LangChain tools
        """
        pass
    
    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the agent's main logic.
        
        Args:
            input_data: Input data for the agent to process
            
        Returns:
            Dict with agent's decision/output
        """
        pass
    
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the agent with full logging and error handling.
        
        This is the main entry point that wraps execute() with:
        - Timing
        - Logging
        - Error handling
        
        Args:
            input_data: Input data for the agent
            
        Returns:
            Dict with results and metadata
        """
        start_time = time.time()
        decision_type = input_data.get("decision_type", "general")
        
        try:
            logger.info(f"{self.agent_name} starting execution for: {decision_type}")
            
            # Execute agent logic
            result = await self.execute(input_data)
            
            # Calculate latency
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Log successful decision
            if self.config.log_decisions:
                log_agent_decision(
                    agent_name=self.agent_name,
                    decision_type=decision_type,
                    input_data=input_data,
                    output_decision=result,
                    reasoning=result.get("reasoning", ""),
                    llm_provider="groq",
                    llm_model=self.config.primary_model,
                    latency_ms=latency_ms,
                    success=True
                )
            
            # Track LLM usage
            self.llm_manager.track_usage(
                provider=LLMProvider.GROQ,
                tokens=result.get("tokens_used", 0)
            )
            
            logger.info(f"{self.agent_name} completed in {latency_ms}ms")
            
            return {
                "success": True,
                "agent": self.agent_name,
                "result": result,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            error_message = str(e)
            
            logger.error(f"{self.agent_name} failed: {error_message}")
            
            # Log failed decision
            if self.config.log_decisions:
                log_agent_decision(
                    agent_name=self.agent_name,
                    decision_type=decision_type,
                    input_data=input_data,
                    output_decision={},
                    reasoning="",
                    llm_provider="groq",
                    llm_model=self.config.primary_model,
                    latency_ms=latency_ms,
                    success=False,
                    error_message=error_message
                )
            
            return {
                "success": False,
                "agent": self.agent_name,
                "error": error_message,
                "latency_ms": latency_ms,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_agent_executor(self):
        """
        Create a LangChain agent executor.
        
        Returns:
            AgentExecutor configured with tools and prompt
        """
        try:
            from langchain.agents import AgentExecutor, create_react_agent
            from langchain.prompts import PromptTemplate
            
            tools = self.get_tools()
            prompt = PromptTemplate.from_template(
                self.get_system_prompt() + 
                "\n\n{agent_scratchpad}"
            )
            
            agent = create_react_agent(
                llm=self.llm,
                tools=tools,
                prompt=prompt
            )
            
            return AgentExecutor(
                agent=agent,
                tools=tools,
                verbose=self.config.log_level == "DEBUG",
                handle_parsing_errors=True,
                max_iterations=5
            )
        except Exception as e:
            logger.error(f"Failed to create agent executor: {e}")
            raise
    
    async def invoke_llm(self, prompt: str) -> str:
        """
        Invoke the LLM directly with a prompt.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response as string
        """
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise
    
    def invoke_llm_sync(self, prompt: str) -> str:
        """
        Invoke the LLM synchronously.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            LLM response as string
        """
        try:
            response = self.llm.invoke(prompt)
            return response.content if hasattr(response, 'content') else str(response)
        except Exception as e:
            logger.error(f"LLM invocation failed: {e}")
            raise
