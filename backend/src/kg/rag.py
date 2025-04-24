import time, sys

from langchain_ollama.llms import OllamaLLM
from langchain.llms import OpenAI
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain.embeddings import OpenAIEmbeddings
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jVector

from langchain_core.language_models.llms import LLM
from langchain_core.outputs import GenerationChunk, LLMResult
from typing import Any, AsyncIterator, Iterator, List, Optional

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

    # Required abstract method implementations
    def get_num_tokens(self, text: str) -> int:
        return len(text.split())

    # Optional async implementations
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
    def __init__(self, llm_config):
        self.llm = OllamaLLM(
            model=llm_config["model_id"],
            num_ctx=llm_config.get("num_ctx", 32768),
            num_predict=llm_config.get("num_predict", 4096),
            temperature=llm_config.get("temperature", 0.5)
        )
    def stream(self, prompt: str):
        return self.llm.stream(prompt)

class OpenAIAdapter(BaseLLM):
    def __init__(self, llm_config):
        self.llm = OpenAI(
            model=llm_config["model_id"],
            temperature=llm_config.get("temperature", 0.5),
            openai_api_key=llm_config.get("api_key")
        )
    def stream(self, prompt: str):
        response = self.llm(prompt)
        yield response

class HuggingFaceAdapter(BaseLLM):
    def __init__(self, llm_config):
        max_seq_len = llm_config.get("max_seq_len", 4096)
        self.max_seq_len = max_seq_len
        self.temperature = llm_config.get("temperature", 0.5)
        model_config = AutoConfig.from_pretrained(llm_config["model_id"], trust_remote_code=True)
        model_config.max_seq_len = max_seq_len
        self.model = AutoModelForCausalLM.from_pretrained(
            llm_config["model_id"],
            config=model_config,
            trust_remote_code=True,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(llm_config["model_id"], trust_remote_code=True)
        self.tokenizer.model_max_length = max_seq_len
   
    def stream(self, prompt: str):

        self.model.eval()
        input_ids = self.tokenizer(prompt, return_tensors="pt").input_ids.to(self.model.device)
        generated_ids = input_ids

        with torch.no_grad():
            outputs = self.model(input_ids, use_cache=True)
        past = outputs.past_key_values

        while True:
            last_token_id = generated_ids[:, -1].unsqueeze(-1)
            with torch.no_grad():
                outputs = self.model(input_ids=last_token_id, past_key_values=past, use_cache=True)
            logits = outputs.logits
            past = outputs.past_key_values

            next_token_logits = logits[:, -1, :] / self.temperature
            probs = torch.softmax(next_token_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)

            generated_ids = torch.cat([generated_ids, next_token], dim=-1)
            token_id = next_token.item()
            decoded = self.tokenizer.decode(next_token.squeeze(), skip_special_tokens=True)
            yield decoded

            if token_id == self.tokenizer.eos_token_id or generated_ids.shape[-1] >= self.max_seq_len:
                break   
    
def get_llm(config):
    provider = config["llm"]["provider"].lower()
    if provider == "ollama":
        return OllamaAdapter(config["llm"])
    elif provider == "openai":
        return OpenAIAdapter(config["llm"])
    elif provider == "huggingface":
        return HuggingFaceAdapter(config["llm"])
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    
def get_llm_with_memory(config):
    base_llm = get_llm(config)
    return LangChainWrapper(adapter=base_llm)

class BaseEmbeddings:
    def embed_query(self, text: str):
        raise NotImplementedError("embed_query() must be implemented.")
    def prepare_query(self, query: str):
        # Default is no extra processing
        return query

class NomicEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, emb_config):
        self.embeddings = OllamaEmbeddings(model=emb_config["model_id"])
        self.query_prefix = emb_config.get("query_prefix", "")
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    def prepare_query(self, query: str):
        return self.query_prefix + query

class OpenAIEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, emb_config):
        self.embeddings = OpenAIEmbeddings(model=emb_config["model_id"],
                                           openai_api_key=emb_config.get("api_key"))
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    
    def prepare_query(self, query: str):
        return query

class HuggingFaceEmbeddingAdapter(BaseEmbeddings):
    def __init__(self, emb_config):
        self.embeddings = HuggingFaceEmbeddings(
            model_name=emb_config["model_id"],
            model_kwargs={'trust_remote_code': True}
        )
    def embed_query(self, text: str):
        return self.embeddings.embed_query(text)
    def prepare_query(self, query: str):
        # No extra processing needed by default.
        return query

def get_embeddings(config):
    provider = config["embedding"]["provider"].lower()
    if provider == "nomic":
        return NomicEmbeddingAdapter(config["embedding"])
    elif provider == "openai":
        return OpenAIEmbeddingAdapter(config["embedding"])
    elif provider == "huggingface":
        return HuggingFaceEmbeddingAdapter(config["embedding"])
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")