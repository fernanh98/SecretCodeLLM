from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain_ollama import ChatOllama
from src.schemas import LLMMessage, ToolCall


class LLMModel(ABC):

    def __init__(
            self,
            model_name: str,
            temperature: float = 0.1,
            tools: List = [],
            seed: int | None = None
        ):
        self.model_name: str = model_name
        self.temperature: float = temperature
        self.tools: List = tools
        self.seed: int | None = seed
        self._model : Any = self.build_model()

    @abstractmethod
    def build_model(self) -> Any:
        """
        This method is used to return an instance of the LLM you will use.
        """
        pass
    
    @abstractmethod
    def chat(
            self,
            messages: List[Dict[str, str]]
        ) -> LLMMessage:
        """
        This method should is used to get a response from the LLM.
        The return type must be an LLMMessage object.

        Args:
            messages (List[Dict[str, str]]): List of messages to pass to the LLM.
        Return:
            (LLMMessage)
        """
        pass


class ChatOllamaLLMModel(LLMModel):

    def __init__(
            self,
            model_name: str,
            temperature: float = 0.1,
            tools: List = [],
            seed: int | None = None
        ):
        super().__init__(model_name, temperature, tools, seed)
        
    def build_model(self) -> Any:
        """
        This method should be changed to create an instance of the LLM you will use.
        For the moment, it makes use of 'langchain_ollama.ChatOllama' class.
        """
        return ChatOllama(
            model=self.model_name, 
            temperature=self.temperature
        ).bind_tools(self.tools)
    
    def chat(
            self,
            messages: List[Dict[str, str]]
        ) -> LLMMessage:
        """
        This method should be changed to get a response from the LLM you use.
        The return type must be an LLMMessage object.
        """

        # The LLM call should be alligned with the provider used
        # In this case, we use .invoke() because it corresponds to ChatOllama class
        llm_response = self._model.invoke(messages)

        ai_msg = LLMMessage(
            model_name = self.model_name,
            content = llm_response.content if len(llm_response.content) > 0 else None,
            tool_call = ToolCall(
                tool_name = llm_response.tool_calls[0]["name"],
                args = llm_response.tool_calls[0]["args"]
            ) if len(llm_response.tool_calls) > 0 else None
        )
        return ai_msg
    

class HumanLLMModel(LLMModel):
    def __init__(
            self,
            model_name: str,
            temperature: float = 0.1,
            tools: List = [],
            seed: int | None = None
    ):
        super().__init__(model_name, temperature, tools, seed)
    
    def build_model(self) -> Any:
        return None
    
    def chat(
            self,
            messages: List[Dict[str, str]]
        ) -> LLMMessage:
        print("----------Mensaje al LLM:-----------\n")
        for msg in messages:
            print("Role: ", msg["role"], "\n", "Content:\n", msg["content"], "\n")

        llm_response = input().split(",")
        if llm_response[0] == "0": # Captain
            tool_name = "indicate_secret_code"
            args = {
                "word": llm_response[2], 
                "number": llm_response[1], 
                "justification": "", 
                "words_related": [""]
            }
        else: # Guesser
            tool_name = "choose_words"
            args = {
                "words": llm_response[1:], 
                "justification": ""
            }

        ai_msg = LLMMessage(
            model_name = self.model_name,
            content = "",
            tool_call = ToolCall(
                tool_name = tool_name,
                args = args
            )
        )
        return ai_msg