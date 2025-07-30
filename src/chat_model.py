import os
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain.chat_models import init_chat_model
from starlette.exceptions import HTTPException
from openai import RateLimitError
from .env import USE_LOCAL_MODEL, LOCAL_MODEL_NAME, LOCAL_LLM_BASE_URL, LOCAL_LLM_API_KEY
from .constants import MODEL_FAILURE_MESSAGE, RATE_LIMIT_MESSAGE, MODEL_NOT_DEFINED, DEFAULT_SYSTEM_PROMPT
from .schemas import LLMResponse
import requests


class ChatModel:
    retriever_tool = None
    system_prompt = None

    def _load_system_prompt(self) -> str:
        """
        Loads and processes the system prompt from the prompt.md file.
        
        Returns:
            str: The cleaned system prompt ready to be used with the model.
        """
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "prompt.md")
            with open(prompt_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return DEFAULT_SYSTEM_PROMPT
        except Exception as e:
            return DEFAULT_SYSTEM_PROMPT

    def _get_knowledge_base_files(self, knowledge_base_path: str) -> list[str]:
        """
        Retrieves a list of file paths for all Markdown (.md) files in the specified knowledge base directory.

        Args:
            knowledge_base_path (str): The path to the directory containing the knowledge base files.

        Returns:
            list[str]: A list of file paths for all Markdown files in the specified directory.
        """
        markdown_paths = []
        # Build absolute path to knowledge base
        abs_kb_path = os.path.join(os.path.dirname(__file__), knowledge_base_path)
        
        for filename in os.listdir(abs_kb_path):
            if filename.endswith(".md"):
                markdown_paths.append(os.path.join(abs_kb_path, filename))
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
            document_list (list): A list of documents to be split. Each document should be a string or an object compatible with the text splitter.

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
        if USE_LOCAL_MODEL:
            embedding = HuggingFaceEmbeddings(
                model_name="paraphrase-multilingual-MiniLM-L12-v2",  # Bueno para español
                model_kwargs={'device': 'cuda'},  # Cambiar a 'cuda' si tienes GPU
                encode_kwargs={'normalize_embeddings': True}
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

    def __init__(self):
        "Instanciate the chat model with the appropriate parameters"
        kb_path = "knowledge_base"
        model_temperature = 0.3
        
        # Load the system prompt
        self.system_prompt = self._load_system_prompt()
        
        if USE_LOCAL_MODEL:
            # Usar LM Studio local
            self.response_model = init_chat_model(
                f"openai:{LOCAL_MODEL_NAME}",  # Nombre del modelo en LM Studio
                temperature=model_temperature,
                api_base=LOCAL_LLM_BASE_URL,
                api_key=LOCAL_LLM_API_KEY
            )
        else:
            # Usar OpenAI
            self.response_model = init_chat_model(
                "openai:gpt-4.1", temperature=model_temperature
            )

        # 1. cargar el contenido
        markdown_files = self._get_knowledge_base_files(kb_path)
        document_list = self._get_documents(markdown_files)

        # 2. separar el texto y codificar con el embedding (tiktoken_encoder)
        docs_splits = self._get_splitted_docs(document_list)
        try:
            vectorstore = self._create_memory_db(docs_splits)
            self.retriever_tool = self._create_retriever(
                vectorstore,
                "retrieve_ParceroGo",
                "Buscador de información parceroGo",
            )
        except RateLimitError as e:
            print(f"Error al crear la base de datos vectorstore: {e}")
        

    def _generate_response(self, message: str):
        # Obtener contexto relevante de la base de conocimiento
        docs = self.retriever_tool.invoke({"query": message})
        
        # Construir el prompt completo
        if docs:
            context_text = "\n".join([doc.page_content if hasattr(doc, 'page_content') else str(doc) for doc in docs])
        else:
            context_text = "No hay información específica disponible."

        # Reemplazar placeholders directamente en el prompt completo
        full_prompt = self.system_prompt.format(
            context_section=context_text,
            user_message=message
        )
        
        # Usar el modelo local
        if USE_LOCAL_MODEL:
            return self._call_local_model(full_prompt)
        else:
            return self.response_model.invoke(full_prompt)

    def _call_local_model(self, prompt: str):
        """Llamar directamente al API de LM Studio"""
        url = f"{LOCAL_LLM_BASE_URL}/chat/completions"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer lm-studio"
        }
        
        data = {
            "model": LOCAL_MODEL_NAME,  # Nombre de tu modelo local
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 500,
            "stream": False
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=f"Error connecting to local model: {str(e)}")

    def ask_to_model(self, message: str, conversation_id: str):
        if not self.retriever_tool or not self.response_model:
            print(f"Error al iniciar componentes del modelo.")
            raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
    
        try:
            response = self._generate_response(message)
        except RateLimitError:
            raise HTTPException(status_code=429, detail=RATE_LIMIT_MESSAGE)
        except Exception as e:
            raise HTTPException(status_code=500, detail=MODEL_FAILURE_MESSAGE)
    
        if not response:
            raise HTTPException(status_code=500, detail=MODEL_NOT_DEFINED)
    
        if isinstance(response, str):
            response = LLMResponse(content=response)
        return response
