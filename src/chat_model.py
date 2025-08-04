"""Chat Model Module"""

import os
import logging

import requests
from langchain.chat_models import init_chat_model
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import RateLimitError
from starlette.exceptions import HTTPException

from src.constants import (
    DEFAULT_SYSTEM_PROMPT,
    KNOWLEDGE_BASE_PATH,
    MODEL_FAILURE_MESSAGE,
    MODEL_NOT_DEFINED,
    PROMPT_PATH,
    RATE_LIMIT_MESSAGE,
)
from src.env import (
    LOCAL_LLM_API_KEY,
    LOCAL_LLM_BASE_URL,
    LOCAL_MODEL_NAME,
    USE_LOCAL_MODEL,
)
from src.schemas import LLMResponse

# Initialize logger
logger = logging.getLogger(__name__)


class ChatModel:
    """Class to handle chat model interactions, including loading knowledge base,
    creating retriever tools, and generating responses based on user queries."""

    def __init__(
        self,
        use_local_model=USE_LOCAL_MODEL,
        local_model_name=LOCAL_MODEL_NAME,
        local_llm_base_url=LOCAL_LLM_BASE_URL,
        local_llm_api_key=LOCAL_LLM_API_KEY,
        prompt_path=PROMPT_PATH,
        knowledge_base_path=KNOWLEDGE_BASE_PATH,
        response_model=None,
        retriever_tool=None,
        logger_instance=None,
    ):
        self.use_local_model = use_local_model
        self.local_model_name = local_model_name
        self.local_llm_base_url = local_llm_base_url
        self.local_llm_api_key = local_llm_api_key
        self.prompt_path = prompt_path
        self.knowledge_base_path = knowledge_base_path
        self.logger = logger_instance or logging.getLogger(__name__)
        self.response_model = response_model
        self.retriever_tool = retriever_tool
        self.system_prompt = self._load_system_prompt()

        if self.response_model is None:
            self.response_model = self._init_response_model()
        if self.retriever_tool is None:
            self.retriever_tool = self._init_retriever_tool()

    def _load_system_prompt(self) -> str:
        """
        Loads and processes the system prompt from the prompt.md file.

        Returns:
            str: The cleaned system prompt ready to be used with the model.
        """
        try:
            self.logger.info("Loading system prompt from file.")
            with open(self.prompt_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            self.logger.warning("Prompt file not found. Using default system prompt.")
            return DEFAULT_SYSTEM_PROMPT
        except Exception as e:
            self.logger.error("Error loading system prompt: %s", e)
            return DEFAULT_SYSTEM_PROMPT

    def _get_knowledge_base_files(self) -> list[str]:
        """
        Retrieves a list of file paths for all Markdown (.md) files in the knowledge
        base directory defined by KNOWLEDGE_BASE_PATH.

        Returns:
            list[str]: A list of file paths for all Markdown files in the specified directory.
        """
        markdown_paths = []
        for filename in os.listdir(self.knowledge_base_path):
            if filename.endswith(".md"):
                markdown_paths.append(os.path.join(self.knowledge_base_path, filename))
        return markdown_paths

    def _get_documents(self, markdown_path: list[str]) -> list[TextLoader]:
        """
        Loads and flattens documents from a list of markdown file paths.

        Args:
            markdown_path (list[str]): A list of file paths to markdown files.

        Returns:
            list[TextLoader]: A flattened list of TextLoader objects containing the loaded content
            from the provided markdown files.
        """
        documents = [
            TextLoader(markdown_file, encoding="utf-8").load()
            for markdown_file in markdown_path
        ]
        return [item for sublist in documents for item in sublist]

    def _get_splitted_docs(self, document_list):
        """
        Splits a list of documents into smaller chunks using a RecursiveCharacterTextSplitter.

        Args:
            document_list (list): A list of documents to be split. Each document should be a string
            or an object compatible with the text splitter.

        Returns:
            list: A list of smaller document chunks obtained by splitting the input documents.
        """
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=100, chunk_overlap=50
        )
        docs_splits = text_splitter.split_documents(document_list)
        return docs_splits

    def _create_memory_db(self, docs_splits):
        """
        Creates an in-memory vector store from a list of document splits.

        This function uses the InMemoryVectorStore to store the provided document
        splits and applies OpenAIEmbeddings to generate embeddings for the documents.

        Args:
            docs_splits (list): A list of document splits to be stored in the vector store.

        Returns:
            InMemoryVectorStore: An in-memory vector store containing the embedded documents.
        """
        if self.use_local_model:
            embedding = HuggingFaceEmbeddings(
                model_name="paraphrase-multilingual-MiniLM-L12-v2",  # Bueno para español
                model_kwargs={"device": "cpu"},  # Cambiar a 'cuda' si tienes GPU
                encode_kwargs={"normalize_embeddings": True},
            )
        else:
            embedding = OpenAIEmbeddings()

        vectorstore = InMemoryVectorStore.from_documents(
            documents=docs_splits, embedding=embedding
        )
        return vectorstore

    def _create_retriever(
        self, vectorstore: InMemoryVectorStore, name: str, description: str
    ):
        """
        Creates a retriever tool from the given vector store.

        Args:
            vectorstore (InMemoryVectorStore): The in-memory vector store to be used for retrieval.
            name (str): The name of the retriever tool.
            description (str): A brief description of the retriever tool.

        Returns:
            Tool: A retriever tool created from the provided vector store.
        """
        retriever = vectorstore.as_retriever()
        return create_retriever_tool(retriever, name, description)

    def _init_response_model(self):
        model_temperature = 0.3
        if self.use_local_model:
            # Usar LM Studio local
            return init_chat_model(
                f"openai:{self.local_model_name}",
                temperature=model_temperature,
                api_base=self.local_llm_base_url,
                api_key=self.local_llm_api_key,
            )
        else:
            return init_chat_model("openai:gpt-4.1", temperature=model_temperature)

    def _init_retriever_tool(self):
        # 1. cargar el contenido
        markdown_files = self._get_knowledge_base_files()
        document_list = self._get_documents(markdown_files)
        # 2. separar el texto y codificar con el embedding (tiktoken_encoder)
        docs_splits = self._get_splitted_docs(document_list)
        try:
            vectorstore = self._create_memory_db(docs_splits)
            return self._create_retriever(
                vectorstore,
                "retrieve_ParceroGo",
                "Buscador de información parceroGo",
            )
        except RateLimitError as e:
            self.logger.error("Error al crear la base de datos vectorstore: %s", e)
            return None

    def _generate_response(self, message: str):
        # Obtener contexto relevante de la base de conocimiento
        if not self.retriever_tool:
            self.logger.error("Retriever tool is not initialized.")
            raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
        docs = self.retriever_tool.invoke({"query": message})
        if docs:
            context_text = "\n".join(
                [doc.page_content if hasattr(doc, "page_content") else str(doc) for doc in docs]
            )
        else:
            context_text = "No hay información específica disponible."
        full_prompt = self.system_prompt.format(
            context_section=context_text, user_message=message
        )
        if self.use_local_model:
            return self._call_local_model(full_prompt)
        else:
            return self.response_model.invoke(full_prompt)

    def _call_local_model(self, prompt: str):
        url = f"{self.local_llm_base_url}/chat/completions"
        headers = {"Content-Type": "application/json"}
        data = {
            "model": self.local_model_name,
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": -1,
            "stream": False,
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=600000)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise HTTPException(
                status_code=500, detail=f"Error connecting to local model: {str(e)}"
            ) from e

    def ask_to_model(self, message: str):
        """Ask the chat model a question and return the response."""
        if not self.retriever_tool or not self.response_model:
            self.logger.error("Error initializing chat model or retriever tool.")
            raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
        try:
            response = self._generate_response(message)
        except RateLimitError as exc:
            raise HTTPException(status_code=429, detail=RATE_LIMIT_MESSAGE) from exc
        except Exception as e:
            self.logger.error("Error generating response from chat model: %s", e)
            raise HTTPException(status_code=500, detail=MODEL_FAILURE_MESSAGE) from e

        if not response:
            raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)

        if isinstance(response, str):
            response = LLMResponse(content=response)
        return response
