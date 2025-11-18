from langchain_ollama.llms import OllamaLLM
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk
from typing import Any, AsyncIterator, Iterator, List, Optional
import os
import logging

logger = logging.getLogger(__name__)
ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

class BaseLLM:
    def stream(self, prompt: str):
        raise NotImplementedError("stream() must be implemented by subclasses.")

class LangChainWrapper(LLM):
    adapter: BaseLLM
    streaming: bool = True
    
    @property
    def _llm_type(self) -> str:
        return "custom_adapter"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> str:
        """Non-streaming version"""
        return "".join(self.adapter.stream(prompt))

    def _stream(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Iterator[GenerationChunk]:
        """Streaming implementation"""
        for token in self.adapter.stream(prompt):
            yield GenerationChunk(text=token)

    def get_num_tokens(self, text: str) -> int:
        return len(text.split())

    async def _acall(self, prompt: str, **kwargs: Any) -> str:
        return self._call(prompt, **kwargs)

    async def _astream(
        self,
        prompt: str,
        **kwargs: Any,
    ) -> AsyncIterator[GenerationChunk]:
        for token in self.adapter.stream(prompt):
            yield GenerationChunk(text=token)

class OllamaAdapter(BaseLLM):
    def __init__(self, model_id:str="gemma3:1b", num_ctx:int=32768, num_predict:int=4096, temperature:float=0.5):
        self.llm = OllamaLLM(
            model=model_id,
            num_ctx=num_ctx,
            num_predict=num_predict,
            temperature=temperature,
            base_url=ollama_base_url,
        )
    def stream(self, prompt: str):
        return self.llm.stream(prompt)

def get_llm(config):
    provider = config["llm"]["provider"].lower()
    if provider == "ollama":
        return OllamaAdapter(config["llm"])
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
def get_llm_with_memory(config):
    base_llm = get_llm(config)
    return LangChainWrapper(adapter=base_llm)

class BaseEmbeddings:
    def embed_query(self, text: str):
        raise NotImplementedError("embed_query() must be implemented.")
    def prepare_query(self, query: str):
        return query

class NomicEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, model_id):
        self.embeddings = OllamaEmbeddings(model=model_id, base_url=ollama_base_url)
        self.query_prefix = ""
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    def prepare_query(self, query: str):
        return self.query_prefix + query